from flask import Blueprint, redirect, request
import requests

from . import arduino
from .config import config, schema
from .helpers import auth, redirect_prev


arduino_endpoint = "workshop"
blueprint = Blueprint("workshop", __name__, template_folder="templates")


def config_arduino():
    arduino.post(
        arduino_endpoint,
        {
            "inactivity_delay": config["lights"]["inactivity_delay"] * 60 * 1000,
            "power_reminder_delay": config["power"]["delay_before_reminder"] * 3600 * 1000,
        }
    )


def power_supply(on):
    return arduino.post(arduino_endpoint, {"power_supply": int(on)})


def power_manual_mode(on):
    return arduino.post(arduino_endpoint, {"power_manual_mode": int(on)})


arduino.register_post_route(power_supply, blueprint, "/alimentation/<int:on>")
arduino.register_post_route(power_manual_mode, blueprint, "/alimentation/manuel/<int:on>")
