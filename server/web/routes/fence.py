from flask import Blueprint, render_template

from .base import arduino_get_route, arduino_post_route, redirect_prev
from ... import arduino


blueprint = Blueprint("fence", __name__)


@blueprint.route("/")
@arduino_get_route
def fence_route():
    return render_template("fence.html", state=arduino.fence.read_state())


@blueprint.route("/activer/<int:activated>")
@arduino_post_route
def activate_route(activated):
    arduino.fence.activate(activated)
    return redirect_prev()


@blueprint.route("/commander/<int:is_on>")
@arduino_post_route
def command_route(is_on):
    arduino.fence.command(is_on)
    return redirect_prev()
