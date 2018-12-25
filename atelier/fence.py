from flask import Blueprint, redirect, request
import requests

from .helpers import post_arduino


state = dict(on=False)
arduino_endpoint = "fence"

blueprint = Blueprint("fence", __name__, template_folder="templates")

@blueprint.route("/activate/<int:on>")
def activate(on):
    return post_arduino(arduino_endpoint, {"state": on})
