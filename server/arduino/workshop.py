from .base import http_get, http_post
from .. import config


def read_state():
    return {
        "alarm": http_get("alarm"),
        "lights": http_get("lights"),
        **http_get("workshop"),
    }


def configure():
    http_post(
        "alarm",
        {
            "delay_before_alert": config.get("alarm", "delay_before_alert") * 1000,
            "delay_before_listening": config.get("alarm", "delay_before_listening")
            * 1000,
        },
    )
    http_post(
        "lights", {"press_delay": int(config.get("lights", "press_delay") * 1000)}
    )
    http_post(
        "workshop",
        {
            "inactivity_delay": config.get("lights", "inactivity_delay") * 60 * 1000,
            "power_reminder_delay": config.get("power", "delay_before_reminder")
            * 3600
            * 1000,
        },
    )


def command_power_supply(is_on):
    return http_post("workshop", {"power_supply": int(is_on)})


def set_power_supply_mode(is_manual):
    return http_post("workshop", {"power_manual_mode": int(is_manual)})


def activate_alarm(activated):
    return http_post("alarm", {"listen": int(activated)})


def command_light(n, is_on):
    return http_post("lights", {n: int(is_on)})
