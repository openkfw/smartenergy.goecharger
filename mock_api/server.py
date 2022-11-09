from flask import Flask, request

app = Flask(__name__)

SUPPORTED_CAR_CHANGE_VALUES = ["amp", "frc", "alw", "psm", "acs"]

car = {
    "car": 1,
    "sse": "051215",
    "amp": 10,
    "frc": 0,
    "alw": True,
    "acu": None,
    "wh": 1136.361,
    "cdi": {"type": 1, "value": 1956999},
    "mca": 10,
    "fmt": 300000,
    "cco": 18,
    "rssi": -71,
    "psm": 1,
    "acs": 1,
}


@app.route("/api/status", methods=["GET"])
def car_status() -> dict:
    global car
    return car


@app.route("/api/set", methods=["GET"])
def car_set() -> dict:
    global car
    args = request.args

    for change_value in SUPPORTED_CAR_CHANGE_VALUES:
        request_value = args.get(change_value, None)
        if request_value != None:
            car[change_value] = (
                bool(int(request_value))
                if change_value == "alw"
                else int(request_value)
            )

    return car


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=4000)
