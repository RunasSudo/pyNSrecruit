#!/usr/bin/python3 -u
#    pyNSrecruit
#    Copyright © 2015, 2017  RunasSudo (Yingtong Li)
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

# If you modify pyNSrecruit, please consider modifying one (or both) of the following lines to show this.
VERSION = "0.2.3"
USERAGENT = "pyNSrecruit/{0} (South Jarvis)".format(VERSION)

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import tkinter.simpledialog
import tkinter.scrolledtext

import collections
import datetime
import json
import re
import time
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
	frmContainer = ttk.Frame(master)
	frmContainer.pack(side=tk.TOP)
	
	ttk.Label(frmContainer, text=label).pack(side=tk.LEFT)
	
	txtText = tk.Text(frmContainer, height=1)
	txtText.pack(side=tk.LEFT)
	
	return txtText

# Shamelessly ripped from the simpledialog source code. Centres a window.
# Licensed under the PSF LICENSE AGREEMENT FOR PYTHON 3.4.2
def _set_transient(widget, master, relx=0.5, rely=0.3):
	widget.withdraw()  # Remain invisible while we figure out the geometry
	widget.transient(master)
	widget.update_idletasks()  # Actualize geometry information
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
	if x + w_width > master.winfo_screenwidth():
		x = master.winfo_screenwidth() - w_width
	elif x < 0:
		x = 0
	if y + w_height > master.winfo_screenheight():
		y = master.winfo_screenheight() - w_height
	elif y < 0:
		y = 0
	widget.geometry("+%d+%d" % (x, y))
	widget.deiconify()  # Become visible at the desired location

#                                LOGGING                               

DEBG = (0, "DEBG")
INFO = (1, "INFO")
WARN = (2, "WARN")
ERRR = (3, "ERRR")
CRIT = (4, "CRIT")
FTAL = (5, "FTAL")

def log(level, text):
	formatted = "{0:%Y-%m-%d %H:%M:%S} [{1}] {2}".format(datetime.datetime.now(), level[1], text)
	print(formatted)
	txtLog.config(state=tk.NORMAL)  # Why would you design a library like this, Ousterhout? WHY!
	txtLog.insert(tk.END, formatted + "\n")
	txtLog.config(state=tk.DISABLED)
	txtLog.yview(tk.END)

# ============================== THE GUTS ==============================

class Campaign:
	def __init__(self, name):
		self.name = name
		self.filters = []
		self.clientKey = ""
		self.telegramID = ""
		self.secretKey = ""
		self.sendingRate = 180
		self.customRate = ""
		self.enabled = 1
		self.dryRun = 0
	def __str__(self):
		return self.name

class TargetFilter:
	FILTER_EXCLUDE = 1
	FILTER_INCLUDE = 2
	
	def __str__(self):
		return "Unknown filter"
	def filterType(self):
		return 0
	
	@staticmethod
	def fromDict(data):
		return TargetFilter()
	def toDict(self):
		return {}
	
	@staticmethod
	def getTypeFromString(typeString):
		if typeString == "FilterIncludeName":
			return FilterIncludeName
		if typeString == "FilterIncludeAction":
			return FilterIncludeAction
		if typeString == "FilterExcludeCategory":
			return FilterExcludeCategory
		log(WARN, "Unknown filter type {0}.".format(typeString))
		return TargetFilter
	def getTypeString(self):
		return "TargetFilter"
	
	def makeCopy(self):
		# Jump through hoops to avoid referencing filters of other campaigns
		# copy.deepcopy = infinite recursion :(
		return TargetFilter.getTypeFromString(self.getTypeString()).fromDict(self.toDict())
	
	def configureCallback(self):
		return
	
	def configure(self, callback):
		top = tk.Toplevel()
		top.wm_title("Configure Filter")
		
		self.frmButtons = ttk.Frame(top)
		self.frmButtons.pack(side=tk.BOTTOM)
		
		def fnConfirm():
			self.configureCallback()
			callback(self)
			top.destroy()
		ttk.Button(self.frmButtons, text="OK", command=fnConfirm).pack(side=tk.LEFT)
		ttk.Button(self.frmButtons, text="Cancel", command=top.destroy).pack(side=tk.LEFT)
		
		_set_transient(top, root)
		
		return top

class TargetFilterInvertible(TargetFilter):
	def configure(self, callback):
		top = super().configure(callback)
		
		self.varInverted = tk.IntVar()
		cbInverted = ttk.Checkbutton(self.frmButtons, text="Invert filter", variable=self.varInverted)
		cbInverted.pack(side=tk.LEFT)
		
		return top

class FilterIncludeName(TargetFilter):
	def __init__(self, names):
		self.names = names
	def __str__(self):
		return "Include nations {0}".format(self.names)
	def filterType(self):
		return TargetFilter.FILTER_INCLUDE
	
	def getNations(self):
		return self.names
	
	@staticmethod
	def fromDict(data):
		return FilterIncludeName(data["names"])
	def toDict(self):
		return {
			"names": self.names
		}
	def getTypeString(self):
		return "FilterIncludeName"
	
	def configureCallback(self):
		self.names = self.txtNames.get(1.0, tk.END).rstrip().split("\n")
		
	def configure(self, callback):
		top = super().configure(callback)
		
		ttk.Label(top, text="Nation names: (one per line)").pack(side=tk.TOP, anchor=tk.W)
		self.txtNames = tkinter.scrolledtext.ScrolledText(top, height=6)
		self.txtNames.pack(side=tk.TOP, fill=tk.X)

class FilterIncludeAction(TargetFilter):
	def __init__(self, actionType):
		self.actionType = actionType
	def __str__(self):
		return "Include action '{0}'".format(self.actionType)
	def filterType(self):
		return TargetFilter.FILTER_INCLUDE
	
	def getNations(self):
		try:
			if self.actionType == "founding" or self.actionType == "refounding":
				req = urllib.request.Request("https://www.nationstates.net/cgi-bin/api.cgi?q=happenings;filter=founding;limit=50")
			req.add_header("User-Agent", USERAGENT)
			resp = urllib.request.urlopen(req)
			
			nations = []
			
			if resp.status == 200:
				data = resp.read().decode("utf-8")
				happenings = re.finditer(r"<!\[CDATA\[(.*)\]\]>", data)
				for happening in happenings:
					happeningString = happening.group(1)
					nation = re.search(r"@@(.*)@@", happeningString).group(1)
					action = re.search(r"@@ was (founded|refounded) in %%", happeningString).group(1)
					
					if action == "founded" and self.actionType == "founding":
						nations.append(nation)
					if action == "refounded" and self.actionType == "refounding":
						nations.append(nation)
				return nations
			else:
				log(ERRR, "Unable to load happenings. Got response code {0}.".format(resp.status))
		except Exception as e:
			log(ERRR, "Unable to load happenings. Check the log.\n{0}".format(repr(e)))
			print(traceback.format_exc())
		
		return []
	
	@staticmethod
	def fromDict(data):
		return FilterIncludeAction(data["action"])
	def toDict(self):
		return {
			"action": self.actionType
		}
	def getTypeString(self):
		return "FilterIncludeAction"
	
	def configureCallback(self):
		self.actionType = self.varActionType.get()
		
	def configure(self, callback):
		top = super().configure(callback)
		
		ttk.Label(top, text="Action type:").pack(side=tk.TOP, anchor=tk.W)
		
		self.varActionType = tk.StringVar()
		ttk.Radiobutton(top, text="Nation Founding (excluding refounding)", variable=self.varActionType, value="founding").pack(anchor=tk.W)
		ttk.Radiobutton(top, text="Nation Refounding", variable=self.varActionType, value="refounding").pack(anchor=tk.W)

class FilterExcludeCategory(TargetFilterInvertible):
	def __init__(self, categories, inverted):
		self.categories = categories
		self.inverted = inverted
	def __str__(self):
		return "{0} categories {1}".format("NOT Exclude" if self.inverted else "Exclude", self.categories)
	def filterType(self):
		return TargetFilter.FILTER_EXCLUDE
	
	def matches(self, nation):
		try:
			req = urllib.request.Request("https://www.nationstates.net/cgi-bin/api.cgi?nation={0}&q=category".format(nation))
			req.add_header("User-Agent", USERAGENT)
			resp = urllib.request.urlopen(req)
			
			if resp.status == 200:
				data = resp.read().decode("utf-8")
				nationCategory = re.search(r"<CATEGORY>(.*)</CATEGORY>", data).group(1)
				log(DEBG, "Got category {0}.".format(nationCategory))
				for matchCategory in self.categories:
					if nationCategory == matchCategory:
						return (True if self.inverted == 0 else False)
				return (False if self.inverted == 0 else True)
			else:
				log(ERRR, "Unable to load data for {1}. Got response code {0}.".format(resp.status, nation))
		except Exception as e:
			log(ERRR, "Unable to load data for {1}. Check the log.\n{0}".format(repr(e), nation))
			print(traceback.format_exc())
		
		return True  # Be safe!
	
	@staticmethod
	def fromDict(data):
		return FilterExcludeCategory(data["categories"], data["inverted"])
	def toDict(self):
		return {
			"categories": self.categories,
			"inverted": self.inverted
		}
	def getTypeString(self):
		return "FilterExcludeCategory"
	
	def configureCallback(self):
		self.inverted = self.varInverted.get()
		self.categories = []
		
		for varCategory in self.varCategories:
			if varCategory[1].get() == 1:
				self.categories.append(varCategory[0])
		
	def configure(self, callback):
		top = super().configure(callback)
		
		ttk.Label(top, text="Exclude the following nation categories:").pack(side=tk.TOP, anchor=tk.W)
		
		self.varCategories = []
		
		def addCategory(master, name):
			var = [name, tk.IntVar()]
			cb = ttk.Checkbutton(master, text=name, variable=var[1])
			cb.pack(side=tk.TOP, anchor=tk.W)
			self.varCategories.append(var)
		
		threeCols = ttk.Frame(top)
		
		col1 = ttk.Frame(threeCols)
		addCategory(col1, "Anarchy")
		addCategory(col1, "Authoritarian Democracy")
		addCategory(col1, "Benevolent Dictatorship")
		addCategory(col1, "Capitalist Paradise")
		addCategory(col1, "Capitalizt")
		addCategory(col1, "Civil Rights Lovefest")
		addCategory(col1, "Compulsory Consumerist State")
		addCategory(col1, "Conservative Democracy")
		addCategory(col1, "Corporate Bordello")
		addCategory(col1, "Corporate Police State")
		col1.pack(side=tk.LEFT)
		
		col2 = ttk.Frame(threeCols)
		addCategory(col2, "Corrupt Dictatorship")
		addCategory(col2, "Democratic Socialists")
		addCategory(col2, "Father Knows Best State")
		addCategory(col2, "Free-Market Paradise")
		addCategory(col2, "Inoffensive Centrist Democracy")
		addCategory(col2, "Iron Fist Consumerists")
		addCategory(col2, "Iron Fist Socialists")
		addCategory(col2, "Left-Leaning College State")
		addCategory(col2, "Left-wing Utopia")
		col2.pack(side=tk.LEFT)
		
		col3 = ttk.Frame(threeCols)
		addCategory(col3, "Liberal Democratic Socialists")
		addCategory(col3, "Libertarian Police State")
		addCategory(col3, "Moralistic Democracy")
		addCategory(col3, "Mother Knows Best State")
		addCategory(col3, "New York Times Democracy")
		addCategory(col3, "Psychotic Dictatorship")
		addCategory(col3, "Right-wing Utopia")
		addCategory(col3, "Scandinavian Liberal Paradise")
		addCategory(col3, "Tyranny by Majority")
		col3.pack(side=tk.LEFT)
		
		threeCols.pack(side=tk.TOP)

isTelegramming = False

listCampaigns = []

listFilters = []

def telegramThread():
	global isTelegramming  # What is Python even?
	
	log(INFO, "Started telegramming.")
	
	telegramHistory = collections.deque(maxlen=100)  # TODO: Make this configurable.
	
	try:
		while isTelegramming:
			targetNationsData = []
			# Compute INCLUDE targets
			for campaign in listCampaigns:
				if campaign.enabled:
					for theFilter in campaign.filters:
						if theFilter.filterType() == TargetFilter.FILTER_INCLUDE:
							nations = theFilter.getNations()
							for nation in nations:
								targetNationsData.append((campaign, nation))
			
			nationsTelegrammed = 0  # This round
			for nationData in targetNationsData:
				campaign = nationData[0]
				nation = nationData[1]
				
				log(DEBG, "Trying {0} with '{1}'.".format(nation, campaign))
				
				if nation in telegramHistory:
					log(DEBG, "Discarding {0} due to being present in history.".format(nation))
					continue
				
				matchesFilter = False
				for theFilter in campaign.filters:
					if theFilter.filterType() == TargetFilter.FILTER_EXCLUDE:
						if theFilter.matches(nation):
							matchesFilter = theFilter
							break
				
				if matchesFilter:
					log(DEBG, "Discarding {0} due to matching '{1}'.".format(nation, matchesFilter))
					continue
				
				nationsTelegrammed += 1
				
				log(INFO, "Telegramming {0} with '{1}'.".format(nation, campaign))
				
				if campaign.dryRun:
					log(INFO, "Dry-run mode enabled, so not doing anything.")
				else:
					# Telegram the nation
					try:
						query = urllib.parse.urlencode({
							"client": campaign.clientKey,
							"tgid": campaign.telegramID,
							"key": campaign.secretKey,
							"to": nation
						})
						
						req = urllib.request.Request("https://www.nationstates.net/cgi-bin/api.cgi?a=sendTG&{0}".format(query))
						req.add_header("User-Agent", USERAGENT)
						
						resp = urllib.request.urlopen(req)
						
						log(DEBG, "Got status: {0}.".format(resp.status))
					except Exception as e:
						log(ERRR, "An error occurred while telegramming the nation. Check the log.\n{0}".format(repr(e)))
						print(traceback.format_exc())
				
				telegramHistory.append(nation)
				
				sendingRate = campaign.sendingRate
				if sendingRate == 0:
					sendingRate = int(campaign.customRate)
				if sendingRate < 0:
					sendingRate = 0
				
				log(INFO, "Waiting {0} seconds.".format(sendingRate))
				time.sleep(sendingRate + 2)  # The rate is a lie!
				
				break
			
			if nationsTelegrammed <= 0:
				log(WARN, "All applicable nations have been telegrammed already. Waiting 30 seconds.")
				log(WARN, "If telegramming a fixed number of recipients, it is safe to stop telegramming now.")
				time.sleep(30)
	except Exception as e:
		log(CRIT, "An error occurred. Check the log.\n{0}".format(repr(e)))
		print(traceback.format_exc())
	
	isTelegramming = False
	
	log(INFO, "Stopped telegramming.")
	btnStart.config(state=tk.NORMAL)
	btnStop.config(state=tk.DISABLED)

def fnStart():
	global isTelegramming
	
	log(INFO, "Starting telegramming.")
	isTelegramming = True
	btnStart.config(state=tk.DISABLED)
	btnStop.config(state=tk.NORMAL)
	
	thread = threading.Thread(target=telegramThread)
	thread.daemon = True
	thread.start()

def fnStop():
	global isTelegramming
	
	log(INFO, "Stopping telegramming. Telegramming will stop when waiting finishes.")
	
	isTelegramming = False  # Signal to the telegram thread that it should stop.
	
	# Wait for stop.

# ========================= GUI CHILD WINDOWS =========================

# -------------------------- CONFIGURE FILTER --------------------------

def fnFilterAddCallback(theFilter):
	listFilters.append(theFilter)
	lbFilters.insert(tk.END, theFilter)

def fnFilterAdd():
	top = tk.Toplevel()
	top.wm_title("Select Filter Type")
	
	varFilterMode = tk.StringVar()
	varFilterMode.set("")
	optFilterMode = ttk.OptionMenu(top, varFilterMode, "", "", "Include", "Exclude")
	optFilterMode.pack(side=tk.TOP, fill=tk.X)
	
	varFilterType = tk.StringVar()
	varFilterType.set("")
	optFilterType = ttk.OptionMenu(top, varFilterType, "", "")
	optFilterType.config(state=tk.DISABLED)
	optFilterType.pack(side=tk.TOP, fill=tk.X)
	
	def fnChangeFilterMode(*args):
		optFilterType["menu"].delete(0, tk.END)
		varFilterType.set("")
		if varFilterMode.get() == "":
			optFilterType.config(state=tk.DISABLED)
		else:
			optFilterType.config(state=tk.NORMAL)
			if varFilterMode.get() == "Include":
				optFilterType["menu"].add_command(label="By Name", command=tkinter._setit(varFilterType, "By Name"))
				optFilterType["menu"].add_command(label="By Action", command=tkinter._setit(varFilterType, "By Action"))
			if varFilterMode.get() == "Exclude":
				optFilterType["menu"].add_command(label="By Category", command=tkinter._setit(varFilterType, "By Category"))
	
	varFilterMode.trace("w", fnChangeFilterMode)
	
	frmButtons = ttk.Frame(top)
	frmButtons.pack(side=tk.BOTTOM)
	
	def fnConfirm():
		if varFilterMode.get() == "Include" and varFilterType.get() == "By Name":
			FilterIncludeName([]).configure(fnFilterAddCallback)
		if varFilterMode.get() == "Include" and varFilterType.get() == "By Action":
			FilterIncludeAction("").configure(fnFilterAddCallback)
		if varFilterMode.get() == "Exclude" and varFilterType.get() == "By Category":
			FilterExcludeCategory([], 0).configure(fnFilterAddCallback)
		
		top.destroy()
	
	ttk.Button(frmButtons, text="OK", command=fnConfirm).pack(side=tk.LEFT)
	ttk.Button(frmButtons, text="Cancel", command=top.destroy).pack(side=tk.LEFT)
	
	_set_transient(top, root)

# ============================= GUI LAYOUT =============================

root = tk.Tk()
root.wm_title("pyNSrecruit")

# themes = Style().theme_names()
# Style().theme_use("alt")

# ------------------------------ MENUBAR ------------------------------

menubar = tk.Menu(root)

menuFile = tk.Menu(menubar, tearoff=0)

def fnMenuSave():
	filename = tkinter.filedialog.asksaveasfilename(parent=root)
	if filename:
		try:
			data = {"version": 1}
			data["campaigns"] = []
			
			for campaign in listCampaigns:
				campaignDict = {}
				campaignDict["name"] = campaign.name
				campaignDict["clientKey"] = campaign.clientKey
				campaignDict["telegramID"] = campaign.telegramID
				campaignDict["secretKey"] = campaign.secretKey
				campaignDict["sendingRate"] = campaign.sendingRate
				campaignDict["customRate"] = campaign.customRate
				campaignDict["enabled"] = campaign.enabled
				campaignDict["dryRun"] = campaign.dryRun
				
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
			
			# Clear the campaign data.
			lbCampaigns.delete(0, tk.END)
			listCampaigns[:] = []
			
			for campaignDict in data["campaigns"]:
				campaign = Campaign(campaignDict["name"])
				campaign.clientKey = campaignDict["clientKey"]
				campaign.telegramID = campaignDict["telegramID"]
				campaign.secretKey = campaignDict["secretKey"]
				campaign.sendingRate = campaignDict["sendingRate"]
				campaign.customRate = campaignDict["customRate"]
				campaign.enabled = campaignDict["enabled"]
				campaign.dryRun = campaignDict["dryRun"]
				
				for filterDict in campaignDict["filters"]:
					filterType = TargetFilter.getTypeFromString(filterDict["type"])
					theFilter = filterType.fromDict(filterDict)
					campaign.filters.append(theFilter)
				
				listCampaigns.append(campaign)
				lbCampaigns.insert(tk.END, campaign)
				
				if not campaign.enabled:
					lbCampaigns.itemconfig(tk.END, fg="#AAAAAA")
			
			log(INFO, "Loaded session data.")
		except Exception as e:
			log(ERRR, "An error occurred while loading session data. Check the log.\n{0}".format(repr(e)))
			print(traceback.format_exc())

menuFile.add_command(label="Load", command=fnMenuLoad)
menuFile.add_separator()
menuFile.add_command(label="Quit", command=root.quit)
menubar.add_cascade(label="File", menu=menuFile)

menuHelp = tk.Menu(menubar, tearoff=0)
def fnMenuHelp():
	webbrowser.open("https://github.com/RunasSudo/pyNSrecruit/wiki")
menuHelp.add_command(label="Online Help", command=fnMenuHelp)
menuHelp.add_command(label="About", state=tk.DISABLED)
menubar.add_cascade(label="Help", menu=menuHelp)

root.config(menu=menubar)

frmTop = ttk.Frame(root)
frmTop.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

frmLeft = ttk.Frame(frmTop)
frmLeft.pack(side=tk.LEFT, fill=tk.BOTH)

# --------------------------- CAMPAIGNS BOX ---------------------------

frmCampaigns = ttk.Frame(frmLeft)
frmCampaigns.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

sbCampaigns = ttk.Scrollbar(frmCampaigns)
sbCampaigns.pack(side=tk.RIGHT, fill=tk.Y)
lbCampaigns = tk.Listbox(frmCampaigns, yscrollcommand=sbCampaigns.set)
lbCampaigns.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
sbCampaigns.config(command=lbCampaigns.yview)

frmCampaignsSL = ttk.Frame(frmLeft)
frmCampaignsSL.pack(side=tk.BOTTOM)

def fnSave():
	campaignName = tkinter.simpledialog.askstring("Save Campaign", "Campaign Name:", parent=root)
	
	# Delete the campaign if it already exists
	for i in range(0, len(listCampaigns)):
		if listCampaigns[i].name == campaignName:
			listCampaigns.pop(i)
			lbCampaigns.delete(i)
			break
	
	campaign = Campaign(campaignName)
	
	campaign.clientKey = txtClientKey.get(1.0, tk.END).rstrip()
	campaign.telegramID = txtTelegramID.get(1.0, tk.END).rstrip()
	campaign.secretKey = txtSecretKey.get(1.0, tk.END).rstrip()
	campaign.sendingRate = varSendingRate.get()
	campaign.customRate = txtCustomRate.get(1.0, tk.END).rstrip()
	campaign.enabled = varCampaignEnabled.get()
	campaign.dryRun = varCampaignDryRun.get()
	
	for theFilter in listFilters:
		campaign.filters.append(theFilter.makeCopy())
	
	listCampaigns.append(campaign)
	lbCampaigns.insert(tk.END, campaign)
	
	if not campaign.enabled:
		lbCampaigns.itemconfig(tk.END, fg="#AAAAAA")

btnSave = ttk.Button(frmCampaignsSL, text="Save", command=fnSave)
btnSave.pack(side=tk.LEFT)

def fnLoad(*args):
	if len(lbCampaigns.curselection()) > 0:
		selection = lbCampaigns.curselection()[0]
		
		# Clear the campaign data.
		lbFilters.delete(0, tk.END)
		listFilters[:] = []
		
		campaign = listCampaigns[selection]
		
		txtClientKey.delete(1.0, tk.END)
		txtClientKey.insert(tk.END, campaign.clientKey)
		txtTelegramID.delete(1.0, tk.END)
		txtTelegramID.insert(tk.END, campaign.telegramID)
		txtSecretKey.delete(1.0, tk.END)
		txtSecretKey.insert(tk.END, campaign.secretKey)
		varSendingRate.set(campaign.sendingRate)
		txtCustomRate.delete(1.0, tk.END)
		txtCustomRate.insert(tk.END, campaign.customRate)
		varCampaignEnabled.set(campaign.enabled)
		varCampaignDryRun.set(campaign.dryRun)
		
		for theFilter in campaign.filters:
			copyFilter = theFilter.makeCopy()
			lbFilters.insert(tk.END, copyFilter)
			listFilters.append(copyFilter)

btnLoad = ttk.Button(frmCampaignsSL, text="Load", command=fnLoad)
btnLoad.pack(side=tk.LEFT)
lbCampaigns.bind("<Double-Button-1>", fnLoad)

def fnDelete():
	if len(lbCampaigns.curselection()) > 0:
		selection = lbCampaigns.curselection()[0]
		lbCampaigns.delete(selection)
		listCampaigns.pop(selection)

btnDelete = ttk.Button(frmCampaignsSL, text="Delete", command=fnDelete)
btnDelete.pack(side=tk.LEFT)

# -------------------------- CAMPAIGN DETAILS --------------------------

frmDetails = ttk.Frame(frmTop, height=500, width=500)
frmDetails.pack_propagate(0)
frmDetails.pack(side=tk.RIGHT, fill=tk.BOTH)

#                            CAMPAIGN FILTERS                           

frmFilterTargets = ttk.LabelFrame(frmDetails, text="Filter Targets")
frmFilterTargets.pack(side=tk.TOP, fill=tk.X)

frmFilterControls = ttk.Frame(frmFilterTargets)
frmFilterControls.pack(side=tk.RIGHT)

btnFilterAdd = ttk.Button(frmFilterControls, text="+", width=2, command=fnFilterAdd)
btnFilterAdd.pack(side=tk.TOP)

def fnFilterRemove():
	if len(lbFilters.curselection()) > 0:
		selection = lbFilters.curselection()[0]
		lbFilters.delete(selection)
		listFilters.pop(selection)

btnFilterRemove = ttk.Button(frmFilterControls, text="−", width=2, command=fnFilterRemove)
btnFilterRemove.pack(side=tk.TOP)

def fnFilterShiftUp():
	lbShift(lbFilters, listFilters, -1)
btnFilterShiftUp = ttk.Button(frmFilterControls, text="▲", width=2, command=fnFilterShiftUp)
btnFilterShiftUp.pack(side=tk.TOP)

def fnFilterShiftDown():
	lbShift(lbFilters, listFilters, 1)
btnFilterShiftDown = ttk.Button(frmFilterControls, text="▼", width=2, command=fnFilterShiftDown)
btnFilterShiftDown.pack(side=tk.TOP)

sbXFilters = ttk.Scrollbar(frmFilterTargets, orient=tk.HORIZONTAL)
sbXFilters.pack(side=tk.BOTTOM, fill=tk.X)
sbYFilters = ttk.Scrollbar(frmFilterTargets, orient=tk.VERTICAL)
sbYFilters.pack(side=tk.RIGHT, fill=tk.Y)
lbFilters = tk.Listbox(frmFilterTargets, xscrollcommand=sbXFilters.set, yscrollcommand=sbYFilters.set)
lbFilters.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
sbXFilters.config(command=lbFilters.xview)
sbYFilters.config(command=lbFilters.yview)

#                             OTHER SETTINGS                            

frmClientOptions = ttk.LabelFrame(frmDetails, text="Client Options")
frmClientOptions.pack(side=tk.TOP, fill=tk.X)

txtClientKey = makeLabelledText(frmClientOptions, "Client Key:")

frmTelegramSettings = ttk.LabelFrame(frmDetails, text="Telegram Details")
frmTelegramSettings.pack(side=tk.TOP, fill=tk.X)

txtTelegramID = makeLabelledText(frmTelegramSettings, "Telegram ID:")
txtSecretKey = makeLabelledText(frmTelegramSettings, "Secret Key:")

def fnGetFromURL():
	apiURL = tkinter.simpledialog.askstring("Get Settings from URL", "Paste the 'make an API Request to' URL here to automatically detect the telegram ID and secret key.\ne.g. http://www.nationstates.net/cgi-bin/api.cgi?a=sendTG&client=YOUR_API_CLIENT_KEY&tgid=TELEGRAM_ID&key=SECRET_KEY&to=NATION_NAME", parent=root)
	if apiURL:
		params = urllib.parse.parse_qs(urllib.parse.urlparse(apiURL).query)
		
		if "client" in params and params["client"][0] != "YOUR_API_CLIENT_KEY":
			txtClientKey.delete(1.0, tk.END)
			txtClientKey.insert(tk.END, params["client"][0])
		
		if "tgid" in params:
			txtTelegramID.delete(1.0, tk.END)
			txtTelegramID.insert(tk.END, params["tgid"][0])
		
		if "key" in params:
			txtSecretKey.delete(1.0, tk.END)
			txtSecretKey.insert(tk.END, params["key"][0])

btnGetFromURL = ttk.Button(frmTelegramSettings, text="Get Settings from URL", command=fnGetFromURL)
btnGetFromURL.pack(side=tk.TOP, fill=tk.X)

frmSendingRate = ttk.LabelFrame(frmDetails, text="Sending Rate")
frmSendingRate.pack(side=tk.TOP, fill=tk.X)

varSendingRate = tk.IntVar()
varSendingRate.set(180)
ttk.Radiobutton(frmSendingRate, text="30s (Non-Recruitment Telegram)", variable=varSendingRate, value=30).pack(side=tk.TOP, anchor=tk.W)
ttk.Radiobutton(frmSendingRate, text="180s (Recruitment Telegram)", variable=varSendingRate, value=180).pack(side=tk.TOP, anchor=tk.W)

frmCustomRate = ttk.Frame(frmSendingRate)
frmCustomRate.pack(side=tk.TOP, anchor=tk.W)

ttk.Radiobutton(frmCustomRate, text="Custom Rate:", variable=varSendingRate, value=0).pack(side=tk.LEFT)

txtCustomRate = tk.Text(frmCustomRate, height=1, width=3)
txtCustomRate.pack(side=tk.LEFT)

ttk.Label(frmCustomRate, text="s (This may violate the API Terms of Service!)").pack(side=tk.LEFT)

varCampaignEnabled = tk.IntVar()
varCampaignEnabled.set(1)
ttk.Checkbutton(frmDetails, text="Campaign Enabled", variable=varCampaignEnabled).pack(side=tk.TOP, anchor=tk.W)

varCampaignDryRun = tk.IntVar()
varCampaignDryRun.set(0)
ttk.Checkbutton(frmDetails, text="Dry Run (Don't actually send any telegrams)", variable=varCampaignDryRun).pack(side=tk.TOP, anchor=tk.W)

# ---------------------------- BOTTOM PANEL ----------------------------

frmBottom = ttk.Frame(root)
frmBottom.pack(side=tk.BOTTOM, fill=tk.X)

frmControls = ttk.Frame(frmBottom)
frmControls.pack(side=tk.LEFT)

btnStart = ttk.Button(frmControls, text="Start", command=fnStart)
btnStart.pack(side=tk.TOP)

btnStop = ttk.Button(frmControls, text="Stop", command=fnStop, state=tk.DISABLED)
btnStop.pack(side=tk.TOP)

frmLog = ttk.Frame(frmBottom)
frmLog.pack(side=tk.RIGHT, fill=tk.X, expand=tk.YES)

txtLog = tkinter.scrolledtext.ScrolledText(frmLog, height=5, state=tk.DISABLED)
txtLog.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

root.mainloop()
