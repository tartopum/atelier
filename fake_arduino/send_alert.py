import requests


def send(name, msg, ip, port):
    requests.post(
        f"http://{ip}:{port}/alert",
        json={"name": name, "message": msg}
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--msg", default="")
    parser.add_argument("--ip", default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    send(args.name, args.msg, args.ip, args.port)
