import os
import re
import json
import operator
import subprocess
import matplotlib.pyplot as plt
import requests
import statistics


class TerroriserError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Terroriser:
    
    def __init__(self):
        self.points = []
        self.nPoints = 0
        self.numOfSplits = 0
        self.axisPos = []
        self.splitNames = []
        self.splitChoice = []
        self.xaxis = ""
        self.yaxis = ""

    # Gets data from rage given a url then uses json2points
    # to parse data into python structures
    def getData(self, regre = False):

        self.regression = regre
        somID = re.search(r"id=(\d+)", self.url).group(1)
        if self.regression:
            splits = re.findall(r'v_branch=(\w+\%?2?\w+\%?2?\w+)&', self.url)
        else:
            splits = re.findall(r'&f_(\w+)=1', self.url)
        if splits:
            for i in splits:
                self.splitChoice.append(i)
                self.config[1] = 1
        # no splits from lib import funs gui so default splits
        else:
            self.splitChoice = ['branch']

        if len(re.findall(r'&v_branch=', self.url)) > 1 and 'branch' not in self.splitChoice:
            self.splitChoice.append('branch')

        # Get som name
        if os.name == "posix":
            p1 = subprocess.Popen(["curl", "-s", "http://rage/?som=" + str(somID)], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(["grep", "som_name"], stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()
            o = p2.communicate()[0]
            self.som_name = re.search(r'som_name\'>([\w+\s+\(\)]+)', str(o)).group(1)

        print("Fetching data.......", end='', flush=True)
        self.xaxisChoice = re.findall(r'xaxis=(\w+)', self.url)
        dir = os.getcwd()
        # catch exception that wget fails (or maybe rage unavailable)
        if os.name == "posix":
            os.system("wget -q \"" + str(self.url)+ "\" -O /tmp/somdata" + str(somID))
        if os.name == "nt":
            response = requests.get(str(self.url))
            response.raise_for_status()
            with open(dir + "\\somdata" + str(somID), "w+") as h:
                h.write(str((response.content).decode('utf-8')))
        if os.name == "posix":
            raw = open("/tmp/somdata" + str(somID))
        if os.name == "nt":
            raw = open(dir + "\\somdata" + str(somID))
        print("COMPLETE")
        print("Parsing JSON data......", end='', flush=True)
        self.points = json2points(self, raw)

        if not self.points:
            print("No data found")
            raise TerroriserError("No data found")

        print("COMPLETE")
        return self.points

    def groupData(self):
        # if we have chosen to split then plot multiple graphs
        x = []; y = []; group = []
        if self.numOfSplits > 1 or self.config[1]:
            for p in self.points:
                # collect different x,y's of each split value, excluding xaxis
                # s will be the str concat of all splitIndentifies from json2points()
                s = ""
                for i in range(self.numOfSplits):
                    if i in self.axisPos:
                        # if we used branch list (assuming this is also xaxis value)
                        # or we branch was other option field
                        # then dont continue as we want to color different branches
                        if self.config[1] == 0:
                            continue
                    if self.regression:
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
                    x.append([(p[0], p[1])]); y.append([(p[0], p[1])])

        elif self.numOfSplits == 1:
            for p in self.points:
                x.append(p[1])
                y.append(p[2])

        return x, y, group

# End of Terroriser class
 
def json2points(t, f):
    json_data=f.read()
    if len(json_data.split()) == 0:
        return None
    # will return exception when cant parse json
    # data is a python dict
    data = json.loads(json_data)
    xlabels = data.get("x_labels")
    t.xaxis = data.get("xaxis")
    t.yaxis = data.get("yaxis")
    series = data.get("series")
    if not series:
        raise TerroriserError("No data in RAGE, old jobs")

    for i in range(len(series)):
         for p in series[i].get("data"):
             t.points.append(p)
    t.splitNames = list(t.points[0][2].keys())
    # splitChoice contains the values of &f_(\w+)= in the url 
    t.numOfSplits = len(t.splitChoice)

    # xaxis branch is selected by user but
    # position of branch values in points.keys() is undetermined
    # this finds the position, we need this later
    for x in t.xaxis.split(","):
        position = list(t.points[0][2].keys()).index(x)
        if position:
            t.axisPos.append(position)

    results = []
    t.pointInformation = []
    # find split options in json
    j = 0
    for i in t.points:
        results.append([j, i[0], i[1]])
        dict = i[2]
        t.pointInformation.append([j, dict.values()])
        # Add the splitByIdentifier, used later to determine color
        if not t.splitChoice:
            for v in dict.values():
                results[j].append(v)
        else:
            if t.regression:
                results[j].append(dict.get("branch"))
            else:
                for split in t.splitChoice:
                    results[j].append(dict.get(split))
        j = j + 1
    t.nPoints = j

    # results = [xvalue, yvalue, splitByIdentifier]
    return results

# Used to order two arrays a, b when each entry in both
# corresponds to a pair (a[0] is with b[0], etc...)
# orders based on a in ascending order
# returns ordered arrays a, b
def order(a, b=None):
    map = []
    if type(a) is list and type(a[0]) is list and b == None:
       # input list A was in the form a[0] = [x[0], y[0]]
       # which is what we want. Change a and b to be lists of ints
       map = a
       a = [0]; b = [0]
       a = a * len(map)
       b = b * len(map)
    # if two lists of ints or floats is passed
    elif len(a) == len(b):
        for i in range(len(a)):
            map.append([a[i],b[i]])

    map = sorted(map)
    k = 0
    for i in map:
        a[k] = i[0]
        b[k] = i[1]
        k += 1

    return a, b

# Given two lists we find the average point
# if we have multiple points on a single x[i]
# i.e. we have a straight vertical line in our plot
# then find the mean average
#
# returns coordinates of points representing the average
def findAverage(x, y):
    assert(len(x)==len(y))
    l = []
    for i in range(len(x)):
        l.append([x[i], y[i]])

    uniqueX = set(map(lambda i:i[0], l))
    newlist = [[j[1] for j in l if j[0]==i] for i in uniqueX]

    l = []
    for group in newlist:
        if len(group) > 2:
            avg = statistics.median(group)
            xlocation = x[y.index(group[0])]
            l.append([xlocation, avg])

    return l

# Given the dataPoints which contains cartesian positions and
# also contains split configuration. Config contains user
# input on how he/she wishes the graphs to be drawn
def drawGraph(t, x, y, groupNames, config):

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
                    text = "x-value: " + str(pos[0]) + "\ny-value: " + str(pos[1])
                    pointID = x[plotIndex][p][0]
                    text += printInformation(pointID)
                    break
        else:
            for p in range(len(x)):
                if x[p] == pos[0] and y[p] == pos[1]:
                    text =  "x-value: " + str(pos[0]) + "\ny-value: " + str(pos[1])
                    text += printInformation(p)
                    break
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.2)

    def printInformation(ID):
        # pointInformation = [[pointID, infoArray], [pointID, infoArray], ...]

        # find the point
        for i in t.pointInformation:
            if i[0] == ID:
                info = i[1]

        string = ""
        # parse the info
        info = list(info)
        t.xaxisChoice.reverse()
        for i in range(len(t.xaxisChoice)):
            string += t.xaxisChoice[i] + ": " + info[i] + "\n"

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

    def plotAvg(xOfAvg, avg, label=None, line=False):
        if line:
            plt.plot(xOfAvg, avg, label=label)
        else:
            plt.plot(xOfAvg, avg, marker="x", ms=10, mec='black', mfc='black', label=label)

    pointSize=250/(t.nPoints)**0.35
    sc = []
    # if we use splits or config[1] then color different plots
    if t.numOfSplits > 1 or config[1]:
        for i in range(len(x)):

            # order points so that plotted properly
            # tmpX and tmpY arrays will contain only floating points
            # of both dependent and indenpendent variables
            tmpX = []; tmpY = []
            lenX = len(x[i]); lenY = len(y[i])
            assert(lenX == lenY)
            for k in range(lenX):
                assert(len(x[i][k]) == 2)
                assert(type(x[i][k]) is tuple)
                assert(type(x[i][k][1]) is int)
                tmpX.append(x[i][k][1])
                tmpY.append(y[i][k][1])
            tmpX, tmpY = order(tmpX, tmpY)

            if showlegend:
                if config[5] == 1:
                    xOfAvg, avg = order(findAverage(tmpX, tmpY))
                    plotAvg(xOfAvg, avg, label=groupNames[i], line=True)
                    continue
                elif config[2] == 1:
                    plot = plt.plot(tmpX, tmpY, label=groupNames[i])
                    sc.append(plt.scatter(tmpX, tmpY, label=None, color=plot[-1].get_color()))
                if config[2] == 0:
                    sc.append(plt.scatter(tmpX, tmpY, label=groupNames[i]))
            else:
                if type(tmpX[0]) is list:
                    print("tmpX[0][0]: ", tmpX[0][0])
                    if type(tmpX[0][0]) is list:
                        print("tmpX[0][0][0]: ", tmpX[0][0][0])
                if config[5] == 1:
                    xOfAvg, avg = order(findAverage(tmpX, tmpY))
                    plotAvg(xOfAvg, avg, line=True)
                    continue
                elif config[2] == 1:
                    plot = plt.plot(tmpX, tmpY, label=groupNames[i])
                    sc.append(plt.scatter(tmpX, tmpY, label=None, color=plot[-1].get_color()))
                if config[2] == 0:
                    sc.append(plt.scatter(tmpX, tmpY, s=pointSize))
            if config[4] == 1:
                xOfAvg, avg = order(findAverage(tmpX, tmpY))
                plotAvg(xOfAvg, avg)

    # no color used
    else:
        x, y = order(x,y)
        if config[2] == 1:
            sc.append(plt.plot(x,y))
        if config[2] == 0:
            sc.append(plt.scatter(x,y, s=pointSize))
        if config[5] == 1:
            xOfAvg, avg = order(findAverage(x, y))
            plotAvg(xOfAvg, avg, line=True)
        elif config[4] == 1:
            xOfAvg, avg = order(findAverage(x, y))
            plotAvg(xOfAvg, avg)

    plt.xlabel(t.xaxis)
    plt.ylabel(t.yaxis)
    cid = fig.canvas.mpl_connect("button_press_event", onclick)

    if config[3] == 1:
        ax.set_ylim(bottom=0)
    if showlegend:
        plt.legend()
    plt.title(t.som_name)
    try:
        print("COMPLETE")
        plt.show()
        fig.canvas.mpl_disconnect(cid)
    except e:
        raise TerroriserError("Couldn't plot graph")

# Main entry point for the tinker program
def tinkerEntryPoint(GUI, url, config):

    terroriser = Terroriser()
    terroriser.url = url
    terroriser.config = config
    print(url)
    GUI.log("Getting data...")
    terroriser.getData(False)
    x, y, groupNames = terroriser.groupData()
    GUI.log("Graphing...")
    print("Plotting data.........", end='', flush=True)
    drawGraph(terroriser, x, y, groupNames, config)
    return
