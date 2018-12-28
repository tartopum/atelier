from flask import Blueprint
import requests

from . import arduino
from .config import schema

schema.add_section("alarm")
schema.add_int("alarm", "delay", min=0, max=60)  # s

state = dict(listening=False, movement=False)
arduino_endpoint = "alarm"
blueprint = Blueprint("alarm", __name__, template_folder="templates")


def listen(on):
    arduino.post(arduino_endpoint, {"listen": int(on)})


arduino.register_post_route(listen, blueprint, "/listen/<int:on>")
