from contextlib import contextmanager
import datetime
import os
import sqlite3
from threading import Lock

from .config import config


_HERE = os.path.dirname(__file__)
_PATH = os.path.join(_HERE, "..", config["server"]["db_path"])
_ALERT_TABLE = "alerts"

lock = Lock()

@contextmanager
def _connect(commit=True):
    with lock:
        try:
            conn = sqlite3.connect(_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
            yield conn
            if commit:
                conn.commit()
        finally:
            conn.close()


def create_tables():
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts(
             timestamp TIMESTAMP,
             name TEXT,
             message TEXT
        )
        """)


def add_alert(name, msg):
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts VALUES(?, ?, ?)",
            (datetime.datetime.now(), name, msg)
        )


def list_alerts():
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts")
        return cursor.fetchall()
