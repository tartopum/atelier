from flask import Blueprint, redirect, request
import requests

from . import arduino
from .config import config


state = dict() # TODO
arduino_endpoint = "tank"
blueprint = Blueprint("tank", __name__, template_folder="templates")


def config_arduino():
    arduino.post(
        arduino_endpoint,
        {
            "time_to_fill_up": config["tank"]["time_to_fill_up"] * 60 * 1000,
            "min_flow_in": config["tank"]["min_flow_in"],
        }
    )


def pump_in(on):
    return arduino.post(arduino_endpoint, {"pump_in": int(on)})


def pump_out(on):
    return arduino.post(arduino_endpoint, {"pump_out": int(on)})


arduino.register_post_route(pump_in, blueprint, "/pump_in/<int:on>")
arduino.register_post_route(pump_out, blueprint, "/pump_out/<int:on>")
