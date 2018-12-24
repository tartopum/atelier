import argparse

from atelier import app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("arduino_ip")
    parser.add_argument("--arduino_port", type=int, default=80)
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout for communications with the Arduino (in seconds)"
    )
    args = parser.parse_args()

    app.config["ARDUINO_IP"] = args.arduino_ip
    app.config["ARDUINO_PORT"] = args.arduino_port
    app.config["ARDUINO_HOST"] = f"http://{args.arduino_ip}:{args.arduino_port}"
    app.config["TIMEOUT"] = args.timeout

    app.run(host="0.0.0.0")
