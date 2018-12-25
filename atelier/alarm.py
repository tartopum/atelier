from flask import Blueprint
import requests

from .helpers import post_arduino


state = dict(listening=False, movement=False)
arduino_endpoint = "alarm"

blueprint = Blueprint("alarm", __name__, template_folder="templates")

@blueprint.route("/listen/<int:on>")
def listen(on):
    return post_arduino(arduino_endpoint, dict(listen=on))
