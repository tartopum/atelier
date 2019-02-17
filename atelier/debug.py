import datetime as dt
import json
import os

from . import alarm, arduino, fence, lights, tank, workshop


HERE = os.path.dirname(__file__)
CONTROLLINO_LOG_PATH = os.path.join(HERE, "..", "debug_controllino.txt")


def read_controllino_state():
    states = {
        component.__name__.split(".")[1]: arduino.read_state(component)
        for component in [alarm, fence, lights, workshop, tank]
    }
    for component, conf in states.items():
        states[component] = dict(sorted(conf.items()))
    return states


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
