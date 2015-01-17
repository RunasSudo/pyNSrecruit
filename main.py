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
import tkinter.simpledialog
from tkinter.scrolledtext import ScrolledText

import datetime
import threading
import traceback
import urllib.parse
import urllib.request
import webbrowser

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
def lbShift(listbox, listdata, offset):
	if len(listbox.curselection()) > 0:
		selection = listbox.curselection()[0]
		if selection + offset >= 0 and selection + offset < listbox.size():
			data = listdata[selection]
			
			listbox.delete(selection)
			listdata.pop(selection)
			
			listbox.insert(selection + offset, data)
			data.insert(selection + offset, data)
			
			listbox.selection_set(selection + offset)

def makeLabelledText(master, label):
	frmContainer = Frame(master)
	frmContainer.pack(side=TOP)
	
	Label(frmContainer, text=label).pack(side=LEFT)
	
	txtText = Text(frmContainer, height=1)
	txtText.pack(side=LEFT)
	
	return txtText

#                                LOGGING                               

INFO = (0, "INFO")
WARN = (1, "WARN")
ERRR = (2, "ERRR")
CRIT = (3, "CRIT")
FTAL = (4, "FTAL")

def log(level, text):
	formatted = "{0:%Y-%m-%d %H:%M:%S} [{1}] {2}".format(datetime.datetime.now(), level[1], text)
	print(formatted)
	txtLog.insert(END, formatted + "\n")
	txtLog.yview(END)

# ============================== THE GUTS ==============================

class TargetFilter:
	def __str__(self):
		return "Unknown filter"

isTelegramming = False

listFilters = []

def telegramThread():
	log(INFO, "Started telegramming.")
	
	try:
		query = urllib.parse.urlencode({
			"client": txtClientKey.get(1.0, END).rstrip(),
			"tgid": txtTelegramID.get(1.0, END).rstrip(),
			"key": txtSecretKey.get(1.0, END).rstrip(),
			"to": "North Jarvis"
		})
		
		req = urllib.request.Request("http://www.nationstates.net/cgi-bin/api.cgi?a=sendTG&{0}".format(query))
		req.add_header("User-Agent", "pyNSrecruit/0.1 (South Jarvis)")
		
		#resp = urllib.request.urlopen(req)
		
		#log(INFO, "Got status: {0}".format(resp.status))
	except Exception as e:
		log(CRIT, "An error occurred while telegramming. Check the log.\n{0}".format(repr(e)))
		print(traceback.format_exc())
	
	isTelegramming = False
	
	log(INFO, "Stopped telegramming.")
	btnStart.config(state=NORMAL)
	btnStop.config(state=DISABLED)

def fnStart():
	log(INFO, "Starting telegramming.")
	isTelegramming = True
	btnStart.config(state=DISABLED)
	btnStop.config(state=NORMAL)
	
	thread = threading.Thread(target=telegramThread)
	thread.start()

def fnStop():
	log(INFO, "Stopping telegramming.")
	
	isTelegramming = False #Signal to the telegram thread that it should stop.
	
	#Wait for stop.

# ============================= GUI LAYOUT =============================

root = Tk()
root.wm_title("pyNSrecruit")
#Style().theme_use("clam")

# ------------------------------ MENUBAR ------------------------------

menubar = Menu(root)

menuFile = Menu(menubar, tearoff=0)
menuFile.add_command(label="Save", state=DISABLED)
menuFile.add_command(label="Load", state=DISABLED)
menuFile.add_separator()
menuFile.add_command(label="Quit", command=root.quit)
menubar.add_cascade(label="File", menu=menuFile)

menuHelp = Menu(menubar, tearoff=0)
def fnMenuHelp():
	webbrowser.open("https://github.com/RunasSudo/pyNSrecruit/wiki")
menuHelp.add_command(label="Online Help", command=fnMenuHelp)
menuHelp.add_command(label="About", state=DISABLED)
menubar.add_cascade(label="Help", menu=menuHelp)

root.config(menu=menubar)

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

#lbCampaigns.itemconfig(1, fg="#AAAAAA")

frmCampaignsSL = Frame(frmLeft, dname="frmCampaignsSL")
frmCampaignsSL.pack(side=BOTTOM)

btnSave = Button(frmCampaignsSL, text="Save", state=DISABLED)
btnSave.pack(side=LEFT)

btnLoad = Button(frmCampaignsSL, text="Load", state=DISABLED)
btnLoad.pack(side=LEFT)

btnDelete = Button(frmCampaignsSL, text="Delete", state=DISABLED)
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

btnFilterAdd = Button(frmFilterControls, text="+", width=2, state=DISABLED)
btnFilterAdd.pack(side=TOP)

btnFilterRemove = Button(frmFilterControls, text="−", width=2, state=DISABLED)
btnFilterRemove.pack(side=TOP)

def fnFilterShiftUp():
	lbShift(lbFilters, listFilters, -1)
btnFilterShiftUp = Button(frmFilterControls, text="▲", width=2, command=fnFilterShiftUp)
btnFilterShiftUp.pack(side=TOP)

def fnFilterShiftDown():
	lbShift(lbFilters, listFilters, 1)
btnFilterShiftDown = Button(frmFilterControls, text="▼", width=2, command=fnFilterShiftDown)
btnFilterShiftDown.pack(side=TOP)

sbFilters = Scrollbar(frmFilterTargets)
sbFilters.pack(side=RIGHT, fill=Y)
lbFilters = Listbox(frmFilterTargets, yscrollcommand=sbFilters.set)
lbFilters.pack(side=LEFT, fill=BOTH, expand=YES)
sbFilters.config(command=lbCampaigns.yview)

tmp = TargetFilter()
lbFilters.insert(END, tmp)
listFilters.append(tmp)

#                             OTHER SETTINGS                            

frmClientOptions = LabelFrame(frmDetails, text="Client Options")
frmClientOptions.pack(side=TOP, fill=X)

txtClientKey = makeLabelledText(frmClientOptions, "Client Key:")

frmTelegramSettings = LabelFrame(frmDetails, text="Telegram Details")
frmTelegramSettings.pack(side=TOP, fill=X)

txtTelegramID = makeLabelledText(frmTelegramSettings, "Telegram ID:")
txtSecretKey = makeLabelledText(frmTelegramSettings, "Secret Key:")

def fnGetFromURL():
	apiURL = tkinter.simpledialog.askstring("Get Settings from URL", "Paste the 'make an API Request to' URL here to automatically detect the telegram ID and secret key.\ne.g. http://www.nationstates.net/cgi-bin/api.cgi?a=sendTG&client=YOUR_API_CLIENT_KEY&tgid=TELEGRAM_ID&key=SECRET_KEY&to=NATION_NAME", parent=root)
	if apiURL:
		params = urllib.parse.parse_qs(urllib.parse.urlparse(apiURL).query)
		
		if "client" in params and params["client"][0] != "YOUR_API_CLIENT_KEY":
			txtClientKey.delete(1.0, END)
			txtClientKey.insert(END, params["client"][0])
		
		if "tgid" in params:
			txtTelegramID.delete(1.0, END)
			txtTelegramID.insert(END, params["tgid"][0])
		
		if "key" in params:
			txtSecretKey.delete(1.0, END)
			txtSecretKey.insert(END, params["key"][0])

btnGetFromURL = Button(frmTelegramSettings, text="Get Settings from URL", command=fnGetFromURL)
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

Label(frmCustomRate, text="s (This may violate the API Terms of Service!)").pack(side=LEFT)

varCampaignEnabled = IntVar()
varCampaignEnabled.set(1)
Checkbutton(frmDetails, text="Campaign Enabled", variable=varCampaignEnabled).pack(side=TOP, anchor=W)

varCampaignDryRun = IntVar()
varCampaignDryRun.set(1)
Checkbutton(frmDetails, text="Dry Run (Don't actually send any telegrams)", variable=varCampaignDryRun).pack(side=TOP, anchor=W)

# ---------------------------- BOTTOM PANEL ----------------------------

frmBottom = Frame(root, dname="frmBottom")
frmBottom.pack(side=BOTTOM, fill=X)

frmControls = Frame(frmBottom, dname="frmControls")
frmControls.pack(side=LEFT)

btnStart = Button(frmControls, text="Start", command=fnStart)
btnStart.pack(side=TOP)

btnStop = Button(frmControls, text="Stop", command=fnStop, state=DISABLED)
btnStop.pack(side=TOP)

frmLog = Frame(frmBottom, dname="frmLog")
frmLog.pack(side=RIGHT, fill=X, expand=YES)

txtLog = ScrolledText(frmLog, height=4)
txtLog.pack(side=LEFT, fill=X, expand=YES)

root.mainloop()
