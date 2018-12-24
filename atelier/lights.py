from flask import Blueprint
import requests

from .helpers import post_arduino


state = {"0": False, "1": False, "2": False}
arduino_endpoint = "lights"

blueprint = Blueprint("lights", __name__, template_folder="templates")

@blueprint.route("/<n>/<on>")
def activate(n, on):
    return post_arduino(arduino_endpoint, {n: on})
