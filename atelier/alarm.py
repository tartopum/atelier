from flask import Blueprint
import requests

from .helpers import post_arduino, register_arduino_route


state = dict(listening=False, movement=False)
arduino_endpoint = "alarm"
blueprint = Blueprint("alarm", __name__, template_folder="templates")


def listen(on):
    return post_arduino(arduino_endpoint, {"listen": int(on)})


register_arduino_route(listen, blueprint, "/listen/<int:on>")
