from flask import url_for

from .. import monitoring


_ERROR_CONDITIONS = (
    (
        "workshop",
        lambda state: state["alarm"]["breach"],
        1,
        "Une intrusion est détectée !",
        "workshop.workshop_route",
    ),
    (
        "tank",
        "is_filter_in_blocked",
        1,
        "Le filtre de la cuve est encrassé.",
        "tank.tank_route",
    ),
    (
        "tank",
        "is_motor_in_blocked",
        1,
        "Le moteur de la pompe du puits est en panne.",
        "tank.tank_route",
    ),
    (
        "tank",
        "is_motor_out_blocked",
        1,
        "Le moteur de la pompe du surpresseur est en panne.",
        "tank.tank_route",
    ),
    (
        "tank",
        "is_overpressured",
        1,
        "Le système est en surpression.",
        "tank.tank_route",
    ),
    ("tank", "manual_mode", 1, "La cuve est en mode manuel.", "tank.tank_route"),
)
_WARNING_CONDITIONS = (
    ("fence", "state", 0, "La clôture est éteinte.", "fence.fence_route"),
    (
        "workshop",
        "power_supply",
        0,
        "L'alimentation de l'atelier est coupée.",
        "workshop.workshop_route",
    ),
)


def _get_messages(states, conditions):
    m = []
    for state_key, val_getter, cond_val, msg, url_name in conditions:
        state = states[state_key]
        if callable(val_getter):
            val = val_getter
        else:
            val = state[val_getter]
        if val == cond_val:
            m.append((msg, url_for(url_name)))
    return m


def _add_disk_usage_message(messages, thresh):
    u = monitoring.get_disk_usage_percent()
    if u > thresh:
        messages.append(
            (
                f"Le disque de la Raspberry est rempli à {u:.0f}%.",
                url_for("monitoring.monitoring_route", _anchor="rpi"),
            )
        )


def _add_cpu_usage_message(messages, thresh):
    u = monitoring.get_cpu_percent()
    if u > thresh:
        messages.append(
            (
                f"Le processeur de la Raspberry est utilisé à {u:.0f}%.",
                url_for("monitoring.monitoring_route", _anchor="rpi"),
            )
        )


def _add_mem_usage_message(messages, thresh):
    u = monitoring.get_virtual_memory_percent()
    if u > thresh:
        messages.append(
            (
                f"La mémoire vive de la Raspberry est utilisée à {u:.0f}%.",
                url_for("monitoring.monitoring_route", _anchor="rpi"),
            )
        )


def get_errors(states):
    messages = _get_messages(states, _ERROR_CONDITIONS)
    _add_disk_usage_message(messages, 90)
    _add_cpu_usage_message(messages, 90)
    _add_mem_usage_message(messages, 90)

    if monitoring.get_cpu_temperature_level() > 1:
        messages.append(
            (
                f"Le processeur de la Raspberry est en surchauffe : {monitoring.get_cpu_temperature()}°C !",
                url_for("monitoring.monitoring_route", _anchor="rpi"),
            )
        )

    return messages


def get_warnings(states):
    messages = _get_messages(states, _WARNING_CONDITIONS)
    _add_disk_usage_message(messages, 70)
    _add_cpu_usage_message(messages, 70)
    _add_mem_usage_message(messages, 70)

    if monitoring.is_debug_mode:
        messages.append(
            (
                "Vous êtes en mode debug.",
                url_for("monitoring.monitoring_route", _anchor="debug"),
            )
        )

    if monitoring.get_cpu_temperature_level() == 1:
        messages.append(
            (
                f"Le processeur de la Raspberry est en légère surchauffe : {monitoring.get_cpu_temperature()}°C",
                url_for("monitoring.monitoring_route", _anchor="rpi"),
            )
        )

    return messages
