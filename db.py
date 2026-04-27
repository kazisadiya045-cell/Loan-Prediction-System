import mysql.connector
from mysql.connector import Error

# ✏️ Change these to match your MySQL setup
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "yourpassword",   # <-- change this
    "database": "loan_prediction_db",
}

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"[DB] Connection error: {e}")
        # Troubleshooting:
        # 1. MySQL running?   → sudo service mysql start
        # 2. Wrong password?  → update DB_CONFIG above
        # 3. No database?     → mysql -u root -p < database/schema.sql
    return None

def save_prediction(data: dict):
    sql = """INSERT INTO predictions
        (age, income, loan_amount, credit_score, employment_years, existing_loans,
         marital_status, education, prediction, prediction_label, prob_approved, prob_rejected)
        VALUES (%(age)s, %(income)s, %(loan_amount)s, %(credit_score)s,
                %(employment_years)s, %(existing_loans)s, %(marital_status)s, %(education)s,
                %(prediction)s, %(prediction_label)s, %(prob_approved)s, %(prob_rejected)s)"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"[DB] Insert error: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def fetch_recent(limit=10):
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT %s", (limit,))
        return cursor.fetchall()
    except Error as e:
        print(f"[DB] Fetch error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()





