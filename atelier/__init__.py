import json

from flask import Flask, render_template, request, jsonify
import requests

from .config import config, schema
from . import arduino, scheduler, alarm, lights, fence, tank, workshop

app = Flask(__name__)
app.register_blueprint(alarm.blueprint, url_prefix="/alarm")
app.register_blueprint(fence.blueprint, url_prefix="/fence")
app.register_blueprint(lights.blueprint, url_prefix="/lights")
app.register_blueprint(workshop.blueprint, url_prefix="/workshop")
app.register_blueprint(tank.blueprint, url_prefix="/tank")

schema.add_section("server")
schema.add_ip("server", "ip")
schema.add_port("server", "port")


@app.route("/")
@arduino.get_route
def home():
    # TODO: display alerts
    return render_template("fence.html", state=arduino.read_state(fence))


def config_route():
    if request.method == "POST":
        for k, v in request.form.items():
            section, param = k.split("__")
            #config[section][param] = 

        arduino.configure()
        config.save()
        return
    return render_template("config.html", config=config.editable)


arduino.register_post_route(config_route, app, "/config", methods=["GET", "POST"])


@app.route("/cloture")
@arduino.get_route
def fence_route():
    return render_template("fence.html", page="fence", state=arduino.read_state(fence))


@app.route("/atelier")
@arduino.get_route
def workshop_route():
    return render_template(
        "workshop.html",
        page="workshop",
        alarm=arduino.read_state(alarm),
        lights=arduino.read_state(lights),
        workshop=arduino.read_state(workshop),
    )


@app.route("/eau")
@arduino.get_route
def tank_route():
    return render_template("tank.html", page="tank")


@app.route("/alert", methods=["POST"])
def receive_alert():
    try:
        data = request.get_json()
        name = data["name"]
        msg = data["message"]
    except (json.decoder.JSONDecodeError, KeyError):
        pass
    print("alert", name, msg)  # TODO
    return ""
