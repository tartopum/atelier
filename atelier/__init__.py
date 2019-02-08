from base64 import b64encode
from collections import defaultdict
from itertools import groupby
import json
import logging

from flask import Flask, render_template, request, redirect, url_for, jsonify
from jsonschema import ValidationError
import psutil
import requests

from .config import config
from .helpers import auth, raise_alert
from . import arduino, db, forms, scheduler, alarm, lights, fence, tank, workshop

app = Flask(__name__)

app.register_blueprint(alarm.blueprint, url_prefix="/alarme")
app.register_blueprint(fence.blueprint, url_prefix="/cloture")
app.register_blueprint(lights.blueprint, url_prefix="/lumieres")
app.register_blueprint(workshop.blueprint, url_prefix="/atelier")
app.register_blueprint(tank.blueprint, url_prefix="/cuve")

debug = False


@app.after_request
def after_request(response):
    if 400 <= response.status_code < 600:
        app.logger.warning(
            f"{request.remote_addr} got {response.status_code} for {request.url}:\n"
            f"\t* Request headers: {request.headers}\n"
            f"\t* Request content: {request.data}\n"
            f"\t* Request content len: {len(request.data)}\n"
            f"\t* Response: {response.response}"
        )
    return response


def config_arduino():
    credentials = b64encode(
        bytes(":".join(config["server"]["http_credentials"]), "utf8")
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
    alerts = db.list_alerts(n_days_ago=7)
    grouped_alerts = groupby(alerts, lambda x: x[0].strftime("%A %d %B"))
    
    return render_template(
        "home.html",
        no_alerts=(len(alerts) < 1),
        alerts=grouped_alerts,
    )


@app.route("/config", methods=["GET", "POST"])
@arduino.post_route
def config_route():
    config_forms = forms.ConfigForms(request.form)
    if request.method == "POST" and config_forms.validate():
        config_forms.populate_config()
        config_arduino()
        config.save()

        scheduler.lunch_job.at = config["alarm"]["lunch"]
        scheduler.night_job.at = config["alarm"]["night"]
        scheduler.tank_job.every = config["tank"]["stats_collection_period"]
        return

    return render_template(
        "config.html",
        forms=config_forms,
        form_errors=any(form.errors for _, form in config_forms.values())
    )


@app.route("/send_config")
def send_config_route():
    config_arduino()
    return ""


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
    )


@app.route("/tank-state")
@arduino.get_route
def tank_state():
    state = arduino.read_state(tank)
    return jsonify(dict(
        **state,
        water_level=tank.water_level(),
    ))


@app.route("/eau/statistiques")
@arduino.get_route
def tank_stats_route():
    return render_template(
        "tank_stats.html",
        volume_between_sensors=tank.volume_between_sensors(),
        volume_below_low_sensor=tank.volume_below_low_sensor(),
        pump_in_power=config["tank"]["pump_in_power"],
        pump_out_power=config["tank"]["pump_out_power"],
        urban_network_power=config["tank"]["urban_network_power"],
    )


@app.route("/debug")
@arduino.get_route
def debug_route():
    states = {
        component.__name__.split(".")[1]: arduino.read_state(component)
        for component in [alarm, fence, lights, workshop, tank]
    }
    states["api"] = arduino.get("config_api")
    for component, conf in states.items():
        states[component] = json.dumps(dict(sorted(conf.items())), indent=2)

    cpu_temp = None
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            cpu_temp = int(f.read()) / 1000
    except (FileNotFoundError, ValueError):
        cpu_temp = None

    return render_template(
        "debug.html",
        states=states,
        debug=debug,
        rpi=dict(
            disk_usage=psutil.disk_usage(__file__),
            cpu_percent=psutil.cpu_percent(),
            cpu_temp=cpu_temp,
            cpu_freq=psutil.cpu_freq(),
            virtual_memory=psutil.virtual_memory(),
        )
    )


@app.route("/debug/<int:on>")
@arduino.get_route
def set_debug_route(on):
    global debug
    debug = on
    scheduler.debug_job.every = config["server"]["debug_period"] if debug else None
    return redirect(url_for("debug_route"))


@app.route("/alert", methods=["POST"])
@auth.login_required
def receive_alert():
    try:
        data = request.get_json()
        name = data["name"]
        msg = data["message"]
        level = data["level"]
    except (json.decoder.JSONDecodeError, KeyError) as e:
        return f"{e.__class__.__name__}: {e}", 500
    else:
        raise_alert(name, msg, level)
    return ""
