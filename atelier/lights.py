from flask import Blueprint
import requests

from .shared import post_arduino


state = {"0": False, "1": False, "2": False}
arduino_endpoint = "lights"

blueprint = Blueprint("lights", __name__, template_folder="templates")

@blueprint.route("/outside/<int:on>")
def outside(on):
    post_arduino(arduino_endpoint, {"0": on})


@blueprint.route("/inside1/<int:on>")
def inside1(on):
    post_arduino(arduino_endpoint, {"1": on})


@blueprint.route("/inside2/<int:on>")
def inside2(on):
    post_arduino(arduino_endpoint, {"2": on})
