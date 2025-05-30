import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'cryptomedz.db')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Table for uploaded files
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                file_name TEXT NOT NULL,
                record_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        # Table for JSON patient records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                record TEXT NOT NULL,
                record_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

def insert_file_record(patient_id, file_name, record_hash):
    timestamp = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO file_uploads (patient_id, file_name, record_hash, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (patient_id, file_name, record_hash, timestamp))
        conn.commit()

def insert_patient_record(patient_id, record, record_hash):
    timestamp = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO patient_records (patient_id, record, record_hash, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (patient_id, record, record_hash, timestamp))
        conn.commit()
