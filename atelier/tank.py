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


def pump_in(on):
    return arduino.post(arduino_endpoint, {"pump_in": int(on)})


def pump_out(on):
    return arduino.post(arduino_endpoint, {"pump_out": int(on)})


def manual_mode(on):
    return arduino.post(arduino_endpoint, {"manual_mode": int(on)})


arduino.register_post_route(pump_in, blueprint, "/pump_in/<int:on>")
arduino.register_post_route(pump_out, blueprint, "/pump_out/<int:on>")
arduino.register_post_route(manual_mode, blueprint, "/manual_mode/<int:on>")
