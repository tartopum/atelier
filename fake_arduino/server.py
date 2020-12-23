import json
import os

from flask import Flask, request, jsonify

app = Flask(__name__)

here = os.path.dirname(__file__)
state_path = os.path.join(here, "state.json")


@app.route("/")
def home():
    with open(state_path) as f:
        return jsonify(json.load(f))


@app.route("/<page>", methods=["GET", "POST"])
def route(page):
    with open(state_path) as f:
        data = json.load(f)

    if request.method == "POST":
        for k, v in request.form.items():
            if k not in data[page]:
                return f"Invalid attribute {k} for {page}", 400
            try:
                v = int(v)
            except ValueError:
                pass
            data[page][k] = v
        with open(state_path, "w") as f:
            json.dump(data, f, indent=2)

    return jsonify(data[page])


@app.route("/tank_stats")
def tank_stats():
    with open(state_path) as f:
        data = json.load(f)
    return jsonify({
        k: data["tank"][k]
        for k in [
            "volume_in", "volume_out_tank", "volume_out_urban_network",
            "pump_in_running_duration", "pump_out_running_duration", "urban_network_running_duration", "is_tank_full",
            "is_tank_empty"
        ]
    })


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5001)
