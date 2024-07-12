from db.database import get_db_connection


conn = get_db_connection()
cur = conn.cursor()
