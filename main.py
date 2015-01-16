#!/usr/bin/python3
#    pyNSrecruit
#    Copyright (C) 2015  RunasSudo (Yingtong Li)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tkinter import *
from tkinter.ttk import *

# =========================== DEBUG SECTION ===========================
DEBUG = False
if DEBUG:
	Frame = LabelFrame

class Frame(Frame): #Magic.
	def __init__(self, master=None, **options):
		if DEBUG and "dname" in options:
			options["text"] = options["dname"]
		options.pop("dname", None)
		super().__init__(master, **options)

# =========================== GUI FUNCTIONS ===========================
def lbShift(listbox, offset):
	if len(listbox.curselection()) > 0:
		selection = listbox.curselection()[0]
		if selection + offset >= 0 and selection + offset < listbox.size():
			text = listbox.get(selection)
			listbox.delete(selection)
			listbox.insert(selection + offset, text)
			listbox.selection_set(selection + offset)

def makeLabelledText(master, label):
	frmContainer = Frame(master)
	frmContainer.pack(side=TOP)
	
	Label(frmContainer, text=label).pack(side=LEFT)
	
	txtText = Text(frmContainer, height=1)
	txtText.pack(side=LEFT)
	
	return txtText

# ============================= GUI LAYOUT =============================

root = Tk()
root.wm_title("pyNSrecruit")
#Style().theme_use("clam")

frmTop = Frame(root, dname="frmTop")
frmTop.pack(side=TOP, fill=BOTH, expand=YES)

frmLeft = Frame(frmTop, dname="frmLeft")
frmLeft.pack(side=LEFT, fill=BOTH)

# --------------------------- CAMPAIGNS BOX ---------------------------

frmCampaigns = Frame(frmLeft, dname="frmCampaigns")
frmCampaigns.pack(side=TOP, fill=BOTH, expand=YES)

sbCampaigns = Scrollbar(frmCampaigns)
sbCampaigns.pack(side=RIGHT, fill=Y)
lbCampaigns = Listbox(frmCampaigns, yscrollcommand=sbCampaigns.set)
lbCampaigns.pack(side=LEFT, fill=BOTH, expand=YES)
sbCampaigns.config(command=lbCampaigns.yview)

for num in range(0, 10):
	lbCampaigns.insert(END, "Campaign {0}".format(num))

lbCampaigns.itemconfig(1, fg="#AAAAAA")

frmCampaignsSL = Frame(frmLeft, dname="frmCampaignsSL")
frmCampaignsSL.pack(side=BOTTOM)

btnSave = Button(frmCampaignsSL, text="Save")
btnSave.pack(side=LEFT)

btnLoad = Button(frmCampaignsSL, text="Load")
btnLoad.pack(side=LEFT)

btnDelete = Button(frmCampaignsSL, text="Delete")
btnDelete.pack(side=LEFT)

# -------------------------- CAMPAIGN DETAILS --------------------------

frmDetails = Frame(frmTop, height=500, width=500, dname="frmDetails")
frmDetails.pack_propagate(0)
frmDetails.pack(side=RIGHT, fill=BOTH)

#                            CAMPAIGN FILTERS                           

frmFilters = Frame(frmDetails, dname="frmFilters")
frmFilters.pack(side=TOP, fill=X)

frmFilterTargets = LabelFrame(frmDetails, text="Filter Targets")
frmFilterTargets.pack(side=TOP, fill=X)

frmFilterControls = Frame(frmFilterTargets, dname="frmFilterControls")
frmFilterControls.pack(side=RIGHT)

btnFilterAdd = Button(frmFilterControls, text="+", width=2)
btnFilterAdd.pack(side=TOP)

btnFilterRemove = Button(frmFilterControls, text="−", width=2)
btnFilterRemove.pack(side=TOP)

def fnFilterShiftUp():
	lbShift(lbFilters, -1)
btnFilterShiftUp = Button(frmFilterControls, text="▲", width=2, command=fnFilterShiftUp)
btnFilterShiftUp.pack(side=TOP)

def fnFilterShiftDown():
	lbShift(lbFilters, 1)
btnFilterShiftDown = Button(frmFilterControls, text="▼", width=2, command=fnFilterShiftDown)
btnFilterShiftDown.pack(side=TOP)

sbFilters = Scrollbar(frmFilterTargets)
sbFilters.pack(side=RIGHT, fill=Y)
lbFilters = Listbox(frmFilterTargets, yscrollcommand=sbFilters.set)
lbFilters.pack(side=LEFT, fill=BOTH, expand=YES)
sbFilters.config(command=lbCampaigns.yview)

lbFilters.insert(END, "Include Recently Founded")
lbFilters.insert(END, "Exclude Regions 'arnhelm_signatory_1', 'Arnhelm Signatory 2'")
lbFilters.insert(END, "Exclude Classification 'Psychotic Dictatorship'")

#                             OTHER SETTINGS                            

frmClientOptions = LabelFrame(frmDetails, text="Client Options")
frmClientOptions.pack(side=TOP, fill=X)

txtClientKey = makeLabelledText(frmClientOptions, "Client Key:")

frmTelegramSettings = LabelFrame(frmDetails, text="Telegram Details")
frmTelegramSettings.pack(side=TOP, fill=X)

txtTelegramID = makeLabelledText(frmTelegramSettings, "Telegram ID:")
txtSecretKey = makeLabelledText(frmTelegramSettings, "Secret Key:")

btnGetFromURL = Button(frmTelegramSettings, text="Get Settings from URL")
btnGetFromURL.pack(side=TOP, fill=X)

frmSendingRate = LabelFrame(frmDetails, text="Sending Rate")
frmSendingRate.pack(side=TOP, fill=X)

varSendingRate = IntVar()
varSendingRate.set(180)
Radiobutton(frmSendingRate, text="30s (Non-Recruitment Telegram)", variable=varSendingRate, value=30).pack(side=TOP, anchor=W)
Radiobutton(frmSendingRate, text="180s (Recruitment Telegram)", variable=varSendingRate, value=180).pack(side=TOP, anchor=W)

frmCustomRate = Frame(frmSendingRate)
frmCustomRate.pack(side=TOP, anchor=W)

Radiobutton(frmCustomRate, text="Custom Rate:", variable=varSendingRate, value=0).pack(side=LEFT)

txtCustomRate = Text(frmCustomRate, height=1, width=3)
txtCustomRate.pack(side=LEFT)

Label(frmCustomRate, text="s").pack(side=LEFT)

varCampaignEnabled = IntVar()
varCampaignEnabled.set(1)
Checkbutton(frmDetails, text="Campaign Enabled", variable=varCampaignEnabled).pack(side=TOP, anchor=W)

# ---------------------------- BOTTOM PANEL ----------------------------

frmBottom = Frame(root, dname="frmBottom")
frmBottom.pack(side=BOTTOM, fill=X)

frmControls = Frame(frmBottom, dname="frmControls")
frmControls.pack(side=LEFT)

btnStart = Button(frmControls, text="Start")
btnStart.pack(side=TOP)

btnStop = Button(frmControls, text="Stop")
btnStop.pack(side=TOP)

frmLog = Frame(frmBottom, dname="frmLog")
frmLog.pack(side=RIGHT, fill=X, expand=YES)

txtLog = Text(frmLog, height=4)
txtLog.pack(side=LEFT, fill=X, expand=YES)

root.mainloop()
