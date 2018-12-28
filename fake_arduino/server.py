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
        print(request.form)
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


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5001)
