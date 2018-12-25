from flask import Flask, render_template, request, jsonify
import requests

from . import alarm, lights, fence, workshop
from .helpers import build_arduino_url, arduino_get

app = Flask(__name__)
app.register_blueprint(alarm.blueprint, url_prefix="/alarm")
app.register_blueprint(fence.blueprint, url_prefix="/fence")
app.register_blueprint(lights.blueprint, url_prefix="/lights")
app.register_blueprint(workshop.blueprint, url_prefix="/workshop")


def update_state(x):
    data = requests.get(
        build_arduino_url(x.arduino_endpoint),
        timeout=app.config["TIMEOUT"]
    ).json()
    for k, v in data.items():
        x.state[k] = v
    return x.state


@app.route("/")
@arduino_get
def home():
    # TODO: display alerts
    return render_template("fence.html", state=update_state(fence))


@app.route("/cloture")
@arduino_get
def fence_route():
    return render_template("fence.html", page="fence", state=update_state(fence))


@app.route("/atelier")
@arduino_get
def workshop_route():
    return render_template(
        "workshop.html",
        page="workshop",
        alarm=update_state(alarm),
        lights=update_state(lights),
        workshop=update_state(workshop),
    )


@app.route("/eau")
@arduino_get
def tank_route():
    return render_template("tank.html", page="tank")
