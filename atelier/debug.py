import os
import datetime as dt
import json
import re

from flask import url_for
import psutil

from . import alarm, arduino, fence, lights, tank, workshop


HERE = os.path.dirname(__file__)
CONTROLLINO_LOG_PATH = os.path.join(HERE, "..", "controllino.log")
ATELIER_LOG_PATH = os.path.join(HERE, "..", "atelier.log")
LOGGING_COLORS = {
    "INFO": "black",
    "WARNING": "orange",
    "ERROR": "red",
    "CRITICAL": "red",
}

is_debug_mode = False


def read_controllino_state():
    states = {
        component.__name__.split(".")[1]: arduino.read_state(component)
        for component in [alarm, fence, lights, workshop, tank]
    }
    for component, conf in states.items():
        states[component] = dict(sorted(conf.items()))
    return states


def get_log_color(header):
    for level, color in LOGGING_COLORS.items():
        if level in header:
            return color
    return "black"


def parse_logs(path):
    PATTERN = r"(?:\[.*?\]\s*){3,}"
    with open(path) as f:
        content = f.read()
        headers = re.findall(PATTERN, content)
        messages = re.split(PATTERN, content)
        colors = [get_log_color(h) for h in headers]
        return zip(headers, messages[1:], colors)


def get_controllino_log():
    states = read_controllino_state()
    states["date"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps(states)


def controllino_logs_to_csv():
    rows = []
    header = ["date"]
    with open(CONTROLLINO_LOG_PATH) as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            row = [data["date"]]
            for component, state in data.items():
                if component == "date":
                    continue
                for k, v in state.items():
                    if i == 0:
                        header.append(f"{component}__{k}")
                    row.append(v)
            rows.append(row)
    return [header, *rows]


def get_disk_usage():
    return psutil.disk_usage(__file__)


def get_disk_usage_percent():
    du = get_disk_usage()
    return du.used / du.total * 100


def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000
    except (FileNotFoundError, ValueError):
        return


def get_cpu_temperature_level():
    t = get_cpu_temperature()
    if t < 60:
        return 0
    if t < 75:
        return 1
    return 2


def get_cpu_freq():
    return psutil.cpu_freq()


def get_cpu_percent():
    return psutil.cpu_percent()


def get_virtual_memory():
    return psutil.virtual_memory()


def get_virtual_memory_percent():
    mu = get_virtual_memory()
    return mu.used / mu.total * 100


def _add_disk_usage_message(messages, thresh):
    u = get_disk_usage_percent()
    if u > thresh:
        messages.append((
            f"Le disque est rempli à {u:.0f}%.",
            url_for("debug_route", _anchor="rpi")
        ))


def _add_cpu_usage_message(messages, thresh):
    u = get_cpu_percent()
    if u > thresh:
        messages.append((
            f"Le CPU est utilisé à {u:.0f}%.",
            url_for("debug_route", _anchor="rpi")
        ))


def _add_mem_usage_message(messages, thresh):
    u = get_virtual_memory_percent()
    if u > thresh:
        messages.append((
            f"La mémoire vive est utilisée à {u:.0f}%.",
            url_for("debug_route", _anchor="rpi")
        ))


def get_errors():
    m = []
    _add_disk_usage_message(m, 90)
    _add_cpu_usage_message(m, 90)
    _add_mem_usage_message(m, 90)

    if get_cpu_temperature_level() > 1:
        m.append((
            f"Le CPU est en surchauffe : {get_cpu_temperature()}°C !",
            url_for("debug_route", _anchor="rpi")
        ))

    return m


def get_warnings():
    m = []
    _add_disk_usage_message(m, 70)
    _add_cpu_usage_message(m, 70)
    _add_mem_usage_message(m, 70)

    if is_debug_mode:
        m.append((
            "Vous êtes en mode debug.",
            url_for("debug_route", _anchor="debug")
        ))

    if get_cpu_temperature_level() == 1:
        m.append((
            f"Le CPU est en légère surchauffe : {get_cpu_temperature()}°C",
            url_for("debug_route", _anchor="rpi")
        ))

    return m
