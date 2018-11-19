from tkinter import *
from tkinter import ttk
import os
import re
from multiprocessing import Process

import terroriser

root = Tk()
root.title("Terroriser")
root.geometry("600x400")

#
# Finds the options that we can split by after tc_config_id
#
def findSplits(id):
    os.system("wget -q http://rage/?som=" + str(id) + " -O /tmp/som" + str(id))
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
        self.content = ttk.Frame(root)
        ttk.Style().theme_use('clam')

        self.somTypeSelected = StringVar()
        self.somTypeSelected.set(somTypes[0])
        somTypesOption = OptionMenu(root, self.somTypeSelected, *somTypes, command=self.getSelection).grid(column=0, row=0)

        self.checkbar = CheckBar(root, [])
        self.checkbar.grid(column=1, row=1, columnspan=2)
        self.somListbox = Listbox(root, exportselection=0, width=30)
        self.somListbox.grid(column=0, row=1, sticky=W)
        self.somListbox.bind("<Double-Button-1>", self.onDouble)

        self.splits = []

        self.xaxisList = Listbox(root, selectmode=MULTIPLE, exportselection=0, width=20)
        insertListOptions(self.xaxisList, xaxis)
        self.xaxisList.grid(column=0, row=2, sticky=W)

        self.label_message = StringVar()
        self.label_message.set("")
        self.info_box = Label(root, textvariable=self.label_message,height=4, width=5, padx=5, pady=5)
        self.info_box.grid(column=0, row=3, sticky='NSWE')

        self.legend = IntVar()
        self.legendOption = Checkbutton(root, text="Show legend", variable=self.legend)
        self.legendOption.grid(column=1, row=2, sticky='NSWE', columnspan=2)

        graphButton = ttk.Button(root, text="Graph", command=okEvent)
        cancelButton = ttk.Button(root, text="Quit", command=root.destroy)

        graphButton.place(relx=0.5, rely=1.0, anchor=SE)
        cancelButton.place(relx=1.0, rely=1.0, anchor=SE)

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
    checkbarStates = frame.checkbar.vars
    listSelected = frame.somListbox.curselection()
    if not listSelected:
        return
    # parse xaxisList selection
    for i in frame.xaxisList.curselection():
        options += "&xaxis=" + frame.xaxisList.get(i)

    tmpDict = soms.get(frame.somTypeSelected.get())
    somID = tmpDict.get(frame.somListbox.get(listSelected))
    if somID == None:
        return
    frame.label_message.set("Graphing data for SOM: " + str(somID))
    j = 0

    for state in checkbarStates:
        if state.get() == 1:
            # checkbox has been ticked
            print(j)
            options += "&f_" + frame.splits[j]
        j = j + 1
    url = "http://rage/?p=som_data&id=" + str(somID) + options
    config = [frame.legend.get()]
    try:
        p = Process(target=terroriser.analyseData(url, config), args=(url, config, ))
        p.start()
        p.join()
    except e:
        print(e)
        frame.label_message.set("Failed to graph")

if __name__=="__main__":
    frame = App()
    root.mainloop()
