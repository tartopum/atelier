from flask import Blueprint, redirect, request
import requests

from . import arduino
from .helpers import make_message_getter


arduino_endpoint = "fence"
blueprint = Blueprint("fence", __name__, template_folder="templates")


def command(on):
    return arduino.post(arduino_endpoint, {"state": int(on)})


def activate(on):
    return arduino.post(arduino_endpoint, {"activated": int(on)})


arduino.register_post_route(activate, blueprint, "/activer/<int:on>")
arduino.register_post_route(command, blueprint, "/commander/<int:on>")


get_errors = make_message_getter([], base_url_name="fence_route")
get_warnings = make_message_getter(
    [
        ("state", 0, "La clôture est éteinte.")
    ],
    base_url_name="fence_route",
)
