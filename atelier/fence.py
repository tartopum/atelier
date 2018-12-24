from flask import Blueprint
import requests

from .shared import post_arduino


state = dict(on=False)
arduino_endpoint = "fence"

blueprint = Blueprint("fence", __name__, template_folder="templates")

@blueprint.route("/activate/<int:on>")
def activate(on):
    post_arduino(arduino_endpoint, {"on": on})
