from collections import defaultdict
import datetime as dt
import math

from . import arduino, db
from .config import config


def _volume(height):
    return height * math.pi * config["tank"]["radius"] ** 2 / 1000


def volume_below_low_sensor():
    return _volume(config["tank"]["low_sensor_height"])


def volume_between_sensors():
    return _volume(config["tank"]["height_between_sensors"])


def water_level():
    start_empty, volume_in, volume_out = db.read_tank_volume_in_out()
    water_volume = 0 if start_empty else volume_between_sensors()
    water_volume = water_volume + volume_in - volume_out
    ratio = water_volume / volume_between_sensors()
    return min(max(0, ratio), 1)


def read_and_store_stats():
    db.store_tank_stats(arduino.http_get("tank_stats"))


def read_volume_history(start, end=None):
    return db.read_tank_volume_history(start, end)


def read_power_consumption(start, end=None):
    return db.read_tank_power_consumption(start, end)


def bin_time_series(dates, data, binsize, start_date=None):
    if not dates:
        return [], []
    if start_date is None:
        start_date = dates[0]
    binned_data = defaultdict(list)
    for date, val in zip(dates, data):
        bin_index = abs(date - start_date) // binsize
        binned_data[start_date + bin_index * binsize].append(val)
    binned_dates = sorted(binned_data)
    return binned_dates, [binned_data[d] for d in binned_dates]


def date_format_from_step(timestep):
    if timestep > dt.timedelta(days=365):
        return "%Y"
    if timestep > dt.timedelta(days=31):
        return "%Y-%m"
    if timestep > dt.timedelta(days=1):
        return "%Y-%m-%d"
    if timestep > dt.timedelta(hours=1):
        return "%Y-%m-%d %H"
    return "%Y-%m-%d %H:%M"


def get_stats_end_date(timestep, end=None):
    if end is None:
        end = dt.datetime.now()
    if timestep < dt.timedelta(days=1):
        return dt.datetime(end.year, end.month, end.day, end.hour)
    if timestep < dt.timedelta(days=30):
        return dt.datetime(end.year, end.month, end.day)
    if timestep >= dt.timedelta(days=30):
        return dt.datetime(end.year, end.month, 1)
    return end


def get_stats_start_date(end, duration, timestep):
    start = end - duration
    if timestep < dt.timedelta(days=1):
        return dt.datetime(start.year, start.month, start.day, start.hour)
    if timestep < dt.timedelta(days=30):
        return dt.datetime(start.year, start.month, start.day)
    return dt.datetime(start.year, start.month, 1)


def get_consumption_data(timestep, duration, end):
    end = get_stats_end_date(timestep, end=end)
    start = get_stats_start_date(end, duration, timestep)
    stats = db.read_tank_stats(start, end)
    dates = [row[0] for row in stats]
    y_well = [row[1] for row in stats]
    y_tank = [row[2] for row in stats]
    y_city = [row[3] for row in stats]
    dates_well, y_well = bin_time_series(dates, y_well, timestep, start_date=start)
    dates_tank, y_tank = bin_time_series(dates, y_tank, timestep, start_date=start)
    dates_city, y_city = bin_time_series(dates, y_city, timestep, start_date=start)
    date_format = date_format_from_step(timestep)

    return {
        "x_tank": [d.strftime(date_format) for d in dates_tank],
        "x_city": [d.strftime(date_format) for d in dates_city],
        "x_well": [d.strftime(date_format) for d in dates_well],
        "y_tank": [sum(period) for period in y_tank],
        "y_city": [sum(period) for period in y_city],
        "y_well": [sum(period) for period in y_well],
    }
