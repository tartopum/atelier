from base64 import b64encode
from collections import defaultdict
import json

from flask import Flask, render_template, request, jsonify
from jsonschema import ValidationError
import requests

from .config import config
from .helpers import auth, raise_alert
from . import arduino, db, forms, scheduler, alarm, lights, fence, tank, workshop

app = Flask(__name__)
app.register_blueprint(alarm.blueprint, url_prefix="/alarm")
app.register_blueprint(fence.blueprint, url_prefix="/fence")
app.register_blueprint(lights.blueprint, url_prefix="/lights")
app.register_blueprint(workshop.blueprint, url_prefix="/workshop")
app.register_blueprint(tank.blueprint, url_prefix="/tank")


def config_arduino():
    credentials = b64encode(
        bytes(":".join(config["server"]["credentials"]), "utf8")
    ).decode("utf8")
    config.validate()
    arduino.post(
        "config_api",
        {
            "ip": config["server"]["ip"],
            "port": config["server"]["port"],
            "auth_header": f"Authorization: Basic {credentials}",
        }
    )
    alarm.config_arduino()
    lights.config_arduino()
    tank.config_arduino()
    workshop.config_arduino()


@app.route("/")
@arduino.get_route
def home():
    return render_template(
        "home.html",
        fence=arduino.read_state(fence),
        alerts=db.list_alerts(n_days_ago=7)
    )


@app.route("/config", methods=["GET", "POST"])
@arduino.post_route
def config_route():
    config_forms = forms.ConfigForms(request.form)
    if request.method == "POST" and config_forms.validate():
        config_forms.populate_config()
        config_arduino()
        config.save()
        # TODO: update scheduler
        return
    return render_template(
        "config.html",
        forms=config_forms,
        form_errors=any(form.errors for form in config_forms.values())
    )


@app.route("/cloture")
@arduino.get_route
def fence_route():
    return render_template("fence.html", state=arduino.read_state(fence))


@app.route("/atelier")
@arduino.get_route
def workshop_route():
    return render_template(
        "workshop.html",
        alarm=arduino.read_state(alarm),
        lights=arduino.read_state(lights),
        workshop=arduino.read_state(workshop),
    )


@app.route("/eau")
@arduino.get_route
def tank_route():
    return render_template(
        "tank.html",
        state=arduino.read_state(tank),
        water_level=tank.water_level(),
        time_to_well_full=tank.time_to_well_full(),
    )


@app.route("/debug")
@arduino.get_route
def debug_route():
    states = {
        component.__name__.split(".")[1]: arduino.read_state(component)
        for component in [alarm, fence, lights, workshop, tank]
    }
    states["api"] = arduino.get("config_api")
    return render_template("debug.html", states=states)


@app.route("/alert", methods=["POST"])
@auth.login_required
def receive_alert():
    try:
        data = request.get_json()
        name = data["name"]
        msg = data["message"]
    except (json.decoder.JSONDecodeError, KeyError):
        pass
    else:
        raise_alert(name, msg)
    return ""
