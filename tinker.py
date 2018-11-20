from tkinter import *
from tkinter import ttk
import os
import re
from multiprocessing import Process
from json import JSONDecodeError

import terroriser

tmpFiles = []

root = Tk()
root.title("Terroriser")
root.geometry("700x400")

#
# Finds the options that we can split by after tc_config_id
#
def findSplits(id):
    os.system("wget -q http://rage/?som=" + str(id) + " -O /tmp/som" + str(id))
    global tmpFiles
    tmpFiles.append("/tmp/som"+str(id))
    # analyse html output to find which options are available for splitting
    somFile = open("/tmp/som"+str(id))
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
    # output array or dictionary of options
    return splits

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
              "DNS req/sec" : 495,
              "DNS req/sec (mean over time)" : 496}

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
    for k in dict.keys():
        v = dict.get(k)
        lbox.insert(v, k)

class App():
    def __init__(self):
        self.content = ttk.Frame(root).grid(column=0,row=0)
        ttk.Style().theme_use('clam')
        topFrame = ttk.Frame(self.content)
        sideFrame = ttk.Frame(self.content)
        bottomFrame = ttk.Frame(self.content)

        self.somTypeSelected = StringVar()
        self.somTypeSelected.set(somTypes[0])
        somTypesOption = OptionMenu(topFrame, self.somTypeSelected, *somTypes, command=self.getSelection).grid(column=0, row=0)

        Label(topFrame, text="Double click on som\nto see split options").grid(column=1, row=0)
        self.checkbar = CheckBar(topFrame, [])
        self.checkbar.grid(column=1, row=1, columnspan=2)
        self.somListbox = Listbox(topFrame, exportselection=0, width=30)
        self.somListbox.grid(column=0, row=1, sticky=W)
        self.somListbox.bind("<Double-Button-1>", self.onDouble)

        self.splits = []

        self.xaxisList = Listbox(topFrame, selectmode=MULTIPLE, exportselection=0, width=20, height=5)
        insertListOptions(self.xaxisList, xaxis)
        self.xaxisList.grid(column=0, row=2, sticky=W)

        Label(sideFrame, text="SOM number\n(optional):").grid(column=0,row=0)
        self.somNumber = Entry(sideFrame, bd=2)
        self.somNumber.grid(column=1,row=0)

        Label(sideFrame, text="URL\n(optional): ").grid(column=0, row=1)
        self.url = Entry(sideFrame, bd=2)
        self.url.grid(column=1, row=1)

        self.label_message = StringVar()
        self.label_message.set("")
        self.info_box = Label(topFrame, textvariable=self.label_message,height=4, width=5, padx=5, pady=5)
        self.info_box.grid(column=0, row=3, sticky='NSWE')

        Label(sideFrame, text="Show legend:").grid(column=0, row=2)
        self.legend = IntVar()
        self.legendOption = Checkbutton(sideFrame, variable=self.legend, height=4, width=5)
        self.legendOption.grid(column=1,row=2)

        graphButton = ttk.Button(bottomFrame, text="Graph", command=okEvent)
        cancelButton = ttk.Button(bottomFrame, text="Quit", command=root.destroy)

        graphButton.grid(column=0, row=0)
        cancelButton.grid(column=1,row=0)

        topFrame.grid(column=0, row=0)
        sideFrame.grid(column=1, row=0)
        bottomFrame.grid(column=0, row=1, columnspan=2)

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

def okEvent():

    options = ""
    somID = None
    checkbarStates = frame.checkbar.vars
    listSelected = frame.somListbox.curselection()
    url = frame.url.get()
    id = frame.somNumber.get()
    # parse xaxisList selection
    for i in frame.xaxisList.curselection():
        options += "&xaxis=" + frame.xaxisList.get(i)

    if url:
        # we use url from url TextBox, check validation
        if not re.match(r'http://rage/\?(som|t)=', url):
            frame.label_message.set("Invalid url provided")
            return
        else:
            url = parseUrl(url)
            if not url:
                frame.label_message.set("Using raw url")
    elif id:
        somID = id
        url = "http://rage/?p=som_data&id=" + str(somID)
    elif listSelected:
        tmpDict = soms.get(frame.somTypeSelected.get())
        somID = tmpDict.get(frame.somListbox.get(listSelected))
        if not somID:
            return
        frame.label_message.set("Graphing data for SOM: " + str(somID))
        j = 0

        for state in checkbarStates:
            if state.get() == 1:
                # checkbox has been ticked
                options += "&f_" + frame.splits[j]
            j = j + 1
        url = "http://rage/?p=som_data&id=" + str(somID) + options
    else:
        return

    config = [frame.legend.get()]
    try:
        # start graphing
        p = Process(target=terroriser.analyseData(url, config), args=(url, config, ))
        p.start()
        p.join()
        # TODO: catch process error code for better error logging
    except JSONDecodeError:
        frame.label_message.set("Invalid SOM number")
    except:
        frame.label_message.set("Failed to graph")
    global tmpFiles
    if somID:
        tmpFiles.append("/tmp/somdata" + str(somID))

def parseUrl(url):
    somID = re.search(r'som=(\d+)', url).group(1)
    if not somID:
        frame.label_message.set("Invalid url provided")
        return None

    newUrl = "http://rage/?p=som_data&id=" + str(somID)
    return newUrl

def cleanup():
    for file in tmpFiles:
        try:
            os.system("rm -f " + file)
        except:
            print("Failed to remove " + file)

if __name__=="__main__":
    frame = App()
    root.mainloop()
    cleanup()
