from flask import Blueprint, redirect, request
import requests

from . import arduino
from .config import schema

schema.add_section("tank")
schema.add_int("tank", "min_flow_in", min=0, max=100)  # L/min
schema.add_int("tank", "time_to_fill_up", min=1, max=(60 * 24))  # min
schema.add_int("tank", "tank_radius", min=0, max=500)  # cm
schema.add_int("tank", "", min=0, max=500)  # cm

state = dict() # TODO
arduino_endpoint = "tank"
blueprint = Blueprint("tank", __name__, template_folder="templates")
