import os
import re
import json
import matplotlib.pyplot as plt

points = None
xaxis = ""
yaxis = ""

def json2points(f):
    json_data=f.read()
    # will return exception when cant parse json
    # data is a python dict
    data = json.loads(json_data)
    xlabels = data.get("x_labels")
    global xaxis
    global yaxis
    xaxis = data.get("xaxis")
    yaxis = data.get("yaxis")
    global points
    points = data.get("series")
    points = points[0].get("data")

    results = []
    # find split options in json
    j = 0
    for i in points:
        results.append([i[0], i[1]])
        dict = i[2]
        for v in dict.values():
            results[j].append(v)
        j += 1

    # results = [xvalue, yvalue, option1, option2, ...]
    return results

def drawGraph(dataPoints):

    fig,ax = plt.subplots()
    annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)


    def update_annot(ind):
        pos = sc.get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = "Not found"
        for p in dataPoints:
            if p[0] == pos[0] and p[1] == pos[1]:
                text = p[2].get(xl)
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)


    def onclick(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    x = []; y = []
    for p in dataPoints:
        x.append(p[0])
        y.append(p[1])

    sc = plt.scatter(x,y)
    global xaxis; global yaxis
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    cid = fig.canvas.mpl_connect("button_press_event", onclick)

    plt.show()
    fig.canvas.mpl_disconnect(cid)

def analyseData(url):
    somID = re.search(r"id=(\d+)", url).group(1)
    # catch exception that wget fails (or maybe rage unavailable)
    os.system("wget -q \"" + str(url)+ "\" -O /tmp/somdata" + str(somID))
    print("Fetched data from " + url)
    raw = open("/tmp/somdata" + str(somID))
    points = json2points(raw)
    drawGraph(points)
