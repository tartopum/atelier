from flask import Blueprint
import requests

from . import arduino
from .config import config


arduino_endpoint = "lights"
blueprint = Blueprint("lights", __name__, template_folder="templates")


def config_arduino():
    arduino.post(
        arduino_endpoint,
        {"press_delay": config["lights"]["press_delay"] * 1000}
    )


def activate(n, on):
    return arduino.post(arduino_endpoint, {n: int(on)})


arduino.register_post_route(activate, blueprint, "/<int:n>/<int:on>")


def activate_all(on):
    return arduino.post(arduino_endpoint, {i: int(on) for i in range(3)})
