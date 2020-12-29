from flask import Blueprint, render_template

from .base import arduino_get_route, arduino_post_route, redirect_prev
from ... import arduino


blueprint = Blueprint("workshop", __name__)


@blueprint.route("/")
@arduino_get_route
def workshop_route():
    state = arduino.workshop.read_state()
    return render_template(
        "workshop.html", alarm=state["alarm"], lights=state["lights"], workshop=state
    )


@blueprint.route("/alimentation/<int:is_on>")
@arduino_post_route
def command_power_supply_route(is_on):
    arduino.workshop.command_power_supply(is_on)
    return redirect_prev(anchor="alimentation")


@blueprint.route("/alimentation/manuel/<int:is_manual>")
@arduino_post_route
def set_power_supply_mode_route(is_manual):
    arduino.workshop.set_power_supply_mode(is_manual)
    return redirect_prev(anchor="alimentation")


@blueprint.route("/alarme/<int:activated>")
@arduino_post_route
def activate_alarm_route(activated):
    arduino.workshop.activate_alarm(activated)
    return redirect_prev(anchor="alarme")


@blueprint.route("/lumieres/<int:n>/<int:is_on>")
@arduino_post_route
def command_light_route(n, is_on):
    arduino.workshop.command_light(n, is_on)
    return redirect_prev(anchor=f"lumiere-{n}")
