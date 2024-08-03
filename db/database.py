import sqlite3
from config import SQLITE_DB_PATH


def get_db_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    return conn


def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create invoice table
    cur.execute(
        """CREATE TABLE IF NOT EXISTS invoice (
            invoice_id TEXT PRIMARY KEY,
            id TEXT,
            username TEXT,
            sub TEXT,
            created TEXT,
            status TEXT DEFAULT 'Reviewing',
            is_paid TEXT DEFAULT 'false',
            price TEXT,
            profit TEXT,
            fee TEXT
        )"""
    )
    conn.commit()

    # Create users table
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id TEXT,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            status TEXT DEFAULT 'active',
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()

    # Create services table
    cur.execute(
        """CREATE TABLE IF NOT EXISTS services (
            service_name TEXT,
            price REAL, 
            fee REAL,
            profit REAL
        )"""
    )
    conn.commit()

    cur.close()
    conn.close()


create_tables()
