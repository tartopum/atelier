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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tank_stats(
             timestamp TIMESTAMP,
             volume_in INTEGER,
             volume_out_tank INTEGER,
             volume_out_urban_network INTEGER,
             urban_network BOOLEAN,
             flow_in REAL,
             flow_out REAL,
             is_tank_full BOOLEAN,
             is_tank_empty BOOLEAN
        )
        """)


def add_alert(name, msg):
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts VALUES(?, ?, ?)",
            (datetime.datetime.now(), name, msg)
        )


def list_alerts(n_days_ago=None):
    with _connect() as conn:
        cursor = conn.cursor()
        if n_days_ago is None:
            cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC")
        else:
            delta = datetime.timedelta(-n_days_ago)
            time_limit = datetime.datetime.now() + delta
            cursor.execute(
                "SELECT * FROM alerts WHERE timestamp > ? ORDER BY timestamp DESC",
                (time_limit,)
            )
        return cursor.fetchall()


def delete_old_alerts():
    with _connect() as conn:
        cursor = conn.cursor()
        delta = datetime.timedelta(-config["server"]["max_alert_day_old"])
        time_limit = datetime.datetime.now() + delta
        cursor.execute("DELETE FROM alerts WHERE timestamp < ?", (time_limit,))


def store_tank_stats(data):
    data = {"now": datetime.datetime.now(), **data}
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tank_stats VALUES("
            ":now, :volume_in, :volume_out_tank, :volume_out_urban_network, "
            ":urban_network, :flow_in, :flow_out, :is_tank_full, :is_tank_empty"
            ")",
            data
        )


def read_tank_stats(start, end=None):
    if end is None:
        end = datetime.datetime.now()
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tank_stats WHERE timestamp > :start AND timestamp < :end ORDER BY timestamp",
            dict(start=start, end=end)
        )
        return cursor.fetchall()


def _is_tank_empty(row):
    return row[7]


def _is_tank_full(row):
    return row[6]


def read_tank_volume_in_out():
    volume_in = 0
    volume_out = 0
    start_empty = True
    with _connect() as conn:
        cursor = conn.cursor()
        for row in cursor.execute("SELECT * FROM tank_stats ORDER BY timestamp DESC"):
            if _is_tank_empty(row):
                start_empty = True
                break
            if _is_tank_full(row):
                start_empty = False
                break
            volume_in += row[1]
            volume_out += row[2]
    return start_empty, volume_in, volume_out
