import datetime as dt

from flask import Blueprint, jsonify, render_template, request

from .base import arduino_get_route, arduino_post_route, redirect_prev
from ..auth import auth
from ... import arduino, config, tank


blueprint = Blueprint("tank", __name__)


@blueprint.route("/")
@arduino_get_route
def tank_route():
    return render_template(
        "tank.html", state=arduino.tank.read_state(), water_level=tank.water_level()
    )


@blueprint.route("/etat")
@arduino_get_route
def tank_state_route():
    # To update the schema with AJAX
    state = arduino.tank.read_state()
    return jsonify(dict(**state, water_level=tank.water_level()))


@blueprint.route("/pompe-puits/<int:is_on>")
@arduino_post_route
def command_pump_in_route(is_on):
    arduino.tank.command_pump_in(is_on)
    return redirect_prev()


@blueprint.route("/pompe-puits/activer")
@arduino_post_route
def activate_pump_in_route():
    arduino.tank.activate_pump_in(1)
    return redirect_prev()


@blueprint.route("/pompe-surpresseur/<int:is_on>")
@arduino_post_route
def command_pump_out_route(is_on):
    arduino.tank.command_pump_out(is_on)
    return redirect_prev()


@blueprint.route("/pompe-surpresseur/activer")
@arduino_post_route
def activate_pump_out_route():
    arduino.tank.activate_pump_out(1)
    return redirect_prev()


@blueprint.route("/mode-manuel/<int:activated>")
@arduino_post_route
def set_manual_mode_route(activated):
    arduino.tank.set_manual_mode(activated)
    return redirect_prev()


@blueprint.route("/reseau-urbain/<int:is_on>")
@arduino_post_route
def command_urban_network_route(is_on):
    arduino.tank.command_urban_network(is_on)
    return redirect_prev()


@blueprint.route("/nettoyage-filtre/<int:is_on>")
@arduino_post_route
def command_filter_cleaning_route(is_on):
    arduino.tank.command_filter_cleaning(is_on)
    return redirect_prev()


@blueprint.route("/statistiques")
@auth.login_required
def stats_route():
    return render_template(
        "tank_stats.html",
        volume_between_sensors=tank.volume_between_sensors(),
        volume_below_low_sensor=tank.volume_below_low_sensor(),
        pump_in_power=config.get("tank", "pump_in_power"),
        pump_out_power=config.get("tank", "pump_out_power"),
        urban_network_power=config.get("tank", "urban_network_power"),
    )


@blueprint.route("/stats/consommation-eau")
def water_consumption_data_route():
    try:
        days = int(request.args.get("days"))
        assert days > 0, "The number of days must be positive"
        timestep = int(request.args.get("timestep"))
        assert timestep > 0, "The timestep must be positive"
    except (TypeError, ValueError, AssertionError) as e:
        return str(e), 400

    try:
        end = dt.datetime.strptime(request.args.get("end", ""), "%Y-%m-%d")
    except (ValueError, KeyError):
        end = dt.datetime.now()

    return jsonify(
        tank.get_consumption_data(
            dt.timedelta(minutes=timestep), dt.timedelta(days), end
        )
    )


@blueprint.route("/stats/niveau-cuve")
def water_level_history_route():
    timestep = dt.timedelta(hours=1)
    end = tank.get_stats_end_date(timestep)
    start = tank.get_stats_start_date(end, dt.timedelta(7), timestep)
    ref_empty, dates, rel_volumes, delta_volume = tank.read_volume_history(
        start, end=end
    )
    start_volume = (0 if ref_empty else tank.volume_between_sensors()) + delta_volume
    dates, rel_volumes = tank.bin_time_series(dates, rel_volumes, timestep)
    # The deltas during h:... lead to the volume at (h+1), not at h
    dates = [d + timestep for d in dates]
    rel_volumes = [sum(bin_vol) for bin_vol in rel_volumes]
    for i, delta in enumerate(rel_volumes):
        if i == 0:
            rel_volumes[i] = start_volume + delta
        else:
            rel_volumes[i] = rel_volumes[i - 1] + delta
    return jsonify(
        {"dates": [d.strftime("%Y-%m-%d %H") for d in dates], "volumes": rel_volumes}
    )


@blueprint.route("/stats/consommation-electrique")
def power_consumption_data_route():
    try:
        days = int(request.args.get("days"))
        assert days > 0, "The number of days must be positive"
        timestep = int(request.args.get("timestep"))
        assert timestep > 0, "The timestep must be positive"
    except (TypeError, ValueError, AssertionError) as e:
        return str(e), 400

    timestep = dt.timedelta(minutes=timestep)
    end = tank.get_stats_end_date(timestep)
    start = tank.get_stats_start_date(end, dt.timedelta(days), timestep)
    dates, pump_in, pump_out, city = tank.read_power_consumption(start, end=end)
    binned_dates, pump_in = tank.bin_time_series(
        dates, pump_in, timestep, start_date=start
    )
    _, pump_out = tank.bin_time_series(dates, pump_out, timestep, start_date=start)
    _, city = tank.bin_time_series(dates, city, timestep, start_date=start)
    date_format = tank.date_format_from_step(timestep)

    return jsonify(
        {
            "dates": [d.strftime(date_format) for d in binned_dates],
            "pump_in": [sum(period) / 60 for period in pump_in],
            "pump_out": [sum(period) / 60 for period in pump_out],
            "city": [sum(period) / 60 for period in city],
        }
    )
