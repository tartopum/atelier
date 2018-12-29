from flask import Blueprint, redirect, request
import requests

from . import arduino
from .config import config, schema


state = dict(power_supply=True, inactivity_delay=(1000 * 60 * 30))
arduino_endpoint = "workshop"
blueprint = Blueprint("workshop", __name__, template_folder="templates")


def config_arduino():
    arduino.post(
        arduino_endpoint,
        {"inactivity_delay": config["lights"]["inactivity_delay"] * 60 * 1000}
    )


def power_supply(on):
    return arduino.post(arduino_endpoint, {"power_supply": int(on)})


arduino.register_post_route(power_supply, blueprint, "/power_supply/<int:on>")
