from tkinter import *
from tkinter import ttk
import os
import re
from multiprocessing import Process

import terroriser

root = Tk()
root.title("Terroriser")
root.geometry("500x300")

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

soms = {"Duration of nth VM clone" : 266,
        "Total duration of VM clones" : 33,
        "Duration of joining domain" : 458}
xaxis = {"branch": 0,
         "product": 1,
         "build_number": 2,
         "build_date": 3,
         "build_tag":4,
         "job_id": 5}

# Inserts dict key,value pairs to a listbox
def insertListOptions(lbox, dict):
    if lbox == None:
        return
    for k in dict.keys():
        v = dict.get(k)
        lbox.insert(v, k)

class App():
    def __init__(self):
        self.content = ttk.Frame(root)
        ttk.Style().theme_use('clam')
        self.checkbar = CheckBar(root, [])
        self.checkbar.grid(column=1, row=0)
        self.listbox = Listbox(root, exportselection=0, width=50)
        insertListOptions(self.listbox, soms)
        self.listbox.grid(column=0, row=0)
        self.listbox.bind("<Double-Button-1>", self.onDouble)

        self.splits = []

        self.xaxisList = Listbox(root, selectmode=MULTIPLE, exportselection=0, width=40)
        insertListOptions(self.xaxisList, xaxis)
        self.xaxisList.grid(column=0, row=1)

        self.label_message = StringVar()
        self.label_message.set("")
        self.info_box = Label(root, textvariable=self.label_message,height=4, width=5, padx=5, pady=5)
        self.info_box.grid(column=0, row=2, sticky='NSWE')

        graphButton = ttk.Button(root, text="Graph", command=okEvent)
        cancelButton = ttk.Button(root, text="Quit", command=root.destroy)

        graphButton.place(relx=0.5, rely=1.0, anchor=SE)
        cancelButton.place(relx=1.0, rely=1.0, anchor=SE)

    def onDouble(self, event):
        somID = soms.get(frame.listbox.get(frame.listbox.curselection()))
        frame.checkbar.clear()
        self.splits = findSplits(somID)
        frame.checkbar.update(self.splits)

def okEvent():

    options = ""
    checkbarStates = frame.checkbar.vars
    listSelected = frame.listbox.curselection()
    if not listSelected:
        return
    # parse xaxisList selection
    for i in frame.xaxisList.curselection():
        options += "&xaxis=" + frame.xaxisList.get(i)

    somID = soms.get(frame.listbox.get(listSelected))
    frame.label_message.set("Graphing data for SOM: " + str(somID))
    j = 0

    for state in checkbarStates:
        if state.get() == 1:
            # checkbox has been ticked
            print(j)
            options += "&f_" + frame.splits[j]
        j = j + 1
    url = "http://rage/?p=som_data&id=" + str(somID) + options
    p = Process(target=terroriser.analyseData(url), args=(url,))
    p.start()
    p.join()

if __name__=="__main__":
    frame = App()
    root.mainloop()
