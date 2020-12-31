from .base import http_get, http_post
from .. import config


def read_state():
    return http_get("tank")


def configure():
    return http_post(
        "tank",
        {
            "time_to_fill_up": config.get("tank", "time_to_fill_up") * 60 * 1000,
            "min_flow_in": config.get("tank", "min_flow_in"),
            "flow_check_period": config.get("tank", "flow_check_period") * 1000,
            "volume_before_pump_out": config.get("tank", "volume_before_pump_out"),
            "filter_cleaning_period": config.get("tank", "filter_cleaning_period")
            * 60
            * 1000,
            "filter_cleaning_duration": config.get("tank", "filter_cleaning_duration")
            * 1000,
            "filter_cleaning_consecutive_delay": config.get(
                "tank", "filter_cleaning_consecutive_delay"
            )
            * 1000,
            "pump_in_start_duration": config.get("tank", "pump_in_start_duration")
            * 1000,
            "max_pump_out_running_time": config.get("tank", "max_pump_out_running_time")
            * 1000
            * 60,
            "max_duration_without_flow_out": config.get(
                "tank", "max_duration_without_flow_out"
            )
            * 1000
            * 60,
        },
    )


def command_pump_in(is_on):
    return http_post("tank", {"pump_in": int(is_on)})


def activate_pump_in(activated):
    return http_post("tank", {"pump_in_activated": int(activated)})


def command_pump_out(is_on):
    return http_post("tank", {"pump_out": int(is_on)})


def activate_pump_out(activated):
    return http_post("tank", {"pump_out_activated": int(activated)})


def set_manual_mode(activated):
    return http_post("tank", {"manual_mode": int(activated)})


def command_urban_network(is_on):
    return http_post("tank", {"urban_network": int(is_on)})


def command_filter_cleaning(is_on):
    return http_post("tank", {"filter_cleaning": int(is_on)})
