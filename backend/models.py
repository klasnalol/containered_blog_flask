from posts_db import get_posts_db_conn

class Post:
    def __init__(self, id, title, content, image_path, author, created_at):
        self.id = id
        self.title = title
        self.content = content
        self.image_path = image_path
        self.author = author
        self.created_at = created_at

    @staticmethod
    def init_db():
        conn = get_posts_db_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                image_path TEXT,
                author VARCHAR(80) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def create(title, content, image_path, author):
        conn = get_posts_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO posts (title, content, image_path, author) VALUES (%s,%s,%s,%s) RETURNING id, created_at",
            (title, content, image_path, author)
        )
        id, created_at = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return Post(id, title, content, image_path, author, created_at)

    @staticmethod
    def get_all():
        conn = get_posts_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, title, content, image_path, author, created_at FROM posts ORDER BY created_at DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Post(*r) for r in rows]

    @staticmethod
    def delete(post_id):
        conn = get_posts_db_conn()
        cur = conn.cursor()
        # remove comments first
        cur.execute("DELETE FROM comments WHERE post_id = %s", (post_id,))
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()
        cur.close()
        conn.close()

class Comment:
    def __init__(self, id, post_id, author, content, created_at):
        self.id = id
        self.post_id = post_id
        self.author = author
        self.content = content
        self.created_at = created_at

    @staticmethod
    def init_db():
        conn = get_posts_db_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                post_id INTEGER REFERENCES posts(id),
                author VARCHAR(80) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def create(post_id, author, content):
        conn = get_posts_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO comments (post_id, author, content) VALUES (%s,%s,%s) RETURNING id, created_at",
            (post_id, author, content)
        )
        id, created_at = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return Comment(id, post_id, author, content, created_at)

    @staticmethod
    def for_post(post_id):
        conn = get_posts_db_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, post_id, author, content, created_at FROM comments WHERE post_id=%s ORDER BY created_at",
            (post_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Comment(*r) for r in rows]
