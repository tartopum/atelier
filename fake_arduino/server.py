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
        data = json.load(f)

    if request.method == "POST":
        for k, v in request.form.items():
            if k not in data[page]:
                return f"Invalid attribute {k} for {page}", 400
            if v in ("0", "1"):
                v = int(v)
            data[page][k] = v
        with open(state_path, "w") as f:
            json.dump(data, f)

    return jsonify(data[page])


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5001)
