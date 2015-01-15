#!/usr/bin/python3
from tkinter import *
from tkinter.ttk import *

root = Tk()
Style().theme_use("clam")

frmTop = Frame(root)
frmTop.pack(side=TOP, fill=BOTH)

frmLeft = Frame(frmTop)
frmLeft.pack(side=LEFT, fill=BOTH)

frmCampaigns = Frame(frmLeft)
frmCampaigns.pack(side=TOP, fill=BOTH, expand=YES)

sbCampaigns = Scrollbar(frmCampaigns)
sbCampaigns.pack(side=RIGHT, fill=Y)
lbCampaigns = Listbox(frmCampaigns, yscrollcommand=sbCampaigns.set)
lbCampaigns.pack(side=LEFT, fill=BOTH, expand=YES)
sbCampaigns.config(command=lbCampaigns.yview)

for num in range(0, 10):
	lbCampaigns.insert(END, "Campaign {0}".format(num))

lbCampaigns.itemconfig(1, fg="#AAAAAA")

frmCampaignsSL = Frame(frmLeft)
frmCampaignsSL.pack(side=BOTTOM)

btnSave = Button(frmCampaignsSL, text="Save")
btnSave.pack(side=LEFT)

btnLoad = Button(frmCampaignsSL, text="Load")
btnLoad.pack(side=LEFT)

btnDelete = Button(frmCampaignsSL, text="Delete")
btnDelete.pack(side=LEFT)

frmDetails = Frame(frmTop, height=500, width=500)
frmDetails.pack_propagate(0)
frmDetails.pack(side=RIGHT, fill=X, expand=YES)

frmBottom = Frame(root)
frmBottom.pack(side=BOTTOM, fill=X)

frmControls = Frame(frmBottom)
frmControls.pack(side=LEFT)

btnStart = Button(frmControls, text="Start")
btnStart.pack(side=TOP)

btnStop = Button(frmControls, text="Stop")
btnStop.pack(side=TOP)

frmLog = Frame(frmBottom)
frmLog.pack(side=RIGHT, fill=X, expand=YES)

txtLog = Text(frmLog, height=4)
txtLog.pack(side=LEFT, fill=X, expand=YES)

root.mainloop()
