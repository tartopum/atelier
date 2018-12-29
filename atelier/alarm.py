from flask import Blueprint
import requests

from . import arduino, forms
from .config import config

state = dict(listening=False, movement=False)
arduino_endpoint = "alarm"
blueprint = Blueprint("alarm", __name__, template_folder="templates")


def config_arduino():
    arduino.post(
        arduino_endpoint,
        {"ms_before_alert": config["alarm"]["delay"] * 1000}
    )


def listen(on):
    arduino.post(arduino_endpoint, {"listen": int(on)})


arduino.register_post_route(listen, blueprint, "/listen/<int:on>")
