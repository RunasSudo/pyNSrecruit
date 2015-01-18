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
import tkinter.filedialog
import tkinter.simpledialog
from tkinter.scrolledtext import ScrolledText

import datetime
import json
import threading
import traceback
import urllib.parse
import urllib.request
import webbrowser

# =========================== GUI FUNCTIONS ===========================
def lbShift(listbox, listdata, offset):
	if len(listbox.curselection()) > 0:
		selection = listbox.curselection()[0]
		if selection + offset >= 0 and selection + offset < listbox.size():
			data = listdata[selection]
			
			listbox.delete(selection)
			listdata.pop(selection)
			
			listbox.insert(selection + offset, data)
			listdata.insert(selection + offset, data)
			
			listbox.selection_set(selection + offset)

def makeLabelledText(master, label):
	frmContainer = Frame(master)
	frmContainer.pack(side=TOP)
	
	Label(frmContainer, text=label).pack(side=LEFT)
	
	txtText = Text(frmContainer, height=1)
	txtText.pack(side=LEFT)
	
	return txtText

# Shamelessly ripped from the simpledialog source code. Centres a window.
# Licensed under the PSF LICENSE AGREEMENT FOR PYTHON 3.4.2
def _set_transient(widget, master, relx=0.5, rely=0.3):
	widget.withdraw() # Remain invisible while we figure out the geometry
	widget.transient(master)
	widget.update_idletasks() # Actualize geometry information
	if master.winfo_ismapped():
		m_width = master.winfo_width()
		m_height = master.winfo_height()
		m_x = master.winfo_rootx()
		m_y = master.winfo_rooty()
	else:
		m_width = master.winfo_screenwidth()
		m_height = master.winfo_screenheight()
		m_x = m_y = 0
	w_width = widget.winfo_reqwidth()
	w_height = widget.winfo_reqheight()
	x = m_x + (m_width - w_width) * relx
	y = m_y + (m_height - w_height) * rely
	if x+w_width > master.winfo_screenwidth():
		x = master.winfo_screenwidth() - w_width
	elif x < 0:
		x = 0
	if y+w_height > master.winfo_screenheight():
		y = master.winfo_screenheight() - w_height
	elif y < 0:
		y = 0
	widget.geometry("+%d+%d" % (x, y))
	widget.deiconify() # Become visible at the desired location

#                                LOGGING                               

INFO = (0, "INFO")
WARN = (1, "WARN")
ERRR = (2, "ERRR")
CRIT = (3, "CRIT")
FTAL = (4, "FTAL")

def log(level, text):
	formatted = "{0:%Y-%m-%d %H:%M:%S} [{1}] {2}".format(datetime.datetime.now(), level[1], text)
	print(formatted)
	txtLog.config(state=NORMAL) #Why would you design a library like this, Ousterhout? WHY!
	txtLog.insert(END, formatted + "\n")
	txtLog.config(state=DISABLED)
	txtLog.yview(END)

# ============================== THE GUTS ==============================

class Campaign:
	def __init__(self, name):
		self.name = name
		self.filters = []
	def __str__(self):
		return self.name

class TargetFilter:
	FILTER_EXCLUDE = 1
	FILTER_INCLUDE = 2
	
	def __str__(self):
		return "Unknown filter"
	def filterType(self):
		return 0
	
	def toDict(self):
		return []
	def fromDict(data):
		return TargetFilter()
	
	def getTypeString(typeString):
		return "TargetFilter"
	def getTypeFromString(typeString):
		if typeString == "FilterIncludeName":
			return FilterIncludeName
		return TargetFilter
	
	def configureCallback(self):
		return
	
	def configure(self, callback):
		top = Toplevel()
		top.wm_title("Configure Filter")
		
		frmButtons = Frame(top)
		frmButtons.pack(side=BOTTOM)
		
		def fnConfirm():
			self.configureCallback()
			callback(self)
			top.destroy()
		Button(frmButtons, text="OK", command=fnConfirm).pack(side=LEFT)
		Button(frmButtons, text="Cancel", command=top.destroy).pack(side=LEFT)
		
		_set_transient(top, root)
		
		return top

class FilterIncludeName(TargetFilter):
	def __init__(self, names):
		self.names = names
	def __str__(self):
		return "Include nations {0}".format(self.names)
	def filterType(self):
		return TargetFilter.FILTER_INCLUDE
	
	def toDict(self):
		return {
			"names": self.names
		}
	def fromDict(data):
		return FilterIncludeName(data["names"])
	def getTypeString(typeString):
		return "FilterIncludeName"
	
	def configureCallback(self):
		self.names = self.txtNames.get(1.0, END).rstrip().split("\n")
		
	def configure(self, callback):
		top = super().configure(callback)
		
		Label(top, text="Nation names: (one per line)").pack(side=TOP, anchor=W)
		self.txtNames = ScrolledText(top, height=6)
		self.txtNames.pack(side=TOP, fill=X)

isTelegramming = False

listCampaigns = []

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

# ========================= GUI CHILD WINDOWS =========================

# -------------------------- CONFIGURE FILTER --------------------------

def fnFilterAddCallback(theFilter):
	listFilters.append(theFilter)
	lbFilters.insert(END, theFilter)

def fnFilterAdd():
	top = Toplevel()
	top.wm_title("Select Filter Type")
	
	varFilterMode = StringVar()
	varFilterMode.set("")
	optFilterMode = OptionMenu(top, varFilterMode, "", "", "Include", "Exclude")
	optFilterMode.pack(side=TOP, fill=X)
	
	varFilterType = StringVar()
	varFilterType.set("")
	optFilterType = OptionMenu(top, varFilterType, "", "")
	optFilterType.config(state=DISABLED)
	optFilterType.pack(side=TOP, fill=X)
	
	def fnChangeFilterMode(*args):
		optFilterType["menu"].delete(0, END)
		varFilterType.set("")
		if varFilterMode.get() == "":
			optFilterType.config(state=DISABLED)
		else:
			optFilterType.config(state=NORMAL)
			if varFilterMode.get() == "Include":
				optFilterType["menu"].add_command(label="By Name", command=tkinter._setit(varFilterType, "By Name"))
	
	varFilterMode.trace("w", fnChangeFilterMode)
	
	frmButtons = Frame(top)
	frmButtons.pack(side=BOTTOM)
	
	def fnConfirm():
		theFilter = None
		
		if varFilterMode.get() == "Include" and varFilterType.get() == "By Name":
			FilterIncludeName(["North Jarvis", "Greater Southeast Jarvis"]).configure(fnFilterAddCallback)
		
		top.destroy()
	
	Button(frmButtons, text="OK", command=fnConfirm).pack(side=LEFT)
	Button(frmButtons, text="Cancel", command=top.destroy).pack(side=LEFT)
	
	_set_transient(top, root)

# ============================= GUI LAYOUT =============================

root = Tk()
root.wm_title("pyNSrecruit")

#themes = Style().theme_names()
#Style().theme_use("alt")

# ------------------------------ MENUBAR ------------------------------

menubar = Menu(root)

menuFile = Menu(menubar, tearoff=0)

def fnMenuSave():
	filename = tkinter.filedialog.asksaveasfilename(parent=root)
	if filename:
		try:
			data = {"version": 1}
			data["campaigns"] = []
			
			for campaign in listCampaigns:
				campaignDict = {}
				campaignDict["name"] = campaign.name
				campaignDict["filters"] = []
				
				for theFilter in campaign.filters:
					filterDict = theFilter.toDict()
					filterDict["type"] = theFilter.getTypeString()
					campaignDict["filters"].append(filterDict)
				
				data["campaigns"].append(campaignDict)
			
			with open(filename, "w") as fHandle:
				json.dump(data, fHandle)
			
			log(INFO, "Saved session data.")
		except Exception as e:
			log(ERRR, "An error occurred while saving session data. Check the log.\n{0}".format(repr(e)))
			print(traceback.format_exc())

menuFile.add_command(label="Save", command=fnMenuSave)

def fnMenuLoad():
	filename = tkinter.filedialog.askopenfilename(parent=root)
	if filename:
		try:
			with open(filename, "r") as fHandle:
				data = json.load(fHandle)
			
			if data["version"] != 1:
				log(ERRR, "Unsupported version number {0}.".format(data.version))
				return
			
			#Clear the campaign data.
			for i in range(0, len(listCampaigns)):
				lbCampaigns.delete(i)
				listCampaigns.pop(i)
			
			for campaignDict in data["campaigns"]:
				campaign = Campaign(campaignDict["name"])
				
				for filterDict in campaignDict["filters"]:
					filterType = TargetFilter.getTypeFromString(filterDict["type"])
					theFilter = filterType.fromDict(filterDict)
					campaign.filters.append(theFilter)
				
				listCampaigns.append(campaign)
				lbCampaigns.insert(END, campaign)
			
			log(INFO, "Loaded session data.")
		except Exception as e:
			log(ERRR, "An error occurred while loading session data. Check the log.\n{0}".format(repr(e)))
			print(traceback.format_exc())

menuFile.add_command(label="Load", command=fnMenuLoad)
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

frmTop = Frame(root)
frmTop.pack(side=TOP, fill=BOTH, expand=YES)

frmLeft = Frame(frmTop)
frmLeft.pack(side=LEFT, fill=BOTH)

# --------------------------- CAMPAIGNS BOX ---------------------------

frmCampaigns = Frame(frmLeft)
frmCampaigns.pack(side=TOP, fill=BOTH, expand=YES)

sbCampaigns = Scrollbar(frmCampaigns)
sbCampaigns.pack(side=RIGHT, fill=Y)
lbCampaigns = Listbox(frmCampaigns, yscrollcommand=sbCampaigns.set)
lbCampaigns.pack(side=LEFT, fill=BOTH, expand=YES)
sbCampaigns.config(command=lbCampaigns.yview)

#lbCampaigns.itemconfig(1, fg="#AAAAAA")

frmCampaignsSL = Frame(frmLeft)
frmCampaignsSL.pack(side=BOTTOM)

def fnSave():
	campaignName = tkinter.simpledialog.askstring("Save Campaign", "Campaign Name:", parent=root)
	
	#Delete the campaign if it already exists
	for i in range(0, len(listCampaigns)):
		if listCampaigns[i].name == campaignName:
			listCampaigns.pop(i)
			lbCampaigns.delete(i)
			break
	
	campaign = Campaign(campaignName)
	
	campaign.filters = listFilters
	
	listCampaigns.append(campaign)
	lbCampaigns.insert(END, campaign)

btnSave = Button(frmCampaignsSL, text="Save", command=fnSave)
btnSave.pack(side=LEFT)

btnLoad = Button(frmCampaignsSL, text="Load", state=DISABLED)
btnLoad.pack(side=LEFT)

def fnDelete():
	if len(lbCampaigns.curselection()) > 0:
		selection = lbCampaigns.curselection()[0]
		lbCampaigns.delete(selection)
		listCampaigns.pop(selection)

btnDelete = Button(frmCampaignsSL, text="Delete", command=fnDelete)
btnDelete.pack(side=LEFT)

# -------------------------- CAMPAIGN DETAILS --------------------------

frmDetails = Frame(frmTop, height=500, width=500)
frmDetails.pack_propagate(0)
frmDetails.pack(side=RIGHT, fill=BOTH)

#                            CAMPAIGN FILTERS                           

frmFilterTargets = LabelFrame(frmDetails, text="Filter Targets")
frmFilterTargets.pack(side=TOP, fill=X)

frmFilterControls = Frame(frmFilterTargets)
frmFilterControls.pack(side=RIGHT)

btnFilterAdd = Button(frmFilterControls, text="+", width=2, command=fnFilterAdd)
btnFilterAdd.pack(side=TOP)

def fnFilterRemove():
	if len(lbFilters.curselection()) > 0:
		selection = lbFilters.curselection()[0]
		lbFilters.delete(selection)
		listFilters.pop(selection)

btnFilterRemove = Button(frmFilterControls, text="−", width=2, command=fnFilterRemove)
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

frmBottom = Frame(root)
frmBottom.pack(side=BOTTOM, fill=X)

frmControls = Frame(frmBottom)
frmControls.pack(side=LEFT)

btnStart = Button(frmControls, text="Start", command=fnStart)
btnStart.pack(side=TOP)

btnStop = Button(frmControls, text="Stop", command=fnStop, state=DISABLED)
btnStop.pack(side=TOP)

frmLog = Frame(frmBottom)
frmLog.pack(side=RIGHT, fill=X, expand=YES)

txtLog = ScrolledText(frmLog, height=4, state=DISABLED)
txtLog.pack(side=LEFT, fill=X, expand=YES)

root.mainloop()
