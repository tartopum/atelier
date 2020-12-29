from collections import namedtuple

from . import db, monitoring
from .notifications import send_sms


SMS_MIN_ALERT_LEVEL = 2
WARNING_ALERT_LEVEL = 1
ERROR_ALERT_LEVEL = 2


_StateAlert = namedtuple(
    "_StateAlert", ["name", "state_key", "val_getter", "alert_val", "message"]
)
Alert = namedtuple("Alert", ["name", "message", "level"])


STATE_ERRORS = (
    _StateAlert(
        "alarm",
        "workshop",
        lambda state: state["alarm"]["breach"],
        1,
        "Une intrusion est détectée !",
    ),
    _StateAlert(
        "tank", "tank", "is_filter_in_blocked", 1, "Le filtre de la cuve est encrassé."
    ),
    _StateAlert(
        "tank",
        "tank",
        "is_motor_in_blocked",
        1,
        "Le moteur de la pompe du puits est en panne.",
    ),
    _StateAlert(
        "tank",
        "tank",
        "is_motor_out_blocked",
        1,
        "Le moteur de la pompe du surpresseur est en panne.",
    ),
    _StateAlert(
        "tank", "tank", "is_overpressured", 1, "Le système est en surpression."
    ),
    _StateAlert("tank", "tank", "manual_mode", 1, "La cuve est en mode manuel."),
)

STATE_WARNINGS = (
    _StateAlert("fence", "fence", "state", 0, "La clôture est éteinte."),
    _StateAlert("fence", "fence", "activated", 0, "La clôture est éteinte."),
    _StateAlert(
        "power_supply",
        "workshop",
        "power_supply",
        0,
        "L'alimentation de l'atelier est coupée.",
    ),
)


def _add_disk_usage_alert(alerts, thresh, level):
    u = monitoring.get_disk_usage_percent()
    if u > thresh:
        alerts.append(
            Alert(
                "monitoring_rpi",
                f"Le disque de la Raspberry est rempli à {u:.0f}%.",
                level,
            )
        )


def _add_cpu_usage_alert(alerts, thresh, level):
    u = monitoring.get_cpu_percent()
    if u > thresh:
        alerts.append(
            Alert(
                "monitoring_rpi",
                f"Le processeur de la Raspberry est utilisé à {u:.0f}%.",
                level,
            )
        )


def _add_mem_usage_alert(alerts, thresh, level):
    u = monitoring.get_virtual_memory_percent()
    if u > thresh:
        alerts.append(
            Alert(
                "monitoring_rpi",
                f"La mémoire vive de la Raspberry est utilisée à {u:.0f}%.",
                level,
            )
        )


def _get_state_alerts(states, conditions, level):
    alerts = []
    for name, state_key, val_getter, cond_val, msg in conditions:
        state = states[state_key]
        if callable(val_getter):
            val = val_getter
        else:
            val = state[val_getter]
        if val == cond_val:
            alerts.append(Alert(name, msg, level))
    return alerts


def get_errors(states):
    alerts = _get_state_alerts(states, STATE_ERRORS, ERROR_ALERT_LEVEL)
    _add_disk_usage_alert(alerts, 90, ERROR_ALERT_LEVEL)
    _add_cpu_usage_alert(alerts, 90, ERROR_ALERT_LEVEL)
    _add_mem_usage_alert(alerts, 90, ERROR_ALERT_LEVEL)

    if monitoring.get_cpu_temperature_level() > 1:
        alerts.append(
            Alert(
                "monitoring_rpi",
                "Le processeur de la Raspberry est en surchauffe : "
                f"{monitoring.get_cpu_temperature()}°C !",
                ERROR_ALERT_LEVEL,
            )
        )

    return alerts


def get_warnings(states):
    alerts = _get_state_alerts(states, STATE_WARNINGS, WARNING_ALERT_LEVEL)
    _add_disk_usage_alert(alerts, 70, WARNING_ALERT_LEVEL)
    _add_cpu_usage_alert(alerts, 70, WARNING_ALERT_LEVEL)
    _add_mem_usage_alert(alerts, 70, WARNING_ALERT_LEVEL)

    if monitoring.is_debug_mode:
        alerts.append(
            Alert("monitoring_debug", "Vous êtes en mode debug.", WARNING_ALERT_LEVEL)
        )

    if monitoring.get_cpu_temperature_level() == 1:
        alerts.append(
            Alert(
                "monitoring_rpi",
                "Le processeur de la Raspberry est en légère surchauffe : "
                f"{monitoring.get_cpu_temperature()}°C",
                WARNING_ALERT_LEVEL,
            )
        )

    return alerts


def raise_alert(name, msg, level):
    db.add_alert(name, msg)
    if level < SMS_MIN_ALERT_LEVEL:
        return
    send_sms(msg)


def delete_old():
    db.delete_old_alerts()
