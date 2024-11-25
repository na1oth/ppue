import wx
import pickle
from lib.char import CharWin

# Assign unique widget numbers
ID_MENU_QUIT = wx.NewIdRef()
ID_MENU_HELP = wx.NewIdRef()
ID_MENU_GUIDE = wx.NewIdRef()

class HelpWin(wx.Dialog):
	def __init__(self, parent, title):
		wx.Dialog.__init__(self, parent=parent, title=title, size=(800, 550), style=wx.DEFAULT_FRAME_STYLE)

		sz = wx.BoxSizer(wx.VERTICAL)

		data = open("help.txt", 'r').read()
		help = wx.TextCtrl(self, size=(-1, 450), value=data, style=wx.TE_MULTILINE | wx.TE_READONLY)
		btn = wx.Button(self, wx.ID_OK, label = "Close", size = (50,20), pos = (75,50))
		sz.Add(help, flag = wx.EXPAND | wx.ALL, border=5)
		sz.Add(btn, flag = wx.ALIGN_CENTER | wx.ALL, border=5)
		self.SetSizer(sz)

class CharFrame(wx.Frame):
	def __init__(self, parent, title):
		super().__init__(parent, title=title, size=(1000,1200))

		# Initial data load
		self.DATA = {}
		for file in ['caps', 'mods', 'packages', 'stats', 'POWERS', 'PERKS', 'FLAWS', 'GEAR' ]:
			self.DATA[file] = self.readData("{}.csv".format(file))
		#print(self.DATA)

		# Create character panel
		self.p = CharWin(self)

		# Create File Menu
		self.makeMenuBar()

		# Create Status Bar
		self.CreateStatusBar()

		self.Show()
		#self.p.Layout()

	def makeMenuBar(self):
		# Create spot for menu
		menuBar = wx.MenuBar()
		self.SetMenuBar(menuBar)        # Attach to frame

		# Create file menu and items for menubar
		fileMenu = wx.Menu()
		fileMenu.Append(wx.ID_NEW, "&New")
		fileMenu.Append(wx.ID_OPEN, "&Load")
		fileMenu.Append(wx.ID_SAVE, "&Save")
		fileMenu.Append(wx.ID_SAVEAS, "Save &As")
		fileMenu.AppendSeparator()
		fileMenu.Append(ID_MENU_QUIT, "&Quit")
		menuBar.Append(fileMenu, "&File")

		helpMenu = wx.Menu()
		menuBar.Append(helpMenu, "&Help")
		helpMenu.Append(ID_MENU_GUIDE, "&User Guide", )

		# Set actions
		self.Bind(wx.EVT_TOOL, self.menuDo, id=wx.ID_NEW)
		self.Bind(wx.EVT_TOOL, self.menuDo, id=wx.ID_OPEN)
		self.Bind(wx.EVT_TOOL, self.menuDo, id=wx.ID_SAVE)
		self.Bind(wx.EVT_TOOL, self.menuDo, id=wx.ID_SAVEAS)
		self.Bind(wx.EVT_TOOL, self.menuDo, id=ID_MENU_QUIT)
		self.Bind(wx.EVT_TOOL, self.helpWin, id=ID_MENU_GUIDE)
	
	def helpWin(self, e):
		a = HelpWin(self, "Usage Notes").ShowModal()

	def menuDo(self, e):
		event = e.GetId()

		# Wipe existing data
		if (event == wx.ID_NEW):
			self.p.newChar()

		# Open existing character
		elif (event == wx.ID_OPEN):
			# wipe existing data
			self.p.newChar()
			# load from savefile
			datafile = self.doFile("Open", file=self.p.PC.filename)
			# If a filename is returned, do load
			if (datafile):
				with open(datafile, 'rb') as file:
					self.p.PC = pickle.load(file)		# reverse of pickle.dumps
				file.close()
				#print(f"F: {self.p.PC.filename}\nStats: {self.p.PC.stat}\nAbil: {self.p.PC.list}\n")
			self.p.loadChar()
			
		# Save As function 
		elif (event == wx.ID_SAVE or event == wx.ID_SAVEAS):
			datafile = self.doFile("Save",file=self.p.PC.filename)
			self.p.PC.filename = datafile
			#print(f"F: {self.p.PC.filename}\nStats: {self.p.PC.stat}\nAbil: {self.p.PC.list}\n")
			# If a filename is returned, do save
			if (datafile):
				with open(datafile, 'wb') as file:
					file.write(pickle.dumps(self.p.PC))  	# reverse of pickle.loads
				file.close()

		# Exit program
		elif (event == ID_MENU_QUIT):
			print("Quit")
			self.close()
	
	def doFile(self, func, dir="./Saves", file=""):
		if (func == "Save"): 
			style = wx.FD_SAVE
		else:
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST

		openFileDialog = wx.FileDialog(self, func, defaultDir=dir, defaultFile=file, wildcard="PPUE characters (*.sav)|*.sav", style=style)
		openFileDialog.ShowModal()
		datafile = openFileDialog.GetPath()
		openFileDialog.Destroy()
		return(datafile)

	def readData(self, filename):
		info = {}

		print(filename)
		with open('data/' + filename, 'r', encoding="utf8") as fp:
			
			# Top line provides field names
			line = fp.readline()
			line = line.strip()
			field_list = line.split("|")

			line = fp.readline()
			while line:
				#print(line)
				line = line.strip()
				data = line.split("|")
				if (data[0]):
					info[data[0]] = {}
					for index in range(0, len(data)):
						info[data[0]][field_list[index]] = data[index]

				line = fp.readline()
			fp.close
			return(info)
