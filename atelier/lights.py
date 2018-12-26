from flask import Blueprint
import requests

from .helpers import post_arduino, register_arduino_route


state = {"0": False, "1": False, "2": False}
arduino_endpoint = "lights"
blueprint = Blueprint("lights", __name__, template_folder="templates")


def activate(n, on):
    return post_arduino(arduino_endpoint, {n: int(on)})


register_arduino_route(activate, blueprint, "/<int:n>/<int:on>")


def activate_all(on):
    return post_arduino(arduino_endpoint, {i: int(on) for i in range(3)})
