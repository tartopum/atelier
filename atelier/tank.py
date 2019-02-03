from collections import defaultdict
import datetime as dt
import math

from flask import Blueprint, jsonify, redirect, request
import requests

from . import arduino, db
from .config import config
from .helpers import auth


arduino_endpoint = "tank"
blueprint = Blueprint("tank", __name__, template_folder="templates")


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


def config_arduino():
    arduino.post(
        arduino_endpoint,
        {
            "time_to_fill_up": config["tank"]["time_to_fill_up"] * 60 * 1000,
            "min_flow_in": config["tank"]["min_flow_in"],
            "flow_check_period": config["tank"]["flow_check_period"] * 1000,
            "volume_before_pump_out": config["tank"]["volume_before_pump_out"],
            "filter_cleaning_period": config["tank"]["filter_cleaning_period"] * 60 * 1000,
            "filter_cleaning_duration": config["tank"]["filter_cleaning_duration"] * 1000,
            "filter_cleaning_consecutive_delay": config["tank"]["filter_cleaning_consecutive_delay"] * 1000,
            "pump_in_start_duration": config["tank"]["pump_in_start_duration"] * 1000,
            "max_pump_out_running_time": config["tank"]["max_pump_out_running_time"] * 1000 * 60,
            "max_duration_without_flow_out": config["tank"]["max_duration_without_flow_out"] * 1000 * 60,
        }
    )


@blueprint.route("/pompe-puits/<int:on>")
@arduino.post_route
def pump_in(on):
    return arduino.post(arduino_endpoint, {"pump_in": int(on)})


@blueprint.route("/pompe-puits/activer")
@arduino.post_route
def activate_pump_in():
    return arduino.post(arduino_endpoint, {"pump_in_activated": 1})


@blueprint.route("/pompe-surpresseur/<int:on>")
@arduino.post_route
def pump_out(on):
    return arduino.post(arduino_endpoint, {"pump_out": int(on)})


@blueprint.route("/pompe-surpresseur/activer")
@arduino.post_route
def activate_pump_out():
    return arduino.post(arduino_endpoint, {"pump_out_activated": 1})


@blueprint.route("/mode-manuel/<int:on>")
@arduino.post_route
def manual_mode(on):
    return arduino.post(arduino_endpoint, {"manual_mode": int(on)})


@blueprint.route("/reseau-urbain/<int:on>")
@arduino.post_route
def urban_network(on):
    return arduino.post(arduino_endpoint, {"urban_network": int(on)})


@blueprint.route("/nettoyage-filtre/<int:on>")
@arduino.post_route
def filter_cleaning(on):
    return arduino.post(arduino_endpoint, {"filter_cleaning": int(on)})


def read_and_store_stats():
    db.store_tank_stats(arduino.get("tank_stats"))


def _bin_time_series(dates, data, binsize, start_date=None):
    if start_date is None:
        start_date = dates[0]
    binned_data = defaultdict(list)
    for date, val in zip(dates, data):
        bin_index = abs(date - start_date) // binsize
        binned_data[start_date + bin_index * binsize].append(val)
    binned_dates = sorted(binned_data)
    return binned_dates, [binned_data[d] for d in binned_dates]


def _date_format_from_step(timestep):
    if timestep > dt.timedelta(days=365):
        return "%Y"
    if timestep > dt.timedelta(days=31):
        return "%Y-%m"
    if timestep > dt.timedelta(days=1):
        return "%Y-%m-%d"
    if timestep > dt.timedelta(hours=1):
        return "%Y-%m-%d %H"
    return "%Y-%m-%d %H:%M"


def _end_date(timestep, end=None):
    if end is None:
        end = dt.datetime.now()
    if timestep < dt.timedelta(days=1):
        return dt.datetime(end.year, end.month, end.day, end.hour)
    if timestep < dt.timedelta(days=30):
        return dt.datetime(end.year, end.month, end.day)
    if timestep >= dt.timedelta(days=30):
        return dt.datetime(end.year, end.month, 1)
    return end


def _start_date(end, duration, timestep):
    start = end - duration
    if timestep <= dt.timedelta(hours=1):
        return dt.datetime(start.year, start.month, start.day, start.hour)
    if timestep <= dt.timedelta(days=1):
        return dt.datetime(start.year, start.month, start.day)
    if timestep <= dt.timedelta(days=30):
        return dt.datetime(start.year, start.month, 1)
    return start


def _consumption_data(timestep, duration):
    try:
        end = dt.datetime.strptime(request.args.get("end", ""), "%Y-%m-%d")
    except (ValueError, KeyError):
        end = dt.datetime.now()

    end = _end_date(timestep, end=end)
    start = _start_date(end, duration, timestep)
    stats = db.read_tank_stats(start, end)
    dates = [row[0] for row in stats]
    y_well = [row[1] for row in stats]
    y_tank = [row[2] for row in stats]
    y_city = [row[3] for row in stats]
    dates_well, y_well = _bin_time_series(dates, y_well, timestep, start_date=start)
    dates_tank, y_tank = _bin_time_series(dates, y_tank, timestep, start_date=start)
    dates_city, y_city = _bin_time_series(dates, y_city, timestep, start_date=start)
    date_format = _date_format_from_step(timestep)

    return jsonify({
        "x_tank": [d.strftime(date_format) for d in dates_tank],
        "x_city": [d.strftime(date_format) for d in dates_city],
        "x_well": [d.strftime(date_format) for d in dates_well],
        "y_tank": [sum(period) for period in y_tank],
        "y_city": [sum(period) for period in y_city],
        "y_well": [sum(period) for period in y_well],
    })


@blueprint.route("/stats/consommation-eau")
@auth.login_required
def water_consumption_data():
    try:
        days = int(request.args.get("days"))
        assert days > 0, "The number of days must be positive"
        timestep = int(request.args.get("timestep"))
        assert timestep > 0, "The timestep must be positive"
    except (TypeError, ValueError, AssertionError) as e:
        return str(e), 400

    return _consumption_data(
        dt.timedelta(minutes=timestep),
        dt.timedelta(days)
    )


@blueprint.route("/stats/niveau-cuve")
@auth.login_required
def water_level_history():
    timestep = dt.timedelta(hours=1)
    end = _end_date(timestep)
    start = _start_date(end, dt.timedelta(7), timestep)
    ref_empty, dates, rel_volumes, delta_volume = db.read_tank_volume_history(start, end=end)
    start_volume = (0 if ref_empty else volume_between_sensors()) + delta_volume
    dates, rel_volumes = _bin_time_series(dates, rel_volumes, timestep)
    # The deltas during h:... lead to the volume at (h+1), not at h
    dates = [d + timestep for d in dates]
    rel_volumes = [sum(bin_vol) for bin_vol in rel_volumes]
    for i, delta in enumerate(rel_volumes):
        if i == 0:
            rel_volumes[i] = start_volume + delta
        else:
            rel_volumes[i] = rel_volumes[i - 1] + delta
    return jsonify({
        "dates": [d.strftime("%Y-%m-%d %H") for d in dates],
        "volumes": rel_volumes,
    })


@blueprint.route("/stats/consommation-electrique")
@auth.login_required
def power_consumption_data():
    try:
        days = int(request.args.get("days"))
        assert days > 0, "The number of days must be positive"
        timestep = int(request.args.get("timestep"))
        assert timestep > 0, "The timestep must be positive"
    except (TypeError, ValueError, AssertionError) as e:
        return str(e), 400

    timestep = dt.timedelta(minutes=timestep)
    end = _end_date(timestep)
    start = _start_date(end, dt.timedelta(days), timestep)
    dates, pump_in, pump_out, city = db.read_tank_power_consumption(start, end=end)
    binned_dates, pump_in = _bin_time_series(dates, pump_in, timestep, start_date=start)
    _, pump_out = _bin_time_series(dates, pump_out, timestep, start_date=start)
    _, city = _bin_time_series(dates, city, timestep, start_date=start)
    date_format = _date_format_from_step(timestep)

    return jsonify({
        "dates": [d.strftime(date_format) for d in binned_dates],
        "pump_in": [sum(period) / 60 for period in pump_in],
        "pump_out": [sum(period) / 60 for period in pump_out],
        "city": [sum(period) / 60 for period in city],
    })
