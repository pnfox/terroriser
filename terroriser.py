import os
import re
import json
import operator
import subprocess
import matplotlib.pyplot as plt
import requests

points = []
nPoints = 0
numOfSplits = 0
axisPos = []
splitNames = []
splitChoice = []
xaxis = ""
yaxis = ""
som_name = ""

def initialize():
    global points
    global pointInformation
    global nPoints
    global numOfSplits
    global axisPos
    global splitNames
    global splitChoice
    global xaxisChoice
    global xaxis
    global yaxis
    global regression
    points = []
    nPoints = 0
    numOfSplits = 0
    axisPos = []
    splitNames = []
    splitChoice = []
    xaxis = ""
    yaxis = ""

class TerroriserError(Exception):
    def __init__(self, message):
        super().__init__(message)

def json2points(f):
    json_data=f.read()
    if len(json_data.split()) == 0:
        raise TerroriserError("No data found")
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
    # splitChoice contains the values of &f_(\w+)= in the url 
    numOfSplits = len(splitChoice)

    global axisPos
    # xaxis branch is selected by user but
    # position of branch values in points.keys() is undetermined
    # this finds the position, we need this later
    for x in xaxis.split(","):
        position = list(points[0][2].keys()).index(x)
        if position:
            axisPos.append(position)

    results = []
    global pointInformation
    pointInformation = []
    # find split options in json
    j = 0
    for i in points:
        results.append([j, i[0], i[1]])
        dict = i[2]
        pointInformation.append([j, dict.values()])
        # Add the splitByIdentifier, used later to determine color
        if not splitChoice:
            for v in dict.values():
                results[j].append(v)
        else:
            global regression
            if regression:
                for key in dict.keys():
                    results[j].append(dict.get(key))
            else:
                for split in splitChoice:
                    results[j].append(dict.get(split))
        j = j + 1
    global nPoints
    nPoints = j

    # results = [xvalue, yvalue, splitByIdentifier]
    return results

# Used to order two arrays a, b when each entry in both
# corresponds to a pair (a[0] is with b[0], etc...)
# orders based on a in ascending order
# returns ordered arrays a, b
def order(a, b):
    map = []
    lenA = len(a)
    if lenA > 1:
        for i in range(lenA):
            map.append([a[i], b[i]])
    elif lenA == 0:
        print("WARNING: terroriser.order: No data in array")
        return [], []
    else:
        map.append([a,b])

    map = sorted(map)
    k = 0
    for i in map:
        a[k] = i[0]
        b[k] = i[1]
        k += 1

    return a, b

# Given the dataPoints which contains cartesian positions and
# also contains split configuration. Config contains user
# input on how he/she wishes the graphs to be drawn
def drawGraph(x, y, groupNames, config):

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
                if x[plotIndex][p][1] == pos[0] and y[plotIndex][p][1] == pos[1]:
                    # FIX: p doesn't point to same point in x and dataPoints
                    # fix with this p = len(x[plotIndex]) + p
                    text = "x-value: " + str(pos[0]) + "\ny-value: " + str(pos[1]) + "\n"
                    pointID = x[plotIndex][p][0]
                    text += printInformation(pointID)
                    break
        else:
            for p in range(len(x)):
                if x[p] == pos[0] and y[p] == pos[1]:
                    text =  "x-value: " + str(pos[0]) + "\ny-value: " + str(pos[1]) + "\n"
                    text += printInformation(p)
                    break
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.2)

    def printInformation(ID):
        global pointInformation
        global xaxisChoice
        # pointInformation = [[pointID, infoArray], [pointID, infoArray], ...]

        # find the point
        for i in pointInformation:
            if i[0] == ID:
                info = i[1]

        string = ""
        # parse the info
        info = list(info)
        xaxisChoice.reverse()
        for i in range(len(xaxisChoice)):
            string += xaxisChoice[i] + ": " + info[i] + "\n"

        return string

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

    global nPoints
    pointSize=250/(nPoints)**0.35
    sc = []
    # if we use splits or config[1] then color different plots
    if numOfSplits > 1 or config[1]:
        for i in range(len(x)):

            # order points so that plotted properly
            # tmpX and tmpY arrays will contain only floating points
            # of both dependent and indenpendent variables
            tmpX = []; tmpY = []
            lenX = len(x[i]); lenY = len(y[i])
            assert(lenX == lenY)
            for k in range(lenX):
                tmpX.append(x[i][k][1])
                tmpY.append(y[i][k][1])
            tmpX, tmpY = order(tmpX, tmpY)

            if showlegend:
                if config[2] == 1:
                    sc.append(plt.plot(tmpX, tmpY, label=groupNames[i]))
                else:
                    sc.append(plt.scatter(tmpX, tmpY, label=groupNames[i]))
            else:
                if config[2] == 1:
                    sc.append(plt.plot(tmpX, tmpY))
                else:
                    sc.append(plt.scatter(tmpX, tmpY, s=pointSize))
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
    global som_name
    plt.title(som_name)
    plt.show()
    fig.canvas.mpl_disconnect(cid)

def group_data(dataPoints, config):
    # if we have chosen to split then plot multiple graphs
    global numOfSplits
    global splitNames
    global regression
    x = []; y = []; group = []
    if numOfSplits > 1 or config[1]:
        global axisPos
        for p in dataPoints:
            # collect different x,y's of each split value, excluding xaxis
            # s will be the str concat of all splitIndentifies from json2points()
            s = ""
            for i in range(numOfSplits):
                if i in axisPos:
                    # if we used branch list (assuming this is also xaxis value)
                    # or we branch was other option field
                    # then dont continue as we want to color different branches
                    if config[1] == 0:
                        continue
                if regression:
                    s += p[3] + "\n"
                else:
                    s += str(p[i+3]) + "\n"
            try:
                position = group.index(s)
                x[position].append((p[0], p[1]))
                y[position].append((p[0], p[2]))
            except:
                # didnt match
                group.append(s)
                x.append([]); y.append([])

    elif numOfSplits == 1:
        for p in dataPoints:
            x.append(p[1])
            y.append(p[2])

    return x, y, group


# Gets data from rage given a url then uses json2points
# to parse data into python structures
def getData(url, config, regre = False):

    initialize()
    global regression
    regression = regre
    global splitChoice
    print(url)
    somID = re.search(r"id=(\d+)", url).group(1)
    if regression:
        splits = re.findall(r'v_branch=(\w+\%?2?\w+\%?2?\w+)&', url)
    else:
        splits = re.findall(r'&f_(\w+)=1', url)
    if splits:
        for i in splits:
            splitChoice.append(i)
            config[1] = 1
    # no splits from gui so default splits
    else:
        splitChoice = ['branch']

    print("SplitChoices: ", splitChoice)

    print("Fetching data........", end='', flush=True)
    global xaxisChoice
    xaxisChoice = re.findall(r'xaxis=(\w+)', url)
    dir = os.getcwd()
    # catch exception that wget fails (or maybe rage unavailable)
    if os.name == "posix":
        os.system("wget -q \"" + str(url)+ "\" -O /tmp/somdata" + str(somID))
    if os.name == "nt":
        response = requests.get(str(url))
        response.raise_for_status()
        with open(dir + "\\somdata" + str(somID), "w+") as h:
            h.write(str((response.content).decode('utf-8')))
    if os.name == "posix":
        raw = open("/tmp/somdata" + str(somID))
    if os.name == "nt":
        raw = open(dir + "\\somdata" + str(somID))
    print("COMPLETE")
    print("Parsing JSON data.........", end='', flush=True)
    points = json2points(raw)
    if not points:
        return None

    # Get som name
    if os.name == "posix":
        p1 = subprocess.Popen(["curl", "-s", "http://rage/?som=" + str(somID)], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "som_name"], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        o = p2.communicate()[0]
        global som_name
        som_name = re.search(r'som_name\'>([\w+\s+\(\)]+)', str(o)).group(1)

    print("COMPLETE")

    return points

# Main entry point for the tinker program
def tinkerEntryPoint(url, config):

    p = getData(url, config, False)
    x, y, groupNames = group_data(p, config)
    print("Plotting data.........")
    drawGraph(x, y, groupNames, config)
