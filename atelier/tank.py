from flask import Blueprint, redirect, request
import requests

from . import arduino, db
from .config import config


state = dict() # TODO
arduino_endpoint = "tank"
blueprint = Blueprint("tank", __name__, template_folder="templates")


def water_level():
    return 0.3 # TODO


def time_to_well_full():
    return 15 # TODO


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
        }
    )


@blueprint.route("/pump_in/<int:on>")
@arduino.post_route
def pump_in(on):
    return arduino.post(arduino_endpoint, {"pump_in": int(on)})


@blueprint.route("/pump_out/<int:on>")
@arduino.post_route
def pump_out(on):
    return arduino.post(arduino_endpoint, {"pump_out": int(on)})


@blueprint.route("/manual_mode/<int:on>")
@arduino.post_route
def manual_mode(on):
    return arduino.post(arduino_endpoint, {"manual_mode": int(on)})


@blueprint.route("/urban_network/<int:on>")
@arduino.post_route
def urban_network(on):
    return arduino.post(arduino_endpoint, {"urban_network": int(on)})


@blueprint.route("/filter_cleaning/<int:on>")
@arduino.post_route
def filter_cleaning(on):
    return arduino.post(arduino_endpoint, {"filter_cleaning": int(on)})


def read_and_store_stats():
    db.store_tank_stats(arduino.get("tank_stats"))
