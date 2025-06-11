Containerized Blog with Flask

This project is a simple blog platform split into separate frontend and backend containers. It uses two PostgreSQL databases: one for user accounts and another for blog posts and comments. Both services are orchestrated via Docker Compose.
Features

    User registration and login endpoints

    Admin users can create and delete posts

    Regular users can add comments

    Image uploads stored in a shared volume

    Frontend served through Flask templates with Nginx and Gunicorn

    REST-style API endpoints for posts and comments

Architecture

The service layout is defined in docker-compose.yml:
```
version: "3.8"
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_DB=mydb
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypassword
      - POSTS_DB_HOST=posts_db
      - POSTS_DB=postsdb
      - POSTS_DB_USER=postsuser
      - POSTS_DB_PASSWORD=postspass
      - UPLOAD_FOLDER=/app/uploads
    ports:
      - "5000:5000"
    volumes:
      - uploads:/app/uploads
    depends_on:
      db:
        condition: service_healthy
      posts_db:
        condition: service_healthy
```
Two PostgreSQL instances (db and posts_db) are provisioned with health checks and persistent volumes:
```
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypassword
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "myuser", "-d", "mydb"]
      interval: 2s
      timeout: 2s
      retries: 15

  posts_db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=postsdb
      - POSTGRES_USER=postsuser
      - POSTGRES_PASSWORD=postspass
    ports:
      - "5433:5432"
    volumes:
      - posts_pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postsuser", "-d", "postsdb"]
      interval: 2s
      timeout: 2s
      retries: 15
```
Backend

The backend Flask app initializes the databases and exposes REST endpoints. The initialization sets up user tables, post tables, and comment tables:
```
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os, time, psycopg2

from db import get_user_db_conn
from posts_db import get_posts_db_conn
from models import Post, Comment

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

Routes include /register, /login, /feed, /posts, and /posts/<id>/comments (see line numbers around 67–195)

.
Frontend

The frontend container runs a small Flask application rendered with Jinja templates. It exposes routes for the main feed, login, registration, and post upload pages:

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

This container uses Gunicorn behind Nginx as defined in frontend/dockerfile and frontend/nginx.conf.
Prerequisites

    Docker and Docker Compose

    No local Python environment is necessary; all dependencies are handled inside the containers.

Usage

    Build and start all services:

    docker compose up --build

    Open http://localhost to view the blog frontend.

    Use the “Register” page to create a new account, then log in to post content. Admin accounts can delete posts. Uploaded images are stored in the uploads volume.

    Stop the stack with docker compose down (add -v to remove volumes if desired).

Directory Structure

    backend/ – API implementation and models

    frontend/ – Jinja templates, static assets, and Nginx configuration

    docker-compose.yml – container orchestration

    README.md – project documentation
```
Environment Variables

Environment variables for the backend database connections are already set in docker-compose.yml. They can be customized if you need different credentials or database names.
Development Notes

The backend uses Flask’s session support to track logged-in users, and CORS is enabled for the frontend to access the API. Uploaded files are saved under /app/uploads inside the backend container.
