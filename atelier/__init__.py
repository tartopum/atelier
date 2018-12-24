from flask import Flask, render_template, request, jsonify
import requests

from . import alarm, lights, fence
from .shared import build_arduino_url

app = Flask(__name__)
app.register_blueprint(alarm.blueprint, url_prefix="/alarm")
app.register_blueprint(fence.blueprint, url_prefix="/fence")
app.register_blueprint(lights.blueprint, url_prefix="/lights")


@app.route("/")
def home():
    try:
        return render_template(
            "index.html",
            alarm=read_state(alarm),
            lights=read_state(lights),
            fence=read_state(fence),
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        return render_template("arduino_404.html", url=e.request.url), 500


def read_state(x):
    data = requests.get(
        build_arduino_url(x.arduino_endpoint),
        timeout=app.config["TIMEOUT"]
    ).json()
    for k, v in data.items():
        x.state[k] = v
