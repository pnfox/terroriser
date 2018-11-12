from tkinter import *
from tkinter import ttk
import os
import re
from multiprocessing import Process

import terroriser

root = Tk()

#
# Finds the options that we can split by after tc_config_id
#
def findSplits(id):
    print("Getting som data and writing to /tmp/som" + str(id))
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
      for pick in picks:
         var = IntVar()
         chk = Checkbutton(self, text=pick, variable=var)
         chk.pack(side=side, anchor=anchor, expand=YES)
         self.vars.append(var)
   def state(self):
      return map((lambda var: var.get()), self.vars)


soms = {"Duration of nth VM clone" : 266,
        "Total duration of VM clones" : 33,
        "Duration of joining domain" : 458}

def insertSomOptions(lbox):
    for k in soms.keys():
        lbox.insert(soms.get(k), k)

class App():
    def __init__(self, splits):
        self.content = ttk.Frame(root)
        ttk.Style().theme_use('clam')
        self.checkbarNames = splits
        self.checkbar = CheckBar(root, self.checkbarNames)
        self.checkbar.grid(column=0, row=0)
        self.listbox = Listbox(root)
        insertSomOptions(self.listbox)
        self.listbox.grid(column=0, row=1)
        self.label_message = StringVar()
        self.label_message = "";
        self.info_box = Label(root, textvariable=self.label_message,height=11, width=50)
        self.info_box.grid(column=0, row=2, sticky='NSWE')
        ok = ttk.Button(root, text="Okay", command=okEvent)
        cancel = ttk.Button(root, text="Cancel")

        ok.place(relx=0.5, rely=1.0, anchor=SE)
        cancel.place(relx=1.0, rely=1.0, anchor=SE)

def okEvent():
    checkbarStates = frame.checkbar.vars
    listSelected = frame.listbox.curselection()
    if not listSelected:
        return

    somID = soms.get(frame.listbox.get(listSelected))
    i = 0
    options = ""
    for state in checkbarStates:
        if state.get() == 1:
            # checkbox has been ticked
            options += "&f_" + frame.checkbarNames[i]
        i += 1
    url = "http://rage/?p=som_data&id=" + str(somID) + options
    #terroriser.analyseData(url)
    p = Process(target=terroriser.analyseData(url), args=(url,))
    p.start()
    p.join()

somID = 266
if __name__=="__main__":
    splitOptions = findSplits(somID)
    frame = App(splitOptions)
    root.mainloop()
