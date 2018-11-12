import os
import re
import json
import matplotlib.pyplot as plt

def json2csv(f):
    json_data=f.read()
    # will return exception when cant parse json
    # data is a python dict
    data = json.loads(json_data)
    print("Data keys: " + str(data.keys()))
    #data.values()
    xlabels = data.get("x_labels")
    xaxis = data.get("xaxis")
    yaxis = data.get("yaxis")
    print(xaxis)
    points = data.get("series")
    points = points[0].get("data")
    xvalues = []
    yvalues = []
    for p in points:
        xvalues.append(p[0])
        yvalues.append(p[1])
    plt.scatter(xvalues, yvalues)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.show()

def analyseData(url):
    somID = re.search(r"id=(\d+)", url).group(1)
    # catch exception that wget fails (or maybe rage unavailable)
    os.system("wget -q \"" + str(url)+ "\" -O /tmp/somdata" + str(somID))
    print("Fetched data from " + url)
    raw = open("/tmp/somdata" + str(somID))
    json2csv(raw)
