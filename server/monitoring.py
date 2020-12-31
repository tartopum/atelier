import os
import datetime as dt
import html
import json
import re

import psutil

from . import arduino
from . import config


HERE = os.path.dirname(__file__)
LOGGING_COLORS = {
    "INFO": "black",
    "WARNING": "orange",
    "ERROR": "red",
    "CRITICAL": "red",
}

is_debug_mode = False


def get_log_color(header):
    for level, color in LOGGING_COLORS.items():
        if level in header:
            return color
    return "black"


def format_log_message(m):
    m = html.escape(m)
    m = m.replace("\n", "<br/>")
    m = re.sub("\s", "&nbsp;", m)
    return m


def parse_logs(path):
    PATTERN = r"^(?:\[[\w \-:,]+\]){3}"
    with open(path) as f:
        content = f.read()
        headers = re.findall(PATTERN, content, flags=re.MULTILINE)
        messages = re.split(PATTERN, content, flags=re.MULTILINE)
        colors = [get_log_color(h) for h in headers]
        return zip(headers, map(format_log_message, messages[1:]), colors)


def get_controllino_log():
    states = arduino.read_states()
    states["date"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps(states)


def controllino_logs_to_csv():
    rows = []
    header = ["date"]
    with open(config.CONTROLLINO_LOG_PATH) as f:
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
