import os
import re
import json
import matplotlib.pyplot as plt

points = None
nPoints = 0
numOfSplits = 0
axisPos = []
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
    global numOfSplits
    numOfSplits = len(points[0][2].keys())
    global axisPos
    for x in xaxis.split(","):
        axisPos.append(list(points[0][2]).index(x))

    results = []
    # find split options in json
    j = 0
    for i in points:
        results.append([i[0], i[1]])
        dict = i[2]
        for v in dict.values():
            results[j].append(v)
        j += 1
    global nPoints
    nPoints = j

    # results = [xvalue, yvalue, option1, option2, ...]
    return results

def drawGraph(dataPoints, config):

    showlegend = config[0]

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
                text = p[2]
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

    # if we have chosen to split then plot multiple graphs
    global numOfSplits
    x = []; y = []
    if numOfSplits > 1:
        group = []
        global axisPos
        for p in dataPoints:
            # collect different x,y's of each split value, excluding xaxis
            s = ""
            for i in range(numOfSplits):
                if i in axisPos:
                    continue
                else:
                    s += p[i+2] + ","
            try:
                position = group.index(s)
                x[position].append(p[0])
                y[position].append(p[1])
            except:
                # didnt match
                group.append(s)
                x.append([]); y.append([])

    elif numOfSplits == 1:
        for p in dataPoints:
            x.append(p[0])
            y.append(p[1])

    global nPoints
    pointSize=250/(nPoints)**0.35
    if numOfSplits > 1:
        for i in range(len(x)):
            if showlegend:
                plt.scatter(x[i], y[i], s=pointSize, label=group[i])
            else:
                plt.scatter(x[i], y[i], s=pointSize)
    else:
        sc = plt.scatter(x,y, s=pointSize)
    global xaxis; global yaxis
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    cid = fig.canvas.mpl_connect("button_press_event", onclick)

    if showlegend:
        plt.legend()
    plt.show()
    fig.canvas.mpl_disconnect(cid)

def analyseData(url, config):
    somID = re.search(r"id=(\d+)", url).group(1)
    # catch exception that wget fails (or maybe rage unavailable)
    os.system("wget -q \"" + str(url)+ "\" -O /tmp/somdata" + str(somID))
    print("Fetched data from " + url)
    raw = open("/tmp/somdata" + str(somID))
    points = json2points(raw)
    drawGraph(points, config)
