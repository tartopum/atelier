from flask import Flask, render_template, request, jsonify
import requests

from . import alarm, lights, fence
from .helpers import build_arduino_url, arduino_req_route

app = Flask(__name__)
app.register_blueprint(alarm.blueprint, url_prefix="/alarm")
app.register_blueprint(fence.blueprint, url_prefix="/fence")
app.register_blueprint(lights.blueprint, url_prefix="/lights")


def update_state(x):
    data = requests.get(
        build_arduino_url(x.arduino_endpoint),
        timeout=app.config["TIMEOUT"]
    ).json()
    for k, v in data.items():
        x.state[k] = v
    return x.state


@app.route("/")
@arduino_req_route
def home():
    # TODO: display alerts
    return render_template("fence.html", state=update_state(fence))


@app.route("/cloture")
@arduino_req_route
def fence_route():
    return render_template("fence.html", state=update_state(fence))


@app.route("/atelier")
@arduino_req_route
def workshop_route():
    return render_template(
        "workshop.html",
        alarm=update_state(alarm),
        lights=update_state(lights)
    )


@app.route("/eau")
@arduino_req_route
def tank_route():
    return render_template("tank.html")
