from flask import Flask, request
import subprocess
import os
from werkzeug.utils import secure_filename
import time
import traceback
app = Flask(__name__)

DATA_DIR = "data"


@app.route("/")
def getHome():
    return '<img src="data.png" />'


@app.route("/addPoint", methods=["POST"])
def addPoint():
    req = request.get_json()
    timestamp = req.get("timestamp", time.time())
    with open(os.path.join(DATA_DIR, secure_filename(req["key"])), "a") as f:
        f.write(str(timestamp) + " " + str(req["value"]) + "\n")
    bounds = getBoundaries()
    print("current bounds", bounds)
    print("timestamp", timestamp)
    if timestamp < bounds[0]:
        setBoundaries(timestamp, bounds[1])
        bounds = (timestamp, bounds[1])
    if timestamp > bounds[1]:
        setBoundaries(bounds[0], timestamp)
    return ""


def setBoundaries(from_date, to_date):
    print("set boundaries", from_date, to_date)
    with open(os.path.join(DATA_DIR, "bounds"), "w") as f:
        f.write(str(from_date) + "," + str(to_date))


def getBoundaries():
    try:
        with open(os.path.join(DATA_DIR, "bounds"), "r") as f:
            bounds = f.read().split(",")
            return float(bounds[0]), float(bounds[1])
    except Exception:
        traceback.print_exc()
        return 1589704190.3275669 * 2, 0


@app.route("/data.png")
def getData():
    bounds = getBoundaries()

    paths = {}
    for path in os.listdir(DATA_DIR):
        if os.path.isfile(os.path.join(DATA_DIR, path)) and path != "bounds":
            paths[path.split("_")[0]] = []
    for path in os.listdir(DATA_DIR):
        if os.path.isfile(os.path.join(DATA_DIR, path)) and path != "bounds":
            paths[path.split("_")[0]].append(path)
    count = len(paths.keys())

    print("There's", count, "files in folder")
    if count == 0:
        return ""
    script = 'set datafile separator " "\n'
    script += "set terminal png size 1900,{}\n".format(count * 200)
    script += "set xdata time\n"
    script += 'set timefmt "%s"\n'
    script += 'set format x "%d %b %H:%M"\n'
    script += "set key left top\n"
    script += "set grid\n"
    script += "set multiplot\n"
    script += "set size 1, {}\n".format(1.0 / count)
    script += "set xrange [{}:{}]\n".format(bounds[0], bounds[1])
    c = 0
    for prefix in paths.keys():
        # script += "set ylabel \"{}\" \n".format(path)
        script += "set origin 0.0, {}\n".format(c / count)
        script += "plot {} \n".format(
            ", ".join(
                [
                    '"'
                    + os.path.join(DATA_DIR, path)
                    + "\" using 1:2 with lines title '{}'".format(path)
                    for path in paths[prefix]
                ]
            )
        )
        # if c == 0:
        c += 1
        # plot \"second.dat\" using 1:2 with lines lw 2 lt 3 title 'hosta'

    p = subprocess.Popen(["gnuplot"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    print(script)
    p.stdin.write(script.encode("utf-8"))
    p.stdin.close()
    return p.stdout.read()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
