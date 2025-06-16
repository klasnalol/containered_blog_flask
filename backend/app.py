from flask import Flask, request, jsonify, session, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os, time, psycopg2
import psutil
from prometheus_client import Gauge, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST

from db import get_user_db_conn
from posts_db import get_posts_db_conn
from models import Post, Comment

# ─── App & CORS ──────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# ─── Prometheus Metrics Setup ────────────────────────────────────────────────
registry = CollectorRegistry()
CPU_GAUGE = Gauge('app_cpu_percent', 'Process CPU utilization', registry=registry)
MEM_GAUGE = Gauge('app_memory_mb', 'Process memory usage in MB', registry=registry)

# ─── Uploads Setup ───────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── Bootstrapping ────────────────────────────────────────────────────────────
def wait_for_dbs():
    for _ in range(10):
        try:
            get_user_db_conn().close()
            get_posts_db_conn().close()
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError("Databases never became ready")

def init_all_dbs():
    # users table with is_admin
    conn = get_user_db_conn()
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        is_admin BOOLEAN NOT NULL DEFAULT FALSE
      );
    """)
    try:
        cur.execute("ALTER TABLE users ALTER COLUMN password TYPE VARCHAR(255);")
    except:
        pass
    conn.commit()
    cur.close()
    conn.close()

    Post.init_db()
    Comment.init_db()

# ─── Helpers ──────────────────────────────────────────────────────────────────
def is_admin():
    user = session.get("user")
    if not user:
        return False
    conn = get_user_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM users WHERE username=%s", (user,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return bool(row and row[0])

# ─── Auth Endpoints ───────────────────────────────────────────────────────────
@app.route("/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    u = data.get("username", "").strip()
    p = data.get("password", "").strip()
    if not u or not p:
        return jsonify({"message": "Both fields required"}), 400

    from werkzeug.security import generate_password_hash
    hashed = generate_password_hash(p)
    try:
        conn = get_user_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s,%s)",
            (u, hashed)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Registration successful"}), 200
    except psycopg2.errors.UniqueViolation:
        return jsonify({"message": "Username exists"}), 400
    except Exception as e:
        print("Reg error:", e)
        return jsonify({"message": "Registration failed"}), 500

@app.route("/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    u = data.get("username", "").strip()
    p = data.get("password", "").strip()
    if not u or not p:
        return jsonify({"message": "Both fields required"}), 400

    from werkzeug.security import check_password_hash
    conn = get_user_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username=%s", (u,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row and check_password_hash(row[0], p):
        session["user"] = u
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/me", methods=["GET"])
def api_me():
    user = session.get("user")
    if not user:
        return jsonify({"user": None, "is_admin": False}), 401
    conn = get_user_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM users WHERE username=%s", (user,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"user": user, "is_admin": bool(row and row[0])}), 200

@app.route("/logout", methods=["POST"])
def api_logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out"}), 200

# ─── Blog/Feed Endpoints ─────────────────────────────────────────────────────
@app.route("/feed", methods=["GET"])
def feed():
    posts = Post.get_all()
    out = []
    for p in posts:
        out.append({
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "image_url": p.image_path,
            "author": p.author,
            "created_at": p.created_at.isoformat(),
            "comments": [
                {
                    "author": c.author,
                    "content": c.content,
                    "created_at": c.created_at.isoformat()
                } for c in Comment.for_post(p.id)
            ]
        })
    return jsonify(out), 200

@app.route("/posts", methods=["POST"])
def create_post():
    if not is_admin():
        return jsonify({"message": "Forbidden"}), 403
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    img = request.files.get("image")
    img_path = ""
    if img:
        fname = secure_filename(img.filename)
        path = os.path.join(UPLOAD_FOLDER, fname)
        img.save(path)
        img_path = f"/uploads/{fname}"
    post = Post.create(title, content, img_path, session["user"])
    return jsonify({"message": "Created", "post_id": post.id}), 201

@app.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    if not is_admin():
        return jsonify({"message": "Forbidden"}), 403
    try:
        Post.delete(post_id)
        return jsonify({"message": "Post deleted"}), 200
    except Exception as e:
        print("Delete error:", e)
        return jsonify({"message": "Deletion failed"}), 500

@app.route("/posts/<int:post_id>/comments", methods=["POST"])
def add_comment(post_id):
    user = session.get("user")
    if not user:
        return jsonify({"message": "Login required"}), 401
    data = request.get_json() or {}
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"message": "Content required"}), 400
    Comment.create(post_id, user, content)
    return jsonify({"message": "Comment added"}), 201

@app.route("/uploads/<filename>")
def uploaded(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ─── Metrics Endpoint ───────────────────────────────────────────────────────
@app.route("/metrics")
def metrics():
    CPU_GAUGE.set(psutil.cpu_percent())
    MEM_GAUGE.set(psutil.Process().memory_info().rss / 1024 / 1024)
    data = generate_latest(registry)
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

# ─── Main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    wait_for_dbs()
    init_all_dbs()
    app.run(host="0.0.0.0", port=5000)
