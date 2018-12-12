from tkinter import *
from tkinter import ttk
import os
import re
import requests
from multiprocessing import Process
from json import JSONDecodeError

import terroriser

tmpFiles = []

root = Tk()
root.title("Terroriser")
root.geometry("700x600")

def getRagePage(id):
    if os.name == "posix":
        os.system("wget -q http://rage/?som=" + str(id) + " -O /tmp/som" + str(id))
    if os.name == "nt":
        response = requests.get("http://rage/?som=" + str(id))
        response.raise_for_status()

        with open("som" + str(id), "wb") as h:
            for block in response.iter_content(1024):
                h.write(block)

    global tmpFiles
    # analyse html output to find which options are available for splitting
    if os.name == "posix":
        tmpFiles.append("/tmp/som"+str(id))
        somFile = open("/tmp/som"+str(id))
    if os.name == "nt":
        somFile = open("som" + str(id))

    return somFile

#
# Finds the options that we can split by after tc_config_id
#
def findSplits(id):
    somFile = getRagePage(id)

    splits = []
    tcConfigFound = False
    for line in somFile:
        if "v_tc_config_id" in line:
            tcConfigFound = True
        elif tcConfigFound:
            # Start of select option
            if "<select" in line:
                name = re.match(r"<select name=\'v_(\w+)\'", line)
                if name:
                    name=name.group(1)
                    splits.append(name)
    somFile.close()
    # output array or dictionary of options
    return splits

def findBranches(id):
    somFile = getRagePage(id)

    branches = []
    branchFound = False
    for line in somFile:
        if "name=\'v_branch\'" in line:
            branchFound = True
        elif "</select" in line:
            branchFound = False
        elif branchFound:
            if "<option" in line:
                v = re.match(r'<option value=\'(\w+)\'', line)
                if v:
                    v = v.group(1)
                    branches.append(v)
    return branches

class CheckBar(Frame):
    def __init__(self, parent=None, picks=[], side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        self.vars = []
        self.checkboxes = []
        self.update(picks)

    def state(self):
        return map((lambda var: var.get()), self.vars)

    def update(self, picks=[]):
        self.vars = []
        for pick in picks:
           var = IntVar()
           chk = Checkbutton(self, text=pick, variable=var)
           chk.pack()
           self.vars.append(var)
           self.checkboxes.append(chk)
    def clear(self):
        for i in self.checkboxes:
            i.destroy()

vmclone = {"Total duration of VM clones" : 33,
           "Duration of nth VM clone" : 266}
actDir = {"Duration of joining domain" : 458,
          "Duration of leabin domain" : 459,
          "Duration of CLI command" : 460,
          "Duration of SSH command" : 461}
apache = {"Apachebench measurement (per client)" : 308,
          "Apachebench measurements (average across clients)" : 309,
          "Apachebench measurements (median across requests)" : 310,
          "Apachebench measurements (max across requests)" : 465}
blackw = {"HTTP throughput" : 476,
              "HTTP throughput (mean over time)" : 477,
              "HTTP end-to-end" : 479,
              "HTTP end-to-end" : 480,
              "DNS req/sec" : 495,
              "DNS req/sec (mean over time)" : 496,
              "SSL encrypted throughput" : 483,
              "SSL encrypted throughput (mean)" : 484,
              "SSL TPS" : 486,
              "SSL TPS (mean)" : 487,
              "TCP Conn/sec" : 481,
              "TCP Conn/sec (mean)" : 482}


soms = {"VM clone" : vmclone,
        "Active Directory operations" : actDir,
        "Apachebench" : apache,
        "Blackwidow" : blackw}
xaxis = {"branch": 0,
         "product": 1,
         "build_number": 2,
         "build_date": 3,
         "build_tag":4,
         "job_id": 5}
somTypes = ["VM clone", "Active Directory operations", "Apachebench", "Blackwidow"]

# Inserts dict key,value pairs to a listbox
def insertListOptions(lbox, dict):
    if lbox == None or dict == None:
        return
    if type(dict) is type([]):
        k = 0
        for i in dict:
            lbox.insert(k, i)
            k += 1
    else:
        for k in dict.keys():
            v = dict.get(k)
            lbox.insert(v, k)

class App():
    def __init__(self):
        self.content = ttk.Frame(root).grid(column=0,row=0)
        ttk.Style().theme_use('clam')
        rightFrame = ttk.Frame(self.content)
        leftFrame = ttk.Frame(self.content)
        middleFrame = ttk.Frame(self.content)
        bottomFrame = ttk.Frame(self.content)

        self.somTypeSelected = StringVar()
        self.somTypeSelected.set(somTypes[0])
        somTypesOption = OptionMenu(rightFrame, self.somTypeSelected, *somTypes, command=self.getSelection).grid(column=0, row=0)

        Label(rightFrame, text="Double click on som\nto see split options").grid(column=1, row=0)
        self.checkbar = CheckBar(rightFrame, [])
        self.checkbar.grid(column=1, row=1, columnspan=2)
        self.somListbox = Listbox(rightFrame, exportselection=0, width=30)
        self.somListbox.grid(column=0, row=1, sticky=W)
        self.somListbox.bind("<Double-Button-1>", self.onDouble)
        #scrollbar = Scrollbar(rightFrame,orient="vertical", width=20)
        #scrollbar.grid(column=0,row=1, sticky=E)
        #scrollbar.config(command=self.somListbox.yview)
        #self.somListbox.config(yscrollcommand=scrollbar.set)


        self.splits = []

        self.xaxisList = Listbox(rightFrame, selectmode=MULTIPLE, exportselection=0, width=20, height=5)
        insertListOptions(self.xaxisList, xaxis)
        self.xaxisList.grid(column=0, row=2, sticky=W)

        Label(leftFrame, text="SOM number\n(optional):").grid(column=0,row=0)
        self.somNumber = Entry(leftFrame, bd=2)
        self.somNumber.grid(column=1,row=0)

        Label(leftFrame, text="URL\n(optional): ").grid(column=0, row=1)
        self.url = Entry(leftFrame, bd=2)
        self.url.grid(column=1, row=1)

        splitsButton = ttk.Button(leftFrame, text="Update GUI", command=updateSplits)
        splitsButton.grid(column=1, row=2)

        self.label_message = StringVar()
        self.label_message.set("")
        self.info_box = Label(rightFrame, textvariable=self.label_message,height=4, width=5, padx=5, pady=5)
        self.info_box.grid(column=0, row=3, sticky='NSWE')

        Label(leftFrame, text="Show legend:").grid(column=0, row=3)
        self.legend = IntVar()
        self.legendOption = Checkbutton(leftFrame, variable=self.legend)
        self.legendOption.grid(column=1,row=3)

        Label(leftFrame, text="Line plot: ").grid(column=0, row=4)
        self.linePlot = IntVar()
        line = Checkbutton(leftFrame, variable=self.linePlot).grid(column=1, row=4)

        Label(middleFrame, text="Branch:").grid(column=0,row=0)
        self.branchList = Listbox(middleFrame, selectmode=MULTIPLE, exportselection=0, width=20, height=3)
        insertListOptions(self.branchList, [])
        self.branchList.grid(column=0, row=1)
        Label(middleFrame, text="Other option:").grid(column=0, row=2)
        self.optionName = Entry(middleFrame, bd=2)
        self.optionValue = Entry(middleFrame, bd=2)
        self.optionName.grid(column=1, row=2)
        self.optionValue.grid(column=2, row=2)

        resetButton = ttk.Button(bottomFrame, text="Reset", command=reset)
        graphButton = ttk.Button(bottomFrame, text="Graph", command=okEvent)
        cancelButton = ttk.Button(bottomFrame, text="Quit", command=root.destroy)

        graphButton.grid(column=0, row=0)
        resetButton.grid(column=1, row=0)
        cancelButton.grid(column=2,row=0)

        rightFrame.grid(column=0, row=0)
        leftFrame.grid(column=1, row=0)
        middleFrame.grid(column=0, row=1, columnspan=2)
        bottomFrame.grid(column=0, row=2, columnspan=2)

    def onDouble(self, event):
        tmpDict = soms.get(frame.somTypeSelected.get())
        somID = tmpDict.get(frame.somListbox.get(frame.somListbox.curselection()))
        frame.checkbar.clear()
        self.splits = findSplits(somID)
        frame.checkbar.update(self.splits)

    def getSelection(self, event):
        self.somTypeSelected.get()
        # update somListBox entries
        frame.somListbox.delete(0, frame.somListbox.size()-1)
        s = soms.get(self.somTypeSelected.get())
        insertListOptions(frame.somListbox, s)

def reset():
    frame.checkbar.clear()
    frame.somListbox.delete(0, frame.somListbox.size()-1)
    frame.url.delete(0, len(frame.url.get()))
    frame.somNumber.delete(0, len(frame.somNumber.get()))

def getOptions():
    options = ""
    checkbarStates = frame.checkbar.vars
    j = 0
    for state in checkbarStates:
        if state.get() == 1:
            # checkbox has been ticked
            options += "&f_" + frame.splits[j] + "=1"
        j = j + 1
    return options

def okEvent():
    options = ""
    somID = None
    listSelected = frame.somListbox.curselection()
    url = frame.url.get()
    id = frame.somNumber.get()
    if (url and id) or (id and listSelected) or (url and listSelected):
        frame.label_message.set("Confused!\n More than one som number found")
        return

    # parse xaxisList selection
    for i in frame.xaxisList.curselection():
        options += "&xaxis=" + frame.xaxisList.get(i)

    # parse branch listbox
    for i in frame.branchList.curselection():
        branch = frame.branchList.get(i).replace("/", "%2F")
        options += "&v_branch=" + branch

    # parse other option textbox fields
    optionName = frame.optionName.get()
    optionValue = frame.optionValue.get()
    if optionName and optionValue:
        for i in optionValue.split(","):
            i = i.replace("/", "%2F")
            options += "&v_" + optionName + "=" + i

    if url:
        # we use url from url TextBox, check validation
        if not re.match(r'http://rage/\?(som|t)=', url):
            frame.label_message.set("Invalid url provided")
            return
        else:
            url = parseTinyUrl(url)
            if url:
                frame.label_message.set("Using raw url")
            else:
                return
            url = url + getOptions()
    # if we used somID textbox
    elif id:
        somID = id
        url = "http://rage/?p=som_data&id=" + str(somID) + getOptions() + options
    elif listSelected:
        tmpDict = soms.get(frame.somTypeSelected.get())
        somID = tmpDict.get(frame.somListbox.get(listSelected))
        if not somID:
            return
        frame.label_message.set("Graphing data for SOM: " + str(somID))
        url = "http://rage/?p=som_data&id=" + str(somID) + options + getOptions()
    else:
        frame.label_message.set("Nothing to graph")
        return

    config = [frame.legend.get(), 0, frame.linePlot.get()]
    if frame.branchList.curselection() or optionName == "branch":
        config[1] = 1

    try:
        # start graphing
        p = Process(target=terroriser.analyseData(url, config), args=(url, config, ))
        p.start()
        p.join()
        # TODO: catch process error code for better error logging
    except JSONDecodeError as e:
        print(e)
        frame.label_message.set("Failed to parse JSON")
    except terroriser.TerroriserError as e:
        frame.label_message.set(e)
    except e:
        print(e)
        frame.label_message.set("Failed to graph")
    global tmpFiles
    if somID:
        tmpFiles.append("/tmp/somdata" + str(somID))

def updateSplits():
    # if we have used Som Number TextBox
    id = frame.somNumber.get()
    urlTextInput = frame.url.get()
    if id:
        somID = id
    # if we have used url textbox
    elif urlTextInput:
        tmp = re.search(r'som=(\d+)', urlTextInput)
        tmp2 = re.search(r'rage/\?t=(\d+)$', urlTextInput)
        if tmp:
            somID = tmp.group(1)
        elif tmp2:
            somID = re.search(r'&id=(\d+)', parseTinyUrl(urlTextInput))
            if somID:
                somID = somID.group(1)
            else:
                frame.label_message.set("Could not update splits")
                return
    else:
        frame.label_message.set("Could not update splits")
        return
    frame.splits = findSplits(somID)
    insertListOptions(frame.branchList, findBranches(somID))
    if frame.splits:
        frame.checkbar.clear()
        frame.checkbar.update(frame.splits)

def parseTinyUrl(url):
    curl = ""
    t = None
    location = 0
    failed = False
    tmp = re.search(r'rage/\?t=(\d+)$', url)
    if tmp:
        t = tmp.group(1)
    tmp = re.search(r'som=(\d+)(.*)', url)
    if tmp:
        somID = tmp.group(1)
        otherthings = tmp.group(2)
        newUrl = "http://rage/?p=som_data&id=" + str(somID) + otherthings
    if t:
        index = 0
        if os.name == "posix":
            output = os.popen("curl -sL " + url).read().split("%")
        for i in range(len(output)):
            if "som" in output[i]:
                location = i+1
                break
            if "this is not the page you are looking for" in output[i]:
                failed = True
        somID = output[location][2:]

        j = 0
        for i in output[location:len(output)]:
            if "252F" in i or "253D" in i:
                i = i.replace("25", "%")
                index += 1
                curl += i
                continue
            if i[:2] == "3A":
                curl += ":" + i[2:]
                continue
            if i[:2] == "2F":
                curl += "/" + i[2:]
                continue
            if i[:2] == "23":
                curl += "#" + i[2:].split("'")[0]
                continue

            i = i[2:].split("'")[0]
            if j % 2 == 0:
                curl += "="
            else:
                curl += "&"
            curl += i
            index += 1
            j += 1
        newUrl = "http://rage/?p=som_data&id" + curl
    if failed:
        frame.label_message.set("Invalid url provided")
        return None
    return newUrl

def cleanup():
    for file in tmpFiles:
        try:
            if os.name == "posix":
                os.system("rm -f " + file)
        except:
            print("Failed to remove " + file)

if __name__=="__main__":

    assert sys.version_info >= (3,0)
    frame = App()
    root.mainloop()
    cleanup()
