from flask import Blueprint
import requests

from .shared import post_arduino


state = dict(listening=False, breach=False)
arduino_endpoint = "alarm"

blueprint = Blueprint("alarm", __name__, template_folder="templates")

@blueprint.route("/listen/<int:on>")
def listen(on):
    post_arduino(arduino_endpoint, dict(listen=on))
