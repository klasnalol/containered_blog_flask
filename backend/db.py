import psycopg2
import os

def get_user_db_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        dbname=os.getenv("POSTGRES_DB", "mydb"),
        user=os.getenv("POSTGRES_USER", "myuser"),
        password=os.getenv("POSTGRES_PASSWORD", "mypassword")
    )
