from flask import Blueprint, redirect, request
import requests

from .helpers import post_arduino, register_arduino_route


state = dict(power_supply=True, inactivity_delay=(1000 * 60 * 30))
arduino_endpoint = "workshop"
blueprint = Blueprint("workshop", __name__, template_folder="templates")


def power_supply(on):
    return post_arduino(arduino_endpoint, {"power_supply": int(on)})


register_arduino_route(power_supply, blueprint, "/power_supply/<int:on>")
