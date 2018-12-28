from flask import Blueprint, redirect, request
import requests

from . import arduino


state = dict(on=False)
arduino_endpoint = "fence"
blueprint = Blueprint("fence", __name__, template_folder="templates")


def activate(on):
    return arduino.post(arduino_endpoint, {"state": int(on)})

arduino.register_post_route(activate, blueprint, "/activate/<int:on>")
