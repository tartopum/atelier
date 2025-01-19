import os
from contextlib import contextmanager
import datetime
import json
import sqlite3
import subprocess as sp
from threading import Lock

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Float, Integer, String, JSON
from sqlalchemy.orm import DeclarativeBase

from . import config


_HERE = os.path.dirname(__file__)
_ALERT_TABLE = "alerts"

TANK_DATE_COL = 0
TANK_VOL_IN_COL = 1
TANK_VOL_OUT_TANK_COL = 2
TANK_VOL_OUT_CITY_COL = 3
TANK_FULL_COL = 4
TANK_EMPTY_COL = 5
TANK_PUMP_IN_COL = 6
TANK_PUMP_OUT_COL = 7
TANK_CITY_COL = 8

lock = Lock()


def db_path():
    return os.path.join(_HERE, "..", config.get("server", "db_path"))


def backup():
    bk_path = os.path.join(_HERE, "..", "backup_db.sqlite3")
    sp.call(["sqlite3", db_path(), f".backup {bk_path}"])
    for path in config.get("server", "db_backup_paths"):
        sp.call(["cp", bk_path, path])


@contextmanager
def _connect(commit=True):
    with lock:
        try:
            conn = sqlite3.connect(db_path(), detect_types=sqlite3.PARSE_DECLTYPES)
            yield conn
            if commit:
                conn.commit()
        finally:
            conn.close()


def create_tables():
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS alerts(
             timestamp TIMESTAMP,
             name TEXT,
             message TEXT
        )
        """
        )
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tank_stats(
             timestamp TIMESTAMP,
             volume_in INTEGER,
             volume_out_tank INTEGER,
             volume_out_urban_network INTEGER,
             is_tank_full BOOLEAN,
             is_tank_empty BOOLEAN,
             pump_in_running_duration INTEGER,
             pump_out_running_duration INTEGER,
             urban_network_running_duration INTEGER
        )
        """
        )


def add_alert(name, msg):
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts VALUES(?, ?, ?)", (datetime.datetime.now(), name, msg)
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
                (time_limit,),
            )
        return cursor.fetchall()


def delete_old_alerts():
    with _connect() as conn:
        cursor = conn.cursor()
        delta = datetime.timedelta(-config.get("server", "max_alert_day_old"))
        time_limit = datetime.datetime.now() + delta
        cursor.execute("DELETE FROM alerts WHERE timestamp < ?", (time_limit,))


def store_tank_stats(data):
    data = {"timestamp": datetime.datetime.now(), **data}
    cols = ",".join(data)
    vals = ",".join([f":{k}" for k in data])
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO tank_stats ({cols}) VALUES({vals})", data)


def read_tank_stats(start, end=None):
    if end is None:
        end = datetime.datetime.now()
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tank_stats WHERE timestamp > :start AND timestamp <= :end ORDER BY timestamp",
            dict(start=start, end=end),
        )
        return cursor.fetchall()


def read_tank_volume_in_out():
    volume_in = 0
    volume_out = 0
    start_empty = True
    with _connect() as conn:
        cursor = conn.cursor()
        for row in cursor.execute("SELECT * FROM tank_stats ORDER BY timestamp DESC"):
            if row[TANK_EMPTY_COL]:
                start_empty = True
                break
            if row[TANK_FULL_COL]:
                start_empty = False
                break
            volume_in += row[TANK_VOL_IN_COL]
            volume_out += row[TANK_VOL_OUT_TANK_COL]
    return start_empty, volume_in, volume_out


def read_tank_volume_history(start, end=None):
    if end is None:
        end = datetime.datetime.now()
    dates = []
    rel_volumes = []
    volume_delta_before = 0
    volume_delta_after = 0
    is_ref_before = False
    ref_empty = None
    with _connect() as conn:
        cursor = conn.cursor()
        q = "SELECT * FROM tank_stats WHERE timestamp <= :end ORDER BY timestamp DESC"
        for row in cursor.execute(q, (end,)):
            if ref_empty is not None and row[TANK_DATE_COL] < start:
                break
            is_ref_before = row[TANK_DATE_COL] < start
            if row[TANK_EMPTY_COL]:
                ref_empty = True
                volume_delta_after = 0
            if row[TANK_FULL_COL]:
                ref_empty = False
                volume_delta_after = 0

            if row[TANK_DATE_COL] >= start:
                dates.append(row[TANK_DATE_COL])
                rel_volumes.append(row[TANK_VOL_IN_COL] - row[TANK_VOL_OUT_TANK_COL])
                volume_delta_after += row[TANK_VOL_IN_COL] - row[TANK_VOL_OUT_TANK_COL]
            else:
                volume_delta_before += row[TANK_VOL_IN_COL] - row[TANK_VOL_OUT_TANK_COL]

    # If the reference is after the start, we have:
    # start = ref - delta_after
    # Otherwise, we have:
    # ref + delta_before = start
    delta_volume = volume_delta_before if is_ref_before else -volume_delta_after
    return ref_empty, dates[::-1], rel_volumes[::-1], delta_volume


def read_tank_power_consumption(start, end=None):
    if end is None:
        end = datetime.datetime.now()
    dates = []
    pump_in = []
    pump_out = []
    city = []
    with _connect() as conn:
        cursor = conn.cursor()
        q = "SELECT * FROM tank_stats WHERE timestamp > :start AND timestamp <= :end ORDER BY timestamp"
        for row in cursor.execute(q, (start, end)):
            dates.append(row[TANK_DATE_COL])
            pump_in.append(row[TANK_PUMP_IN_COL])
            pump_out.append(row[TANK_PUMP_OUT_COL])
            city.append(row[TANK_CITY_COL])
    return dates, pump_in, pump_out, city


class Base(DeclarativeBase):
  pass


db = SQLAlchemy(model_class=Base)


class Orchard(db.Model):
    __tablename__ = "orchard"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    # Un rang est un alignement d'arbres espacés de façon équidistante
    # Si au sein d'un même rang les arbres changent d'espacement, il faudra créer deux rangs d'affilée
    # Voir web.routes.orchard.import_points_route() pour la structure
    rows = Column(JSON, default=list)
