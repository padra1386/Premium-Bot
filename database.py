import psycopg2
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT


def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
    )
    return conn


# In database.py
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS invoice (
            invoice_id VARCHAR(50) PRIMARY KEY,
            id TEXT,
            username VARCHAR(255),
            sub VARCHAR(255),
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT NULL,
            is_paid VARCHAR(50) DEFAULT 'false',
            price VARCHAR(255)
        )"""
    )
    conn.commit()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id TEXT,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            status VARCHAR(255) DEFAULT 'active',
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS services (
            service_name VARCHAR(255),
            price FLOAT(24), 
            fee FLOAT(24),
            profit FLOAT(24)
        )"""
    )
    conn.commit()
    cur.close()
    conn.close()


create_tables()
