from flask import Blueprint, redirect, request
import requests

from . import arduino
from .config import config, schema
from .helpers import auth, redirect_prev


turn_off_power = True
state = dict(power_supply=True, inactivity_delay=(1000 * 60 * 30))
arduino_endpoint = "workshop"
blueprint = Blueprint("workshop", __name__, template_folder="templates")


def config_arduino():
    arduino.post(
        arduino_endpoint,
        {"inactivity_delay": config["lights"]["inactivity_delay"] * 60 * 1000}
    )


def power_supply(on):
    return arduino.post(arduino_endpoint, {"power_supply": int(on)})


@blueprint.route("/turn_off_power/<int:turn_off>")
@auth.login_required
def turn_off_power_route(turn_off):
    global turn_off_power
    turn_off_power = turn_off
    return redirect_prev()


arduino.register_post_route(power_supply, blueprint, "/power_supply/<int:on>")
