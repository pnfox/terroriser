import os
import re
import json
import operator
import matplotlib.pyplot as plt

points = []
nPoints = 0
numOfSplits = 0
axisPos = []
splitNames = []
splitChoice = []
xaxis = ""
yaxis = ""

def initialize():
    global points
    global nPoints
    global numOfSplits
    global axisPos
    global splitNames
    global splitChoice
    global xaxis
    global yaxis
    points = []
    nPoints = 0
    numOfSplits = 0
    axisPos = []
    splitNames = []
    splitChoice = []
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
    series = data.get("series")
    if not series:
        return None

    for i in range(len(series)):
         for p in series[i].get("data"):
             points.append(p)

    global splitNames
    splitNames = list(points[0][2].keys())
    global numOfSplits
    global splitChoice
    numOfSplits = len(splitChoice)

    global axisPos
    for x in xaxis.split(","):
        if list(points[0][2].keys()).index(x):
            axisPos.append(list(points[0][2].keys()).index(x))

    results = []
    # find split options in json
    j = 0
    for i in points:
        results.append([i[0], i[1]])
        dict = i[2]
        if not splitChoice:
            for v in dict.values():
                results[j].append(v)
        else:
            for split in splitChoice:
                results[j].append(dict.get(split))
        j = j + 1
    global nPoints
    nPoints = j

    # results = [xvalue, yvalue, option1, option2, ...]
    return results

def order(a, b):
    # need to order a and move b accordingly
    # could map each entry in a with b
    # this would assume no two values in b are equal, which is possible
    map = []
    for i in range(len(a)):
        map.append([a[i], b[i]])

    map = sorted(map)
    k = 0
    for i in map:
        a[k] = i[0]
        b[k] = i[1]
        k += 1

    return a, b

def drawGraph(dataPoints, config):

    showlegend = config[0]

    fig,ax = plt.subplots()
    annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                bbox=dict(boxstyle="round", fc="w"),
                arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)


    def update_annot(ind, plotIndex):
        pos = sc[plotIndex].get_offsets()[ind["ind"][0]]
        annot.xy = pos
        text = "Not found"

        if type(x[0]) is not int:
            # we need to find where x[plotIndex] starts in dataPoints
            s = 0
            for i in x:
                if i == x[plotIndex]:
                    break
                s += len(i)

            for p in range(len(x[plotIndex])):
                if x[plotIndex][p] == pos[0] and y[plotIndex][p] == pos[1]:
                    # FIX: p doesn't point to same point in x and dataPoints
                    # fix with this p = len(x[plotIndex]) + p
                    text = "x-value: " + str(pos[0]) + "\ny-value: " + str(pos[1]) + "\n" + str(dataPoints[s+p][2])
                    break
        else:
            for p in dataPoints:
                if p[0] == pos[0] and p[1] == pos[1]:
                    text =  "x-value: " + str(pos[0]) + "\ny-value: " + str(pos[1]) + "\n" + str(p[2])
                    break
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.2)


    def onclick(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            k = 0
            for plots in sc:
                # tmp fix for disabling annotations on line graphs
                if type(plots) is list:
                    return
                cont, ind = plots.contains(event)
                if cont:
                    update_annot(ind, k)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    break
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()
                        break
                k += 1

    # if we have chosen to split then plot multiple graphs
    global numOfSplits
    global splitNames
    x = []; y = []; group = []
    if numOfSplits > 1 or config[1]:
        global axisPos
        for p in dataPoints:
            # collect different x,y's of each split value, excluding xaxis
            s = ""
            for i in range(numOfSplits):
                if i in axisPos:
                    # if we used branch list (assuming this is also xaxis value)
                    # or we branch was other option field
                    # then dont continue as we want to color different branches
                    if config[1] == 0:
                        continue
                s += p[i+2] + "\n"
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
    sc = []
    # if we use splits or config[1] then color different plots
    if numOfSplits > 1 or config[1]:
        for i in range(len(x)):
            if showlegend:
                # order points so that plotted properly
                x[i], y[i] = order(x[i], y[i])
                if config[2] == 1:
                    sc.append(plt.plot(x[i], y[i], label=group[i]))
                else:
                    sc.append(plt.scatter(x[i], y[i], label=group[i]))
            else:
                if config[2] == 1:
                    sc.append(plt.plot(x[i], y[i]))
                else:
                    sc.append(plt.scatter(x[i], y[i], s=pointSize))
    # no color used
    else:
        if config[2] == 1:
            sc.append(plt.plot(x,y))
        else:
            sc.append(plt.scatter(x,y, s=pointSize))
    global xaxis; global yaxis
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    cid = fig.canvas.mpl_connect("button_press_event", onclick)

    if showlegend:
        plt.legend()
    plt.show()
    fig.canvas.mpl_disconnect(cid)

def analyseData(url, config):

    initialize()
    global splitChoice
    print(url)
    somID = re.search(r"id=(\d+)", url).group(1)
    splits = re.findall(r'&f_(\w+)=1', url)
    if splits:
        for i in splits:
            splitChoice.append(i)
            config[1] = 1
    # no splits from gui so default splits
    else:
        splitChoice = ['branch']

    # catch exception that wget fails (or maybe rage unavailable)
    if os.name == "posix":
        os.system("wget -q \"" + str(url)+ "\" -O /tmp/somdata" + str(somID))
    if os.name == "nt":
        response = requests.get(str(url))
        response.raise_for_status()
        with open("somdata" + str(somID)) as h:
            for block in response.iter_count(1024):
                h.write(block)
    print("Fetched data")
    if os.name == "posix":
        raw = open("/tmp/somdata" + str(somID))
    if os.name == "nt":
        raw = open("somdata" + str(somID))
    points = json2points(raw)
    if not points:
        return None
    drawGraph(points, config)
