from flask import Flask, request
import subprocess
import os
from werkzeug.utils import secure_filename
import time
import traceback
import urllib

app = Flask(__name__)

IMG_WIDTH = 1900
DATA_DIR = "data"
DURATIONS = [
    (0, "ALL"),
    (1.577e7, "6M"),
    (0.788e7, "3M"),
    (2.628e6, "1M"),
    (604800, "1w"),
    (259200, "3d"),
    (86400, "1d"),
    (86400 / 2, "12h"),
    (3600 * 3, "3h"),
    (3600, "1h"),
    (1800, "30m"),
    (900, "15m"),
    (300, "5m"),
]


@app.route("/")
def getHome():
    paramstr = urllib.parse.urlencode(request.args)
    css = """
    <style>
        a {
              text-decoration: none;
        }
        a:link{
          color:blue;
        }
        a:visited{
          color:blue;
        }
        a:hover{
          color:orange;
        }
        a:focus{
          color:green;
        }
        a:active{
          color:red;
        }
    </style>"""
    imgStr = '<img src="data.png?{}" />'.format(paramstr)
    buttonStr = ""
    for duration in DURATIONS:
        current_duration = request.args.get("duration", 0)
        if int(duration[0]) == int(current_duration):
            buttonStr += "<a> {} </a>".format(duration[1])
        else:
            buttonStr += '<a href="/?duration={}"> {} </a>'.format(
                int(duration[0]), duration[1]
            )

    return css + buttonStr + imgStr


@app.route("/addPoints", methods=["POST"])
def addPoints():
    points = request.get_json()
    for req in points:
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
    duration = request.args.get("duration")
    print(duration)
    if duration and int(duration) != 0:
        bounds = (time.time() - int(duration), bounds[1])
    print(bounds)
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
    script += "set terminal png size {},{}\n".format(IMG_WIDTH, count * 200)
    script += "set xdata time\n"
    script += 'set timefmt "%s"\n'
    script += 'set format x "%d %b %H:%M"\n'
    script += "set key left top\n"
    script += "set grid\n"
    script += "set multiplot\n"
    script += "set size 1, {}\n".format(1.0 / count)
    script += "set xrange [{}:{}]\n".format(bounds[0], bounds[1])
    c = 0
    duration = bounds[1] - bounds[0]
    interval = (bounds[1] - bounds[0]) / IMG_WIDTH
    print(interval)
    for prefix in paths.keys():
        # script += "set ylabel \"{}\" \n".format(path)
        script += "set origin 0.0, {}\n".format(c / count)
        script += "plot {} \n".format(
            ", ".join(
                [
                    "\"-\" using 1:2 with lines title '{}'".format(path)
                    for path in paths[prefix]
                ]
            )
        )
        script += "\n"
        for path in paths[prefix]:
            with open(os.path.join(DATA_DIR, path), "r") as reader:
                lastTS = 0
                for line in reader.readlines():
                    currentTS = float(line.split(" ")[0])
                    if currentTS - lastTS > interval:
                        script += line
                        lastTS = currentTS
                script += "e\n"

        # if c == 0:
        c += 1
        # plot \"second.dat\" using 1:2 with lines lw 2 lt 3 title 'hosta'

    p = subprocess.Popen(["gnuplot"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    #print(script)
    p.stdin.write(script.encode("utf-8"))
    p.stdin.close()
    return p.stdout.read()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
