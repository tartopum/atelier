import argparse

arduino = dict(
    ip="localhost",
    port=80,
    timeout=10,
)


def from_cmdline():
    global arduino
    parser = argparse.ArgumentParser()
    parser.add_argument("arduino_ip")
    parser.add_argument("--arduino_port", type=int, default=arduino["port"])
    parser.add_argument(
        "--timeout",
        type=int,
        default=arduino["timeout"],
        help="Timeout for communications with the Arduino (in seconds)"
    )
    args = parser.parse_args()

    arduino["ip"] = args.arduino_ip
    arduino["port"] = args.arduino_port
    arduino["timeout"] = args.timeout
