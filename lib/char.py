import math
import re
import wx 
import wx.adv
import wx.lib.mixins.listctrl as listmix
from types import SimpleNamespace
from wx.lib.agw import ultimatelistctrl as ULC
#import wx.dataview as dv

d = ["key", "lvl", "alt", "modlist", "pv", "notes", "source", "type" ]
sources = ["Innate", "Magic", "Psychic", "Super", "Tech", "Trained"]
width = 200

'''
To be done
- Print
- Attributes derived from powers
- How to do martial arts (strike defaults to 1/2 Agility)
- getBase should resolve power levels

'''

##################################################
class EditItemDiag(wx.Dialog):
	def __init__(self, parent, row, object):
		wx.Dialog.__init__(self, parent=parent, size=(600, 500), style=wx.DEFAULT_FRAME_STYLE)
		
		# Set up variables for object
		self.CharWin = parent		# CharWin class object
		self.PC = parent.PC		# CharInfo class object
		self.LC = object		# ULC object
		self.DATA = parent.DATA		# Data files
		self.box = {}			# Boxes widget
		self.w = {}			# widget dict
		self.py = object.GetItemPyData(row) # Smuggled py data
		self.row = self.py.row		# make row variale avaiable
		self.area = self.py.area	# section
		self.rData = self.PC.list[self.py.area][self.row] 	# copy of row data
		self.key = self.rData[d.index("key")]			# name of trait
		self.base = int(self.CharWin.getBase(self.key, self.area))

		# Set diag colors 
		self.SetFont(self.CharWin.font['bold'])			# Default to bold font
		self.SetBackgroundColour(self.CharWin.font["white"])	# Default to white background

		# Create main sizer
		self.SetTitle(f"Edit {self.key}")
		vsz = wx.BoxSizer(wx.VERTICAL)
		gbs = wx.GridBagSizer(vgap=0)
		vsz.Add(gbs, flag=wx.ALL | wx.EXPAND, border = 5)
		self.SetSizer(vsz)
		row = 0

		# Create first section which shows how the ability will be presented.
		gbs.Add(self.mkHeader(" AS SHOWN "), pos=(row,0), span=(1,2), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
		row += 1
		hrow = wx.BoxSizer(wx.HORIZONTAL)
		self.w['pv'] = wx.TextCtrl(self, size=(45, -1), value="" , style=wx.NO_BORDER | wx.TE_READONLY | wx.TE_CENTRE )	
		self.w['pv'].SetBackgroundColour(self.CharWin.font["white"])	# Default to white background
		hrow.Add(self.w['pv'])

		self.w['lbl'] = wx.TextCtrl(self, size=(520, -1), value="", style=wx.NO_BORDER | wx.TE_READONLY | wx.ALIGN_LEFT )
		self.w['lbl'].SetBackgroundColour(self.CharWin.font["white"])	# Default to white background
		hrow.Add(self.w['lbl'], flag=wx.EXPAND)
		gbs.Add(hrow, pos=(row,0), span=(1,2), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
		row += 1
		
		# Notes Entry (applies to all abilities) 
		gbs.Add(self.mkHeader(" Notes: "), pos=(row,0), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
		self.w['notes'] = wx.TextCtrl(self, size=(200, -1), value=self.rData[d.index("notes")], style = wx.ALIGN_LEFT)
		self.w['notes'].Bind(wx.EVT_TEXT, lambda event, widget = "notes" : self.setFromWidget(event, widget ))
		gbs.Add(self.w['notes'], pos=(row,1), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
		row +=1

		# level Adjustment
		if ("PER" in self.DATA[self.area][self.key] and float(self.DATA[self.area][self.key]["PER"]) > 0):
			header = self.mkHeader(" Adjust Level: ")
			gbs.Add(header, pos=(row,0), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
			self.w['spin'] = wx.SpinButton(self, size=(50, -1), style=wx.SP_HORIZONTAL)
			self.w['spin'].SetRange(1, int(self.DATA['caps'][self.PC.stat['caps']['val']]['LVL']) - self.base )
			self.w['spin'].Bind(wx.EVT_SPIN, lambda event, widget = "lvl" : self.setFromWidget(event, widget ))
			gbs.Add(self.w['spin'], pos=(row,1), flag = wx.ALIGN_CENTRE_VERTICAL)
			row += 1

		if (self.area == "POWERS"):
			gbs.Add(self.mkHeader(" Source: "), pos=(row,0), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
			self.w['src'] = wx.ComboBox(self, size=(width*2, -1), choices=sources, style=wx.CB_DROPDOWN | wx.CB_READONLY)
			self.w['src'].Bind(wx.EVT_COMBOBOX, lambda event, widget = "source" : self.setFromWidget(event, widget ))
			gbs.Add(self.w['src'], pos=(row,1), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
			row += 1

			gbs.Add(self.mkHeader(" Pick Pros/Cons: "), pos=(row,0), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
			self.w['mods'] = wx.ComboBox(self, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
			self.w['mods'].Bind(wx.EVT_COMBOBOX, lambda event, widget = "mods" : self.setFromWidget(event, widget ))
			gbs.Add(self.w['mods'], pos=(row,1), flag = wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
			row += 1


		self.w['modlist'] = wx.adv.EditableListBox(self, size=(width*2, -1), label="Pros/Cons Selected", style=wx.adv. EL_ALLOW_NEW |
			wx.adv.EL_ALLOW_EDIT | wx.adv.EL_ALLOW_DELETE)
		#self.w['modlist'].SetStrings(["1", "2", "3"])
		events =  [ wx.EVT_LIST_DELETE_ITEM, wx.EVT_LIST_END_LABEL_EDIT]
		for evt in events:
			self.w['modlist'].Bind(evt, self.updateModlist)
		gbs.Add(self.w['modlist'], pos=(row,0), span=(1, 2), flag = wx.EXPAND)
		row += 1

		#wx.EVT_LIST_BEGIN_DRAG, wx.EVT_LIST_BEGIN_RDRAG, wx.EVT_LIST_BEGIN_LABEL_EDIT, wx.EVT_LIST_END_LABEL_EDIT, wx.EVT_LIST_DELETE_ITEM, 
		#wx.EVT_LIST_DELETE_ALL_ITEMS, wx.EVT_LIST_ITEM_SELECTED, wx.EVT_LIST_ITEM_DESELECTED, wx.EVT_LIST_ITEM_ACTIVATED, wx.EVT_LIST_ITEM_FOCUSED, 
		#wx.EVT_LIST_ITEM_MIDDLE_CLICK, wx.EVT_LIST_ITEM_RIGHT_CLICK, wx.EVT_LIST_KEY_DOWN, wx.EVT_LIST_INSERT_ITEM, wx.EVT_LIST_COL_CLICK, 
		#wx.EVT_LIST_COL_RIGHT_CLICK, wx.EVT_LIST_COL_BEGIN_DRAG, wx.EVT_LIST_COL_DRAGGING, wx.EVT_LIST_COL_END_DRAG, wx.EVT_LIST_CACHE_HINT,
		#wx.EVT_LIST_ITEM_CHECKED, wx.EVT_LIST_ITEM_UNCHECKED 

		# Buttons to close the window
		closeButton = wx.Button(self, label='Done')
		closeButton.Bind(wx.EVT_BUTTON, self.onClose)
		gbs.Add(closeButton, pos=(row,0), span=(1,2), flag=wx.ALIGN_CENTRE)

		gbs.AddGrowableCol(1)
		# Update with current values 
		self.updateDiag()
		# Fix layout?
		self.Layout()

	def updateModlist(self, event):
		wx.CallAfter(self.AfterRun)
	
	def AfterRun(self):
		print(f"Modlist {self.w['modlist'].GetStrings()}")
		self.rData[d.index('modlist')] = ("; ".join(self.w['modlist'].GetStrings()))  + "; "
		self.PC.list[self.py.area][self.row] = self.rData
		self.updateDiag()

	def updateDiag(self):
		# Get and update label which also updates PV
		label = self.CharWin.doRowDesc(self.area, self.rData)
		self.w['lbl'].SetValue(label)

		# Get and update cost
		pv = self.CharWin.totalRowPV(self.area, self.rData)
		self.w['pv'].SetValue(f'[{pv:.12g}]')
		if (float(pv) == 0): self.w['pv'].Hide()

		# Update choices for mods
		if (self.area == "POWERS"): 
			# Update Source
			self.w['src'].SetValue(self.rData[d.index("source")])
			# Update Mods
			mods = self.CharWin.createList("mods", kFilter=self.key, tFilter=self.rData[d.index("type")])
			mods[0] = "ADD PRO/CON"
			self.w['mods'].SetItems(mods)
			self.w['mods'].SetValue("ADD PRO/CON")

		modlist = self.rData[d.index("modlist")].strip("; $")
		modlist = modlist.split("; ")
		if (modlist):
		        self.w['modlist'].SetStrings(modlist)

		# Set Spinner to Lvl if it's an adjustable ability
		if ("PER" in self.DATA[self.area][self.key] and float(self.DATA[self.area][self.key]["PER"]) > 0): self.w['spin'].SetValue(int(self.rData[d.index("lvl")]))

		
	def setFromWidget(self, event, widget):
		if (widget == "mods"):
			#print(f"{widget} = {event.EventObject.GetValue()}")
			mod = event.EventObject.GetValue()
			# strip notes
			mod = re.sub(' \(.+$', "", mod)
			# reverse cost/name
			mod = mod.split("] ")
			mod = f'{mod[1]} {mod[0]}]'
			if (self.rData[d.index("modlist")] == ""): 
				self.rData[d.index("modlist")] = mod
			else:
				self.rData[d.index("modlist")] += f"{mod}; "
		else: 
			self.rData[d.index(widget)] = event.EventObject.GetValue()

		# Update PC and Diag window
		self.PC.list[self.py.area][self.row] = self.rData
		self.updateDiag()
		
	def mkHeader(self, title):
		header = wx.StaticText(self, label=title)
		header.SetBackgroundColour(self.CharWin.font["blue"]) 
		header.SetForegroundColour(self.CharWin.font["white"]) 
		return(header)
		
	def onClose(self, e):
		self.Destroy()


##################################################
class ELC(ULC.UltimateListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
	def __init__(self, parent, size=wx.DefaultSize):
		ULC.UltimateListCtrl.__init__(self, parent, size=size, agwStyle=ULC.ULC_REPORT | ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL | 
			ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | ULC.ULC_NO_HEADER | ULC.ULC_EDIT_LABELS)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

##################################################
class LC(ULC.UltimateListCtrl, listmix.ColumnSorterMixin, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, columns, size=(-1, -1)):
		ULC.UltimateListCtrl.__init__(self, parent, size=size, agwStyle=ULC.ULC_REPORT | ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL |
			ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | ULC.ULC_NO_HEADER)
		listmix.ColumnSorterMixin.__init__(self, columns)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

		self.itemDataMap = {}
	#	self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumn)

	def OnColumn(self, e):
		self.Refresh()
		e.Skip()

	def GetListCtrl(self):
		return self

##################################################
class CharInfo():
	def __init__(self, parent):
		self.DATA		= parent.DATA
		self.filename		= ""
		self.image		= "icons/hero.png"
		self.stat		= {}
		self.list		= {}

	def clearData(self):
		self.filename 		= ""
		self.image		= "icons/hero.png"
		self.stat.clear() 
		for area in self.list.keys():
			self.list[area].clear()

		# Assign initial values
		for stat in self.DATA['stats'].keys():
			self.stat[stat] = {}
			self.stat[stat]['LVL'] = self.DATA['stats'][stat]['BASE']
			self.stat[stat]['pv'] = int(self.DATA['stats'][stat]['ADD'])
			self.stat[stat]['val'] = ""
			# Assign val to BASE to make packages and caps work properly
			# Fix TEXT stats and INFO (for combobox)
			if (self.DATA['stats'][stat]['TYPE'] == "TEXT" or self.DATA['stats'][stat]['TYPE'] == "INFO"):
				self.stat[stat]['val'] = self.DATA['stats'][stat]['BASE']
		self.stat['packages']['val'] = self.DATA['stats']['packages']['BASE']

##################################################
class CharWin(wx.ScrolledWindow):
	def __init__(self, parent):
		wx.ScrolledWindow.__init__(self,parent)

		# Dictionaries
		self.dropdown	= {}	# Trait lists
		self.grid	= {}	# drop down selection storage
		self.lbl	= {}	# Widgets used as labels
		self.spin	= {}	# Spin widgets

		# Loaded datafiles
		self.parent		= parent
		self.DATA 		= parent.DATA
		for list in ['POWERS', 'PERKS', "FLAWS", "GEAR"]:
			self.dropdown[list] = self.createList(list)

		# Font & color dictionary
		fontname = wx.MODERN
		fontname = wx.ROMAN
		self.font		= {}
		self.font['black'] 	= wx.Colour(0,0,0)
		self.font['blue'] 	= wx.Colour(33,70,150)
		self.font['grey']	= wx.Colour(230, 230, 230)
		self.font['red']	= wx.Colour(255, 0, 0)
		self.font['white'] 	= wx.Colour(255,255,255)

		self.font['bold']	= wx.Font(8, fontname, wx.NORMAL, wx.BOLD)
		self.font['normal']	= wx.Font(8, fontname, wx.NORMAL, wx.NORMAL)
		self.font['small']	= wx.Font(6, fontname, wx.NORMAL, wx.BOLD)
		self.font['big']	= wx.Font(16, fontname, wx.NORMAL, wx.BOLD)

		# Class to store char info for saving / printing
		self.PC 		= CharInfo(self)
		self.newChar()

		# Set a few defaults
		self.areas	= [ 'POWERS', 'PERKS', 'FLAWS', 'GEAR' ]
		self.indent = 10			# Left indent
		self.row = 0				# Row tracker
		self.rtObjSz = 40			# Spinner size
		self.SetFont(self.font['bold'])		# Default to bold font
		self.SetForegroundColour(self.font['black'])
		self.SetBackgroundColour(self.font['white'])

		# Create a sizer to store everything
		self.mainSizer = wx.GridBagSizer(0,0)
		self.SetSizerAndFit(self.mainSizer)

		self.addSpacer() # Blue line between system menu and char name

		# Two character name fields, hero aligned left and real name aligned right
		self.lbl['cname'] = wx.TextCtrl(self, size=(width, -1), value=self.PC.stat['cname']['val'], style = wx.ALIGN_LEFT)
		self.lbl['cname'].SetFont(self.font['big'])
		self.lbl['cname'].SetForegroundColour(self.font['blue'])
		self.lbl['cname'].Bind(wx.EVT_TEXT, lambda event, trait="cname": self.setStatFromWidget(event, trait))
		self.lbl['rname'] = wx.TextCtrl(self, size=(width, -1), value=self.PC.stat['rname']['val'], style = wx.ALIGN_RIGHT | wx.NO_BORDER)
		self.lbl['rname'].SetForegroundColour(self.font['blue'])
		self.lbl['rname'].Bind(wx.EVT_TEXT, lambda event, trait="rname": self.setStatFromWidget(event, trait))
		self.mainSizer.Add(self.lbl['cname'], pos=(self.row,0), span=(1,4), flag=wx.EXPAND )
		self.mainSizer.Add(self.lbl['rname'], pos=(self.row,4), span=(1,2), flag=wx.EXPAND | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=self.indent)
		self.row += 1

		self.addSpacer() # Blue line between system menu and char name

		image_start = self.row # Save row where the image should start

		# Do character selection sections, values to be filled later
		for section in ["INFO", "ABILITIES", "TALENTS"]:
			self.row = self.drawTwoCol(section, self.row)
		self.row = self.drawOneCol("POWERS", 2, 0, self.row)
		self.drawOneCol("FLAWS", 1, 0, self.row)
		self.row = self.drawOneCol("PERKS", 1, 2, self.row)

		#self.lbl['pic'] = wx.StaticBitmap(self, -1, wx.Bitmap(self.PC.image, wx.BITMAP_TYPE_ANY))
		self.lbl['bmp'] = wx.Bitmap(self.PC.image, wx.BITMAP_TYPE_ANY)
		self.lbl['pic'] = wx.BitmapButton(self, -1, self.lbl['bmp'])
		self.setImage()	
		self.lbl['pic'].Bind(wx.EVT_BUTTON, self.doImage)
		self.mainSizer.Add(self.lbl['pic'], span=(self.row-image_start,2), pos=(image_start,4), flag=wx.EXPAND | wx.LEFT, border=self.indent)

		# Add spot for freeform text 
		self.sectionHeader("NOTES", 2, 0)
		self.lbl['notes'] = wx.TextCtrl(self, size=(width*2, -1), value=self.PC.stat['notes']['val'], style=wx.TE_MULTILINE)
		self.lbl['notes'].Bind(wx.EVT_TEXT, lambda event, trait="notes": self.setStatFromWidget(event, trait))
		self.mainSizer.Add(self.lbl['notes'], span=(1,4), pos=(self.row+1, 0), flag=wx.EXPAND | wx.LEFT, border=self.indent)

		self.drawOneCol("GEAR", 1, 4, self.row)

		# Both data columns grow
		self.mainSizer.AddGrowableCol(0)
		self.mainSizer.AddGrowableCol(2)

		# Assign panel events (which affect specific widgets)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onActivated)
		#self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onRightClick)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelected)

		# Recalculate and redraw as necessary
		self.reDrawChar()

	### Set new image 
	def doImage(self, event):
		wildcard = "Image files (*.png)|*.png"
		dialog = wx.FileDialog(None, "Choose a file", wildcard=wildcard, style=wx.FD_OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			self.PC.image = dialog.GetPath()
			self.setImage()
		dialog.Destroy() 

	### Updates the bitmap in the panel to current self.PC.image file
	def setImage(self):
		self.lbl['bmp'].LoadFile(self.PC.image, wx.BITMAP_TYPE_ANY)
		self.lbl['bmp'].Rescale(self.lbl['bmp'], (417, 773))
		self.lbl['pic'].SetBitmap( self.lbl['bmp'] )

	### Create lists for drop downs
	def createList(self, dict, tFilter="", kFilter=""):
		temp = [" ADD {}".format(dict)]
		for key in self.DATA[dict]:
			# Get notes text ready
			notes = self.DATA[dict][key].get("NOTES", "")
			if ("/" in notes): notes = ""

			power = self.DATA[dict][key].get("POWER", "")
			type = self.DATA[dict][key].get("TYPE", "")

			# Filtering
			if ( ( power != "" and kFilter != "" ) and kFilter != power ): continue # skip to next
			#if ( ( type != ""  or (tFilter != "" ) and tFilter != self.DATA[dict][key]["TYPE"]) ): continue # Skip to next

			cost = ""
			if (dict == "mods" or dict == "POWERS" or dict == "PERKS"): cost = "[0] "	# Display cost even if 0
			if (float(self.DATA[dict][key].get("ADD", 0)) != 0) : cost = f'[{self.DATA[dict][key]["ADD"]}] '
			if (float(self.DATA[dict][key].get("PER", 0)) != 0) : cost = f'[{self.DATA[dict][key]["PER"]}^] '

			show = key
			if (self.DATA[dict][key].get("RESOLVE", "") == "1"): show=f"{key}*"
			if (type and notes):
				show = f"{cost}{show} ({type}; {notes})"
			elif (type):
				show = f"{cost}{show} ({type})"
			elif (notes):
				show = f"{cost}{show} ({notes})"
			else:
				show = f"{cost}{show}"
			
			temp.append(show)
		return(temp)

	### Set Sheet to Defaults
	def newChar(self):
		# Clear char dicionaries
		self.PC.clearData()

		# Verify widgets have been created
		if (self.spin):
			self.setImage()
			self.reDrawChar()

	### set image and redraw rest of fields
	def loadChar(self):
		self.setImage()

		self.reDrawChar()

	### Draw section for powers, perks, flaws, gear
	def drawOneCol(self,section, span, col, row):
		self.sectionHeader(section, span, col)
		row += 1

		# Put both widgets in a sizer
		hsz = wx.BoxSizer(wx.VERTICAL)
		# Create dropdown for selecting things to add
		selCombo = wx.Choice(self, size=(width, -1), choices=self.dropdown[section])
		selCombo.SetSelection(0)
		selCombo.Bind(wx.EVT_CHOICE, lambda event, section=section: self.doChoice(event, section))
		hsz.Add(selCombo, flag=wx.EXPAND)

		self.PC.list[section] = []
		# Init grid section 
		if (section == "POWERS" or section == "PERKS"):
			count = 3 # Delete, PV, Desc
		else: 
			count = 2 # Delete, Desc
		height = 125
		if (section == "POWERS"): height = 300
		if (section == "GEAR"): height = 200
		self.grid[section] = LC(self, count, size=(-1, height))
		for idx in range(count-1):
			self.grid[section].InsertColumn(idx, "", format=ULC.ULC_FORMAT_CENTRE)
		self.grid[section].InsertColumn(count-1, "")
		self.grid[section].SetColumnWidth(0, 20)
		hsz.Add(self.grid[section], flag=wx.EXPAND)
		if (section == "POWERS" or section == "PERKS"): self.grid[section].SetColumnWidth(1, 45)

		# Add DV to mainsizer
		self.mainSizer.Add(hsz, pos=(row,col), span=(1,span*2), flag=wx.EXPAND | wx.LEFT, border=self.indent)
		#self.mainSizer.Add(selCombo, pos=(row,col), span=(1,span*2), flag=wx.EXPAND | wx.LEFT, border=self.indent)
		#self.mainSizer.Add(self.grid[section], pos=(row,col), span=(1,span*2), flag=wx.EXPAND | wx.LEFT, border=self.indent)
		row += 1

		return(row)

	### Draw section for info, abilities, and talents
	def drawTwoCol(self,section, row):
		col = 0
		self.sectionHeader(section, 2, col)
		row += 1

		for key in self.DATA['stats']:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			if (section != self.DATA['stats'][key]['TYPE']): continue	
			if (key == "caps" or key == "packages"):
				
				self.lbl[key] = wx.ComboBox(self, width, size=(width, -1), value=self.PC.stat[key]['val'], choices=list(self.DATA[key].keys()), style=wx.CB_DROPDOWN | wx.CB_READONLY)
				self.lbl[key].Bind(wx.EVT_COMBOBOX, lambda event, trait=key: self.setStatFromWidget(event, trait))
				hsz.Add(self.lbl[key], flag=wx.EXPAND)
			else:
				self.traitname = wx.TextCtrl(self, size=(width/2, -1), value=key, style=wx.NO_BORDER | wx.TE_READONLY | wx.ALIGN_LEFT )
				if (key == "Total"): self.traitname.SetValue("Point Total")
				self.lbl[key] = wx.TextCtrl(self, size=(width/2, -1), value=self.PC.stat[key]['val'], style=wx.NO_BORDER | wx.TE_READONLY | wx.ALIGN_LEFT )

				hsz.Add(self.traitname)
				hsz.Add(self.lbl[key], flag=wx.EXPAND)

				#self.lbl[key].SetBackgroundColour("white")

			if (section == "INFO" or section == "TEXT"):
				#self.mainSizer.Add(self.lbl[key], pos=(row,col), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.LEFT, border=self.indent)
				self.mainSizer.Add(hsz, pos=(row,col), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.LEFT, border=self.indent)
			else:
				# Set abilities and talents with a min/max spinner
				self.spin[key] = wx.SpinButton(self, size=(self.rtObjSz, -1), style=wx.SP_HORIZONTAL)
				self.spin[key].SetValue(1)	# Gets min/max/value gets reset after first spin press
				self.spin[key].SetMin(1)	# Gets min/max/value gets reset after first spin press
				self.spin[key].Bind(wx.EVT_SPIN, lambda event, trait=key: self.setStatFromWidget(event, trait))
				self.mainSizer.Add(hsz, pos=(row,col), flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.LEFT, border=self.indent)
				self.mainSizer.Add(self.spin[key], pos=(row,col+1), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT )
			if (col == 0):
				col = 2
			else:
				col = 0
				row += 1
		return(row)

	### Draw section headers w/optional point value
	def sectionHeader(self, section, span, col):
		lbl = wx.TextCtrl(self, size=(-1, -1), value=section, style=wx.NO_BORDER | wx.TE_READONLY | wx.ALIGN_LEFT )
		lbl.SetForegroundColour(self.font['white'])
		lbl.SetBackgroundColour(self.font['blue'])

		self.lbl[section] = wx.TextCtrl(self, size=(self.rtObjSz, -1), value="", style=wx.NO_BORDER | wx.TE_READONLY | wx.ALIGN_RIGHT )
		self.lbl[section].SetForegroundColour(self.font['white'])
		self.lbl[section].SetBackgroundColour(self.font['blue'])

		self.mainSizer.Add(lbl, pos=(self.row,col), span=(1,span), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.TOP, border=self.indent)
		self.mainSizer.Add(self.lbl[section], pos=(self.row,col+span), span=(1,span), flag=wx.EXPAND | wx.TOP, border=self.indent )

	### Draw a horizontal line
	def addSpacer(self):
		# Division Line
		linebar = wx.StaticText(self, size=(200,5), label="")
		linebar.SetBackgroundColour(self.font['blue'])
		self.mainSizer.Add(linebar, pos=(self.row, 0), span=(1,6), flag=wx.EXPAND )
		self.row += 1

	### Refresh all the widgets
	def reDrawChar(self):
		minSpin  = {}
		minSpin['ABILITIES'] = int(self.DATA['packages'][self.PC.stat['packages']['val']]['ABILITIES'])
		minSpin['TALENTS'] = int(self.DATA['packages'][self.PC.stat['packages']['val']]['TALENTS'])
		maxSpin = int(self.DATA['caps'][self.PC.stat['caps']['val']]['LVL'])
		super_stat = {}
		edge_bonus = 0
		resolve = 0
		total = 0
		top = 0
		typetotal = {}								

		# Dictionary for totals
		for key in self.DATA['stats'].keys():
			type = self.DATA['stats'][key]['TYPE']
			if (type not in typetotal): typetotal[type] = 0
			#if (self.DATA['stats'][key]['TYPE'] == "INFO"): continue	# Skip INFO

			# Types that use spin buttons
			if (type == "ABILITIES" or type == "TALENTS"):
				self.spin[key].SetRange(minSpin[type], maxSpin)
				# Verify min and max fall in the allowed ranged
				self.PC.stat[key]['LVL'] = max(minSpin[type], int(self.PC.stat[key]['LVL']))
				self.PC.stat[key]['LVL'] = min(maxSpin, int(self.PC.stat[key]['LVL']))
				# Set display again in case it changed
				#self.PC.stat[key]['val'] = "{0: <13} {1: ^9}".format(key, str(self.PC.stat[key]['LVL']) + "d")
				self.PC.stat[key]['val'] = f"{str(self.PC.stat[key]['LVL'])}d"
				# Set widgets again in case they changed
				self.spin[key].SetValue(int(self.PC.stat[key]['LVL']))
				val = int(self.PC.stat[key]['LVL']) - minSpin[type]
				if (val == 0): showval = ""	
				if (val > 0): showval = f' [{val}]'
				self.lbl[key].SetValue(f"{self.PC.stat[key]['val']}{showval}")
				typetotal[type] += int(self.PC.stat[key]['LVL']) - minSpin[type]
				# Set top to highest ability
				if (type == "ABILITIES" and int(self.PC.stat[key]['LVL']) > top): top = int(self.PC.stat[key]['LVL'])
			# Non spin buttons
			else:
				self.lbl[key].SetValue(self.PC.stat[key]['val'])
				if (key == "packages"):
					typetotal[type] = int(self.DATA[key][self.PC.stat[key]['val']]['ADD'])
		for type in typetotal.keys():
			# Update subtotal widget for section
			if (type != "TEXT"): self.lbl[type].SetValue("{} pts".format(typetotal[type]))
			# Update Total
			total += typetotal[type] 

		for section in self.grid:
			# Delete all rows in grid
			for item in range(self.grid[section].GetItemCount()):
				self.grid[section].DeleteItem(0)
			# Add rows from self.PC.list data
			subtotal = 0
			for idx, row in enumerate(self.PC.list[section]):
				pv = self.updateRow(idx, section)
				if (pv != ""): subtotal += float(pv)
				# Test for resolve affecting abilities
				if (section == "FLAWS"):
					if (int(self.DATA[section][row[0]].get("RESOLVE", 0)) == 1): resolve += 1
				if (section == "POWERS"):
					if (row[0] == "Lightning Reflexes"): edge_bonus += 6
					affect = int(self.DATA[section][row[0]].get("RESOLVE", 0))
					if (affect == 1): 
						resolve += row[d.index("lvl")]
					if (affect > 1): 
						lvl = self.getBase(row[0], section) + row[d.index("lvl")]
						if ( lvl > top ): top = lvl
			if (subtotal > 0): self.lbl[section].SetValue(f"{subtotal:.12g} pts")
			if (subtotal == 0): self.lbl[section].SetValue("")
			total += subtotal

		# Set Edge
		edge = int(self.PC.stat['Perception']['LVL']) + max(int(self.PC.stat['Agility']['LVL']),int(self.PC.stat['Intellect']['LVL']))
		self.PC.stat['Edge']['val'] = f"{edge + edge_bonus}"
		self.PC.stat['Edge']['LVL'] = edge + edge_bonus
		self.lbl['Edge'].SetValue(self.PC.stat['Edge']['val'])

		# Set Health
		health = math.ceil( (int(self.PC.stat['Toughness']['LVL']) + max(int(self.PC.stat['Might']['LVL']),int(self.PC.stat['Willpower']['LVL'])))/2 )
		self.PC.stat['Health']['val'] = f"{health}"
		self.PC.stat['Health']['LVL'] = health
		self.lbl['Health'].SetValue(self.PC.stat['Health']['val'])

		# Set total and resolve
		resolve += (maxSpin - top) * 2
		self.lbl['Resolve'].SetValue(f"{resolve}")
		self.lbl['Total'].SetValue(f"{total:.12g}")

		self.Layout()

	# Set stat dictionary from widget value
	def setStatFromWidget(self, event, trait):
		self.PC.stat[trait]['val'] = event.EventObject.GetValue()
		if (event.GetEventType() != wx.EVT_TEXT._getEvtType()):
			self.PC.stat[trait]['LVL'] = event.EventObject.GetValue()
			self.reDrawChar()

	# Add to listcntl from combobox
	def doChoice(self, event, section):
		# Get index of selecion choice
		sel = event.EventObject.GetSelection()
		# Force back to ADD line
		event.EventObject.SetSelection(0)
		# if not ADD line
		if ( sel != 0 ):
			key = event.EventObject.GetString(sel)
			key = re.sub('\[.+\] ', "", key)
			key = re.sub('\*', "", key)
			key = re.sub(' \(.+$', "", key)
			key = re.sub(':.+$', "", key)
			self.PC.list[section].append([""] * len(d))
			self.PC.list[section][-1][d.index("key")] = key

		# Update sections
		self.reDrawChar()

	# Take row info, do necessary calc, and put it into the grid
	def updateRow(self, row, section):
		# Create a shorter path to the row data
		rData = self.PC.list[section][row]
		# If dict item not found for key, make a stub entry to pull blank data from
		if (rData[0] not in self.DATA[section]):  self.DATA[section][rData[0]] = {}


		# Assign level to 1 if empty, otherwise use lvl value
		if (rData[d.index("lvl")] == ""): rData[d.index("lvl")] = 1 
		
		# Assign type and source if this is a power, and the source is blank
		if (section == "POWERS" and rData[d.index("source")] == ""):
			rData[d.index("source")] = "Super"

		# Assign type for later use and add type to modlist
		rData[d.index("type")] = self.DATA[section][rData[d.index('key')]].get("TYPE", "")
		if (rData[d.index("modlist")] == ""): 
			rData[d.index("modlist")] =  f'{rData[d.index("type")]}; '
			notes = self.DATA[section][rData[d.index('key')]].get("NOTES", "")
			if (notes and "/" not in notes): rData[d.index("modlist")] += f"{notes}; " 

		# Set Desc 
		desc = self.doRowDesc(section, rData)

		# Start off row with delete button
		button = wx.Button(self.grid[section], size=(20,20), label="X", style=wx.BORDER_NONE)
		#button.SetFont(self.font["big"])
		button.SetBackgroundColour(self.font["white"])
		button.SetForegroundColour(self.font["red"])
		button.Bind(wx.EVT_BUTTON, lambda event, row=row, section=section: self.onDelRow(event, row, section))

		# Show desc and delete button
		self.grid[section].Append( [""] * self.grid[section].GetColumnCount() ) 
		self.grid[section].SetItemWindow( row, col=0, wnd=button )
		self.grid[section].SetStringItem( row, self.grid[section].GetColumnCount()-1, desc )	
		# Assign sorting info
		self.grid[section].itemDataMap[row] = [""] * self.grid[section].GetColumnCount()
		self.grid[section].itemDataMap[row][0] = "0"
		self.grid[section].itemDataMap[row][1] = "0"
		self.grid[section].itemDataMap[row][self.grid[section].GetColumnCount()-1] = desc
		self.grid[section].SetItemData(row, row)
		self.grid[section].SetItemPyData(row, SimpleNamespace(area=section, row=row))

		if (section == "POWERS" or section == "PERKS"):
			# Get PV and show in pts area
			rData[d.index("pv")] = self.totalRowPV(section, rData) # Set PV
			self.grid[section].SetStringItem( row, 1,  f'[{rData[d.index("pv")]:.12g}]' )

		self.grid[section].SortListItems( self.grid[section].GetColumnCount()-1 )	# Sort by last column
		# Assign list back to original location 
		self.PC.list[section][row] = rData
		#if (section == "POWERS" or section == "PERKS"): self.grid[section].SetColumnWidth(1, wx.LIST_AUTOSIZE)

		return(rData[d.index("pv")])

	def totalRowPV(self, section, rData):
		if ("ADD" in self.DATA[section][rData[d.index('key')]]): 
			add = float(self.DATA[section][rData[d.index('key')]]['ADD']) 
			per = float(self.DATA[section][rData[d.index('key')]]['PER'])
			modlist = rData[d.index("modlist")].split("; ")
			for mod in modlist:
				if (mod == "" or "[" not in mod): continue

				is_test = mod[ mod.find('[')+1 : mod.find(']') ]
				if ("^" in is_test):
					is_test = is_test.strip("^")
					per += float( is_test )
				else:
					add += float( is_test )
				#add += float( self.DATA["mods"][mod].get('ADD', 0) )
				#is_add = re.search(r'\[(\-?\d+)\]', mod).group(1)
				#is_per = re.search(r'\[(\-?\d+\\)\]', mod).group(1)
				#mod = re.sub(r' \[.+?\]', "", mod)
				#print(f'{mod} Add {is_add} Per {is_per}')
				#print(f'{mod} Per {re.match("[(\d+)\\]", mod)}')
				#add += float( self.DATA["mods"][mod].get('ADD', 0) )
				#per += float( self.DATA["mods"][mod].get('PER', 0) )
			# Do minimums -> add can't go below 1 and per can't be under 1/2 lvls 
			if (per < 1 and float(self.DATA[section][rData[d.index('key')]]['PER']) != 0): per = .5
			total = add + per * rData[d.index('lvl')]
			if (total <= 0): total = 1
		else: 
			total = 0
		return(total)


	# Get base level for powers and perks
	def getBase(self, key, section):
		# Get Base for ability
		if ("BASE" in self.DATA[section][key]):
			base = self.DATA[section][key]["BASE"]
		else:
			base = "0"

		# Resolve Stat: into numbers
		result = re.search(r"Stat:(\w+) ", base)
# Resolve Powers
		if (result): base = re.sub(r"{}".format(result.group(0)), "{} ".format(self.PC.stat[result.group(1)]['LVL']), base) 
		# return math evaluated string
		return(math.ceil(eval(base)))

	# Create the ability description from list data	
	def doRowDesc(self, section, rData):
		# Start description field with ability key
		desc = rData[d.index('key')]
		# Add * to flaws that give resolve at the start of each adventure
		if ("RESOLVE" in self.DATA[section][rData[d.index('key')]] and  self.DATA[section][rData[d.index('key')]]['RESOLVE'] == "1" ): desc += "*"
		# Add level information to powers and perks with levels
		if ( "PER" in self.DATA[section][rData[d.index('key')]] and self.DATA[section][rData[d.index('key')]]['PER'] != "0" ): 
			base = self.getBase(rData[d.index('key')], section)
			if (section == "POWERS"): desc += f" {base + rData[d.index('lvl')]}d"
			if (section == "PERKS"): desc += f" {base + rData[d.index('lvl')]}"

		modlist = re.sub(r'; $', "", rData[d.index("modlist")])
		source = rData[d.index("source")]
		notes = self.DATA[section][rData[d.index('key')]].get("NOTES", "")
		if ("/" in notes):  
			# Get note for ability level. Really should account for and prior to ; base, but no power has those yet.
			notes = notes.split("/")
			notes = notes[int(rData[d.index("lvl")])-1]
		else:
			notes = ""

		# Notes = per level effects, source only for powers, modlist for all user editted stuff
		if (notes and source and modlist):
			desc += f" ({notes}; {source}; {modlist})"
		elif (source and modlist):
			desc += f" ({source}; {modlist})"
		elif (modlist):
			desc += f" ({modlist})"

		# Add user notes
		if (rData[d.index("notes")]): desc += f': {rData[d.index("notes")]}'

		return(desc)

	# Delete a row.  Updates stats, empties and recreates lists 
	def onDelRow(self, event, row, section):
		print(f"Pre {self.PC.list[section]}")
		self.PC.list[section].pop(row)
		print(f"Post {self.PC.list[section]}")
		self.reDrawChar()

	# Double click to edit
	def onActivated(self, event):
		print ("Double click")
		a = EditItemDiag(self, event.GetIndex(), event.EventObject).ShowModal()
		self.reDrawChar()

	# Single click to edit
	def onSelected(self, event):
		print ("Select click")
		a = EditItemDiag(self, event.GetIndex(), event.EventObject).ShowModal()
		self.reDrawChar()

'''
		# nameText.Bind(wx.EVT_SET_FOCUS, lambda event, item=item: self.onEditItem(event, item))

	def onRightClick(self, event):
		# Get index for id
		idx = event.GetIndex()
		event.EventObject.Select(idx, on=True)

		# Create Popup for Edit(?) and Delete
		self.selected_obj = event
		self.popupmenu = wx.Menu()
		self.popupmenu.Append(-1, "Delete")
		self.Bind(wx.EVT_MENU, self.onContextDel)
		self.PopupMenu(self.popupmenu, event.GetPoint())
		self.popupmenu.Destroy()

	def onContextDel(self, event):
		# check event ID
		idx = self.selected_obj.GetIndex()
		self.selected_obj.EventObject.DeleteItem(idx)
		
'''
