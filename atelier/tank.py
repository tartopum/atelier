from flask import Blueprint, redirect, request
import requests

from . import arduino
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
