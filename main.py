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
		super(Frame, self).__init__(master, **options)

# ============================= GUI LAYOUT =============================

root = Tk()
#Style().theme_use("clam")

frmTop = Frame(root, dname="frmTop")
frmTop.pack(side=TOP, fill=BOTH)

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

Label(frmFilters, text="Filter Targets").pack(side=TOP, anchor=W)

frmFilterControls = Frame(frmFilters, dname="frmFilterControls")
frmFilterControls.pack(side=RIGHT)

btnFilterAdd = Button(frmFilterControls, text="+", width=2)
btnFilterAdd.pack(side=TOP)

btnFilterRemove = Button(frmFilterControls, text="−", width=2)
btnFilterRemove.pack(side=TOP)

btnFilterShiftUp = Button(frmFilterControls, text="▲", width=2)
btnFilterShiftUp.pack(side=TOP)

btnFilterShiftDown = Button(frmFilterControls, text="▼", width=2)
btnFilterShiftDown.pack(side=TOP)

sbFilters = Scrollbar(frmFilters)
sbFilters.pack(side=RIGHT, fill=Y)
lbFilters = Listbox(frmFilters, yscrollcommand=sbFilters.set)
lbFilters.pack(side=LEFT, fill=BOTH, expand=YES)
sbFilters.config(command=lbCampaigns.yview)

#                             OTHER SETTINGS                            

Label(frmDetails, text="Telegram Settings").pack(side=TOP, anchor=W)

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
