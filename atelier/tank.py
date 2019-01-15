from collections import defaultdict
import datetime as dt
import math

from flask import Blueprint, jsonify, redirect, request
import requests

from . import arduino, db
from .config import config


state = dict()
arduino_endpoint = "tank"
blueprint = Blueprint("tank", __name__, template_folder="templates")


def water_level():
    start_empty, volume_in, volume_out = db.read_tank_volume_in_out()
    total_volume = (
        config["tank"]["height_between_sensors"]
        * math.pi * config["tank"]["radius"] ** 2
        / 1000
    )
    water_volume = 0 if start_empty else total_volume
    water_volume = water_volume + volume_in - volume_out
    ratio = water_volume / total_volume
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
            "pump_in_start_duration": config["tank"]["pump_in_start_duration"] * 1000,
            "max_pump_out_running_time": config["tank"]["max_pump_out_running_time"] * 1000,
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


def _bin_time_series(dates, data, binsize):
    binned_data = defaultdict(list)
    for date, val in zip(dates, data):
        bin_index = abs(date - dates[0]) // binsize
        binned_data[dates[0] + bin_index * binsize + binsize / 2].append(val)
    binned_dates = sorted(binned_data)
    return binned_dates, [binned_data[d] for d in binned_dates]


def _consumption_data(timestep, duration):
    try:
        end = dt.datetime.strptime(request.args.get("end", ""), "%Y-%m-%d")
    except (ValueError, KeyError) as e:
        end = dt.datetime.now()

    start = end - duration
    stats = db.read_tank_stats(start, end)
    dates = [row[0] for row in stats]
    y_well = [row[1] for row in stats]
    y_tank = [row[2] for row in stats]
    y_city = [row[3] for row in stats]
    dates_well, y_well = _bin_time_series(dates, y_well, timestep)
    dates_tank, y_tank = _bin_time_series(dates, y_tank, timestep)
    dates_city, y_city = _bin_time_series(dates, y_city, timestep)

    date_format = "%Y-%m-%d %H"
    if timestep >= dt.timedelta(days=1):
        date_format = "%Y-%m-%d"
    if timestep >= dt.timedelta(days=31):
        date_format = "%Y-%m"
    if timestep >= dt.timedelta(days=365):
        date_format = "%Y"

    return jsonify({
        "x_tank": [d.strftime(date_format) for d in dates_tank],
        "x_city": [d.strftime(date_format) for d in dates_city],
        "x_well": [d.strftime(date_format) for d in dates_well],
        "y_tank": [sum(period) for period in y_tank],
        "y_city": [sum(period) for period in y_city],
        "y_well": [sum(period) for period in y_well],
    })



@blueprint.route("/stats/consommation")
def consumption_data():
    try:
        days = int(request.args.get("days"))
        assert days > 0, "The number of days must be positive"
        timestep = int(request.args.get("timestep", 0))
        assert timestep >= 0, "The timestep must be greater than or equal to 0"
    except (TypeError, ValueError, AssertionError) as e:
        return str(e), 400

    if not timestep:
        max_points = 100
        step_sizes = [30, 60, 180, 360, 720, 1440, 4320, 10080, 20160, 43200]  # minutes
        n_minutes = days * 24 * 60
        for timestep in step_sizes:
            if n_minutes / timestep <= max_points:
                break

    return _consumption_data(
        dt.timedelta(minutes=timestep),
        dt.timedelta(days)
    )
