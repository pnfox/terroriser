from tkinter import *
from tkinter import ttk
import os
import re
import requests
from multiprocessing import Process
from json import JSONDecodeError

import terroriser

tmpFiles = []

COLOR = "grey86"
COLOR2 = "black"

def getRagePage(id):
   
    if id == 0 or id == None:
        raise ValueError("Incorrect SOM ID")
    
    print("Getting rage page http://rage/?som=" + str(id))
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
    
    print("Finding more useful options from rage page")
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
                v = re.match(r'<option value=\'([^\']*)\'', line)
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
           chk = Checkbutton(self, text=pick, variable=var, bg="cyan")
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
diskconc2 = {"Aggregate disk thoughput" : 389,
             "Disk throughput" : 390,
             "Maximum agg disk throughput" : 453,
             "Aggregate IOPS" : 454,
             "Min agg disk throughput single block-size" : 500}
lmbench = {"Simple syscall" : 41,
           "Simple read" : 42,
           "Simple write" : 43,
           "Simple stat" : 44,
           "Simple fstat" : 45,
           "Simple open/close" : 46,
           "Signal handler installation" : 47,
           "Signal handler overhead" : 48,
           "Protection fault" : 49,
           "Pipe latency" : 50,
           "Pipe bandwidth" : 66,
           "AF_UNIX sock stream latency" : 51,
           "AF_UNIX sock stream bandwidth" : 65,
           "Process fork+exit" : 52,
           "Process fork+execve" : 53,
           "Process fock+/bin/sh -c" : 54,
           "Float bogomflops" : 55,
           "Double bogomflops" : 56,
           "File /local/scratch/XXX write bandwidth" : 57,
           "Pagefaults on /local/scratch/XXX" : 58,
           "UDP latency using localhost" : 59,
           "TCP latency using localhost" : 60,
           "61 RPC/udp latency using localhost" : 61,
           "RPC/tcp latecy using localhost" : 62,
           "TCP/IP connection cost to localhost" : 63,
           "Average transfer" : 64,
           "TLB size" : 67,
           "Select on X fds" : 68,
           "Select on X TCP fds" : 69,
           "Filesystem latency (create ops per second)" : 70,
           "Filesystem latency (delete ops per second)" : 71,
           "Sock bandwidth using localhost" : 72,
           "Read bandwidth" : 73,
           "Read open2close bandwidth" : 74,
           "Mmap read bandwidth" : 75,
           "Mmap read open2close bandwidth" : 76,
           "Libc bcopy unaligned" : 77,
           "Libc bcopy aligned" : 78,
           "Memory read bandwidth" : 82,
           "Memory write bandwidth" : 84,
           "Integer op" : 90,
           "Int64 op" : 91,
           "Float op" : 92,
           "Double op" : 93,
           "Integer op parallelism" : 94,
           "Int64 op parallelism" : 95,
           "Float op parallelism" : 96,
           "Double op parallelism" : 97,
           "Steam2 latency" : 99,
           "Stream2 bandwidth" : 101} 


soms = {"VM clone" : vmclone,
        "Active Directory operations" : actDir,
        "Apachebench" : apache,
        "Blackwidow" : blackw,
        "Diskconc2" : diskconc2,
        "Lmbench" : lmbench}
xaxis = {"branch": 0,
         "product": 1,
         "build_number": 2,
         "build_date": 3,
         "build_tag":4,
         "job_id": 5}
somTypes = ["VM clone", "Active Directory operations", "Apachebench", "Blackwidow", "Diskconc2", "Lmbench"]

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

class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Terroriser")
        self.configure(background=COLOR)
        self.content = ttk.Frame(self).grid(column=0,row=0)
        ttk.Style().theme_use('clam')

        self.somTypeSelected = StringVar()
        self.somTypeSelected.set(somTypes[0])
        self.somTypesDropDown = OptionMenu(self.content, self.somTypeSelected, *somTypes, command=self.getSelection)
        self.somTypesDropDown.config(width=20)
        self.somTypesDropDown.grid(column=0, row=2, padx=20, sticky="EW")
        self.somTypesDropDown.tk_setPalette(background=COLOR)
        
        checkbarFrame = ttk.Frame(self.content)
        self.checkbar = CheckBar(checkbarFrame, [])
        checkbarFrame.grid(column=3, row=3)
        self.somListbox = Listbox(self.content, exportselection=0, width=30, foreground=COLOR2)
        self.somListbox.grid(column=1, row=2, sticky=W)
        self.somListbox.bind("<Double-Button-1>", self.onDouble)
        self.somListbox.bind("<Button-1>", self.disableUI)
        self.somListbox.bind("<Button-3>", self.deselect)
        
        Label(self.content, text="Xaxis:").grid(column=0, row=5)
        self.xaxisList = Listbox(self.content, selectmode=MULTIPLE, exportselection=0, width=30, height=5, background=COLOR, foreground=COLOR2)
        insertListOptions(self.xaxisList, xaxis)
        self.xaxisList.grid(column=1, row=5, sticky=W)

        Label(self.content, text="SOM number:", background=COLOR, foreground=COLOR2).grid(column=0,row=1)
        self.somNumber = Entry(self.content, width=30 ,bd=2)
        self.somNumber.grid(column=1, row=1)
        self.somNumber.bind("<Button-1>", self.disableUI)

        Label(self.content, text="URL: ", background=COLOR, foreground=COLOR2).grid(column=0, row=0)
        self.url = Entry(self.content, width=30, bd=2)
        self.url.grid(column=1, row=0)
        self.url.bind("<Button-1>", self.disableUI)

        #splitsButton = Button(leftFrame, text="Update GUI", command=updateSplits, bg=COLOR, fg=COLOR2)
        #splitsButton.grid(column=1, row=2)

        self.label_message = StringVar()
        self.label_message.set("")
        self.info_box = Label(self.content, textvariable=self.label_message,height=4, width=5, padx=5, pady=5, bg=COLOR, fg=COLOR2)
        self.info_box.grid(column=1, row=9, columnspan=2, sticky='NSWE')

        Label(self.content, text="Show legend:", background=COLOR, foreground=COLOR2).grid(column=7, row=8)
        self.legend = IntVar()
        self.legendOption = Checkbutton(self.content, variable=self.legend)
        self.legendOption.grid(column=8,row=8)

        Label(self.content, text="Line plot: ", background=COLOR, foreground=COLOR2).grid(column=7, row=9)
        self.linePlot = IntVar()
        line = Checkbutton(self.content, variable=self.linePlot, bg=COLOR, fg=COLOR2).grid(column=8, row=9)

        Label(self.content, text="Branch:", background=COLOR, foreground=COLOR2).grid(column=0,row=4)
        self.branchList = Listbox(self.content, selectmode=MULTIPLE, exportselection=0, width=30, height=3, bg=COLOR, fg=COLOR2)
        insertListOptions(self.branchList, [])
        self.branchList.grid(column=1, row=4)
        Label(self.content, text="Other option:", background=COLOR, foreground=COLOR2).grid(column=0, row=6)
        self.optionName = Entry(self.content, bd=2, bg=COLOR, fg=COLOR2)
        self.optionValue = Entry(self.content, bd=2, bg=COLOR, fg=COLOR2)
        self.optionName.grid(column=1, row=6)
        self.optionValue.grid(column=2, row=6)

        resetButton = Button(self.content, bg=COLOR, fg=COLOR2, text="Reset", command=reset)
        graphButton = Button(self.content, bg=COLOR, fg=COLOR2, text="Graph", command=okEvent)
        cancelButton = Button(self.content, bg=COLOR, fg=COLOR2, text="Quit", command=self.destroy)

        graphButton.grid(column=7, row=10, sticky=E)
        resetButton.grid(column=8, row=10, sticky=E)
        cancelButton.grid(column=9,row=10, sticky=E)

    def onDouble(self, event):
        updateSplits()
        self.label_message.set("")
        
    def getSelection(self, event):
        self.somTypeSelected.get()
        # update somListBox entries
        self.somListbox.delete(0, self.somListbox.size()-1)
        s = soms.get(self.somTypeSelected.get())
        insertListOptions(self.somListbox, s)
     
    def deselect(self, event):
        for i in self.somListbox.curselection():
            self.somListbox.select_clear(i)
        if event:
            root.disableUI(None)
        
    # If URL is used then dont let user use somID Entry box or categoriesDropDown
    def disableUI(self, event):
        url = self.url.get()
        somID = self.somNumber.get()
        category = self.somListbox.curselection()
        if url:
            self.somNumber['state'] = DISABLED
            self.somTypesDropDown['state'] = DISABLED
            self.somListbox['state'] = DISABLED
            self.deselect(None)
        elif somID:
            self.url['state'] = DISABLED
            self.somTypesDropDown['state'] = DISABLED
            self.somListbox['state'] = DISABLED
            self.deselect(None)
        elif category:
            self.url['state'] = DISABLED
            self.somNumber['state'] = DISABLED
        else:
            self.url['state'] = NORMAL
            self.somNumber['state'] = NORMAL
            self.somTypesDropDown['state'] = NORMAL
            self.somListbox['state'] = NORMAL

def reset():
    root.checkbar.clear()
    root.somListbox.delete(0, root.somListbox.size()-1)
    root.url.delete(0, len(root.url.get()))
    root.somNumber.delete(0, len(root.somNumber.get()))
    root.branchList.delete(0, 'end')
    root.optionName.delete(0, 'end')
    root.optionValue.delete(0, 'end')
    
def getOptions():
    options = ""
    checkbarStates = root.checkbar.vars
    j = 0
    for state in checkbarStates:
        if state.get() == 1:
            # checkbox has been ticked
            options += "&f_" + root.splits[j] + "=1"
        j = j + 1
    return options

def okEvent():
    options = ""
    somID = None
    listSelected = root.somListbox.curselection()
    url = root.url.get()
    id = None
    try:
        id = root.somNumber.get()
        if id:
            id = int(id)
    except: ValueError:
        root.label_message.set("Som number must be int")
    if (url and id) or (id and listSelected) or (url and listSelected):
        root.label_message.set("Confused!\n More than one som number found")
        return

    # parse xaxisList selection
    for i in root.xaxisList.curselection():
        options += "&xaxis=" + root.xaxisList.get(i)

    # parse branch listbox
    for i in root.branchList.curselection():
        branch = root.branchList.get(i).replace("/", "%2F")
        options += "&v_branch=" + branch

    # parse other option textbox fields
    optionName = root.optionName.get()
    optionValue = root.optionValue.get()
    if optionName and optionValue:
        for i in optionValue.split(","):
            i = i.replace("/", "%2F")
            options += "&v_" + optionName + "=" + i

    if url:
        # we use url from url TextBox, check validation
        if not re.match(r'http://rage/\?(som|t)=', url):
            root.label_message.set("Invalid url provided")
            return
        else:
            url = parseTinyUrl(url)
            if url:
                root.label_message.set("Using raw url")
            else:
                return
            url = url + getOptions()
    # if we used somID textbox
    elif id and isinstance(id, int):
        somID = id
        url = "http://rage/?p=som_data&id=" + str(somID) + getOptions() + options
    elif listSelected:
        tmpDict = soms.get(root.somTypeSelected.get())
        somID = tmpDict.get(root.somListbox.get(listSelected))
        if not somID:
            return
        root.label_message.set("Graphing data for SOM: " + str(somID))
        url = "http://rage/?p=som_data&id=" + str(somID) + options + getOptions()
    else:
        root.label_message.set("Nothing to graph")
        return

    config = [root.legend.get(), 0, root.linePlot.get()]
    if root.branchList.curselection() or optionName == "branch":
        config[1] = 1

    try:
        # start graphing
        root.label_message.set("Starting to graph")
        p = Process(target=terroriser.analyseData(url, config), args=(url, config, ))
        p.start()
        p.join()
        root.label_message.set("")
        # TODO: catch process error code for better error logging
    except JSONDecodeError as e:
        print(e)
        root.label_message.set("Failed to parse JSON")
    except terroriser.TerroriserError as e:
        root.label_message.set(e)
    except e:
        print(e)
        root.label_message.set("Failed to graph")

    global tmpFiles
    if somID:
        tmpFiles.append("/tmp/somdata" + str(somID))

def updateSplits():
 
    root.label_message.set("Getting available branches")
    somID = None
    tmpDict = soms.get(root.somTypeSelected.get())
    category = tmpDict.get(root.somListbox.get(root.somListbox.curselection()))
    # if we have used Som Number TextBox
    id = root.somNumber.get()
    urlTextInput = root.url.get()
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
                root.label_message.set("Could not update splits")
                return
    elif category:
        somID = category
    
    if not somID:
        root.label_message.set("Could not update splits")
        return
 
    root.splits = findSplits(somID)
    insertListOptions(root.branchList, findBranches(somID))
    if root.splits:
        root.checkbar.clear()
        root.checkbar.update(root.splits)
        
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
        newUrl = "http://rage/?p=som_data&id" + curl.split("'));")[0]
    if failed:
        root.label_message.set("Invalid url provided")
        return None
    return newUrl

def cleanup():
    for file in tmpFiles:
        try:
            if os.name == "posix":
                os.system("rm -f " + file)
        except:
            print("Failed to remove " + file)
    if os.name == "nt":
        os.system("rm somdata*")

if __name__=="__main__":

    assert sys.version_info >= (3,0)
    root = App()
    root.mainloop()
    cleanup()
