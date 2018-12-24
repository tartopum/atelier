import json
import os

from flask import Flask, request, jsonify

app = Flask(__name__)

here = os.path.dirname(__file__)
state_path = os.path.join(here, "state.json")


@app.route("/")
def home():
    with open(state_path) as f:
        return "<pre>" + json.dumps(json.load(f), indent=4) + "</pre>"


@app.route("/<page>", methods=["GET", "POST"])
def route(page):
    with open(state_path) as f:
        data = json.load(f)[page]

    if request.method == "POST":
        for k, v in request.form.items():
            data[k] = v
        with open(state_path, "w") as f:
            json.dump(data, f)

    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
