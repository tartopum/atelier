from flask import Blueprint, redirect, request
import requests

from .helpers import post_arduino


state = dict(power_supply=True, inactivity_delay=(1000 * 60 * 30))
arduino_endpoint = "workshop"

blueprint = Blueprint("workshop", __name__, template_folder="templates")

@blueprint.route("/power_supply/<int:on>")
def power_supply(on):
    return post_arduino(arduino_endpoint, {"power_supply": on})
