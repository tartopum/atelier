from flask import Blueprint, redirect, request
import requests

from .helpers import post_arduino, register_arduino_route


state = dict(on=False)
arduino_endpoint = "fence"
blueprint = Blueprint("fence", __name__, template_folder="templates")


def activate(on):
    return post_arduino(arduino_endpoint, {"state": int(on)})

register_arduino_route(activate, blueprint, "/activate/<int:on>")
