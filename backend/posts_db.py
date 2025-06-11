import psycopg2
import os

def get_posts_db_conn():
    return psycopg2.connect(
        host=os.getenv("POSTS_DB_HOST", "posts_db"),
        dbname=os.getenv("POSTS_DB", "postsdb"),
        user=os.getenv("POSTS_DB_USER", "postsuser"),
        password=os.getenv("POSTS_DB_PASSWORD", "postspass")
    )
