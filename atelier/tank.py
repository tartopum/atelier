from flask import Blueprint, redirect, request
import requests

from . import arduino
from .config import config, schema

schema.add_int("tank", "min_flow_in", min=0, max=100)  # L/min
schema.add_int("tank", "time_to_fill_up", min=1, max=(60 * 24))  # min
schema.add_int("tank", "tank_radius", min=0, max=500)  # cm
schema.add_int("tank", "tank_height", min=0, max=500)  # cm

state = dict() # TODO
arduino_endpoint = "tank"
blueprint = Blueprint("tank", __name__, template_folder="templates")


def config_arduino():
    arduino.post(
        arduino_endpoint,
        {
            "time_to_fill_up": config["tank"]["time_to_fill_up"] * 60 * 1000,
            "min_flow_in": config["tank"]["min_flow_in"],
        }
    )
