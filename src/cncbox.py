import os, wx
import sys, inspect
import configparser

cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
	sys.path.insert(0, cmd_folder)
	
from gcframe import GcFrame
import box
from images import Images
from circledlg import CircleDlg
from rectangledlg import RectangleDlg
from gcodedlg import GCodeDlg

weightSingle = 10;
weightDouble = 16;

DIMFORMAT = "%8.2f"
BUTTONDIM = (56, 56)
BTNSPACING = 10
SECTION = "cncbox"
FNSETTINGS = "cncbox.ini"

TITLE = "Tabbed Box G Code Generator"

class Settings:
	def __init__(self, rootDir):
		self.boxDirectory = os.getcwd()
		self.gcodeDirectory = os.getcwd()
		
		config = configparser.ConfigParser()
		config.read(FNSETTINGS)
		if config.has_section(SECTION):
			for n, v in config.items(SECTION):
				if n == "boxdirectory":
					self.boxDirectory = v
				elif n == "gcodedirectory":
					self.gcodeDirectory = v
		
	def saveSettings(self):
		config = configparser.ConfigParser()
		config.add_section(SECTION)
		config.set(SECTION, 'boxdirectory', self.boxDirectory)
		config.set(SECTION, 'gcodedirectory', self.gcodeDirectory)
		
		with open(FNSETTINGS, 'w') as configfile:
			config.write(configfile)

class MainFrame(wx.Frame):
	def __init__(self):
		
		self.objectName = ""
		
		self.modified = False
		self.settings = Settings(cmd_folder)
		
		self.mainModelShowing = False
		
		wx.Frame.__init__(self, None, size=(700, 2000), title=TITLE, style=wx.TAB_TRAVERSAL+wx.DEFAULT_FRAME_STYLE)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.SetBackgroundColour("white")
		self.Show()
		
		self.Bind(wx.EVT_KEY_DOWN, self.keyDown)
		self.Bind(wx.EVT_KEY_UP, self.keyUp)
		self.Bind(wx.EVT_CHAR, self.keyChar)
		
		self.fileName = None
		
		self.currentFace = box.FACE_TOP
		self.hiLite = [ 0, 0, 0, 0, 0, 0 ]
		self.toolrad = 1.5
		self.circles = []
		self.rects = []
		
		self.bx = box.box(100, 200, 200, 6)
		
		self.images = Images(os.path.join(cmd_folder, "images"))
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.AddSpacer(20)
		
		ovsizer = wx.BoxSizer(wx.VERTICAL)
		ohsizer = wx.BoxSizer(wx.HORIZONTAL)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		sbox = wx.StaticBox(self, -1, "Box Dimensions")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
		
		t = wx.StaticText(self, wx.ID_ANY, "Height: ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.bx.Height, size=(70, -1), style=wx.TE_RIGHT)
		self.tcHeight = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextHeight)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer(30)
		hb.Add(t, 0, wx.TOP|wx.LEFT, 10)
		hb.Add(tc, 0, wx.TOP|wx.LEFT, 10)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer(10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Width: ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.bx.Width, size=(70, -1), style=wx.TE_RIGHT)
		self.tcWidth = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextWidth)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer(30)
		hb.Add(t, 0, wx.TOP|wx.LEFT, 10)
		hb.Add(tc, 0, wx.TOP|wx.LEFT, 10)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer(10)
		
		t = wx.StaticText(self, wx.ID_ANY, "Depth: ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.bx.Depth, size=(70, -1), style=wx.TE_RIGHT)
		self.tcDepth = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextDepth)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer(30)
		hb.Add(t, 0, wx.TOP|wx.LEFT, 10)
		hb.Add(tc, 0, wx.TOP|wx.LEFT, 10)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer(10)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(20)
		
		t = wx.StaticText(self, wx.ID_ANY, "Wall Thickness: ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.bx.Wall, size=(70, -1), style=wx.TE_RIGHT)
		self.tcWall = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextWall)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer(30)
		hb.Add(t, 0, wx.TOP|wx.LEFT, 10)
		hb.Add(tc, 0, wx.TOP|wx.LEFT, 10)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer(10)
			
		sbox = wx.StaticBox(self, -1, "Tool Radius Relief")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		self.rbRlfNone = wx.RadioButton(self, wx.ID_ANY, " None ", style = wx.RB_GROUP, size=(110, -1) )
		self.rbRlfHeight = wx.RadioButton(self, wx.ID_ANY, " Tab/Slot Height ", size=(110, -1) )
		self.rbRlfWidth = wx.RadioButton(self, wx.ID_ANY, " Tab/Slot Width ", size=(110, -1) )
		bmNone = wx.StaticBitmap(self, wx.ID_ANY, self.images.pngNone)
		bmHRlf = wx.StaticBitmap(self, wx.ID_ANY, self.images.pngHrelief)
		bmWRlf = wx.StaticBitmap(self, wx.ID_ANY, self.images.pngWrelief)

		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(self.rbRlfNone, 1, wx.TOP, 18)
		hb.Add(bmNone)
		self.Bind(wx.EVT_RADIOBUTTON, self.onNoRelief, self.rbRlfNone)
		staticboxsizer.Add(hb)
		
		staticboxsizer.AddSpacer(10)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(self.rbRlfHeight, 1, wx.TOP, 18)
		hb.Add(bmHRlf)
		self.Bind(wx.EVT_RADIOBUTTON, self.onHRelief, self.rbRlfHeight)
		staticboxsizer.Add(hb)
		
		staticboxsizer.AddSpacer(10)
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(self.rbRlfWidth, 1, wx.TOP, 18)
		hb.Add(bmWRlf)
		self.Bind(wx.EVT_RADIOBUTTON, self.onWRelief, self.rbRlfWidth)
		staticboxsizer.Add(hb)
		
		staticboxsizer.AddSpacer(10)
		t = wx.StaticText(self, wx.ID_ANY, "Tool Radius: ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.toolrad, size=(70, -1), style=wx.TE_RIGHT)
		self.tcToolRad = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextToolRad)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer(30)
		hb.Add(t, 0, wx.TOP|wx.LEFT, 10)
		hb.Add(tc, 0, wx.TOP|wx.LEFT, 10)
		staticboxsizer.Add(hb)
		
		staticboxsizer.AddSpacer(10)
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(20)
		
		ohsizer.Add(vsizer)
		ohsizer.AddSpacer(20)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		sbox = wx.StaticBox(self, -1, "Front/Back to Left/Right Joints")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		self.rbFSTabs = wx.RadioButton(self, wx.ID_ANY, " Front/Back Tabs ", style = wx.RB_GROUP )
		self.rbFSSlots = wx.RadioButton(self, wx.ID_ANY, " Front/Back Slots " )
		staticboxsizer.Add(self.rbFSTabs)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbFSSlots)
		self.Bind(wx.EVT_RADIOBUTTON, self.onFSTabs, self.rbFSTabs)
		self.Bind(wx.EVT_RADIOBUTTON, self.onFSSlots, self.rbFSSlots)
		
		t = wx.StaticText(self, wx.ID_ANY, "Number of Tabs/Slots:")
		sc = wx.SpinCtrl(self, wx.ID_ANY, "count", size=(50, -1))
		sc.SetRange(0, 20)
		sc.SetValue(0)
		self.scFSCount = sc
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(t, 1, wx.TOP, 3)
		sz.AddSpacer(10)
		sz.Add(sc)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(sz)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinFSCount, sc)
		
		t = wx.StaticText(self, wx.ID_ANY, "Tab/Slot length:")
		sc = wx.SpinCtrl(self, wx.ID_ANY, "length", size=(50, -1))
		sc.SetRange(1, 30)
		sc.SetValue(10)
		self.scFSLength = sc
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(t, 1, wx.TOP, 3)
		sz.AddSpacer(10)
		sz.Add(sc)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(sz)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinFSLength, sc)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(10)
		
		sbox = wx.StaticBox(self, -1, "Front/Back to Top/Bottom Joints")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		self.rbFTBTabs = wx.RadioButton(self, wx.ID_ANY, " Front/Back Tabs ", style = wx.RB_GROUP )
		self.rbFTBSlots = wx.RadioButton(self, wx.ID_ANY, " Front/Back Slots " )
		staticboxsizer.Add(self.rbFTBTabs)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbFTBSlots)
		self.Bind(wx.EVT_RADIOBUTTON, self.onFTBTabs, self.rbFTBTabs)
		self.Bind(wx.EVT_RADIOBUTTON, self.onFTBSlots, self.rbFTBSlots)
		
		t = wx.StaticText(self, wx.ID_ANY, "Number of Tabs/Slots:")
		sc = wx.SpinCtrl(self, wx.ID_ANY, "count", size=(50, -1))
		sc.SetRange(0, 20)
		sc.SetValue(0)
		self.scFTBCount = sc
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(t, 1, wx.TOP, 3)
		sz.AddSpacer(10)
		sz.Add(sc)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(sz)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinFTBCount, sc)
		
		t = wx.StaticText(self, wx.ID_ANY, "Tab/Slot length:")
		sc = wx.SpinCtrl(self, wx.ID_ANY, "length", size=(50, -1))
		sc.SetRange(1, 30)
		sc.SetValue(10)
		self.scFTBLength = sc
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(t, 1, wx.TOP, 3)
		sz.AddSpacer(10)
		sz.Add(sc)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(sz)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinFTBLength, sc)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(10)
		
		sbox = wx.StaticBox(self, -1, "Left/Right to Top/Bottom Joints")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		self.rbSTBTabs = wx.RadioButton(self, wx.ID_ANY, " Left/Right Tabs ", style = wx.RB_GROUP )
		self.rbSTBSlots = wx.RadioButton(self, wx.ID_ANY, " Left/Right Slots " )
		staticboxsizer.Add(self.rbSTBTabs)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(self.rbSTBSlots)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSTBTabs, self.rbSTBTabs)
		self.Bind(wx.EVT_RADIOBUTTON, self.onSTBSlots, self.rbSTBSlots)
		
		t = wx.StaticText(self, wx.ID_ANY, "Number of Tabs/Slots:")
		sc = wx.SpinCtrl(self, wx.ID_ANY, "count", size=(50, -1))
		sc.SetRange(0, 20)
		sc.SetValue(0)
		self.scSTBCount = sc
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(t, 1, wx.TOP, 3)
		sz.AddSpacer(10)
		sz.Add(sc)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(sz)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinSTBCount, sc)
		
		t = wx.StaticText(self, wx.ID_ANY, "Tab/Slot length:")
		sc = wx.SpinCtrl(self, wx.ID_ANY, "length", size=(50, -1))
		sc.SetRange(1, 30)
		sc.SetValue(10)
		self.scSTBLength = sc
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(t, 1, wx.TOP, 3)
		sz.AddSpacer(10)
		sz.Add(sc)
		staticboxsizer.AddSpacer(10)
		staticboxsizer.Add(sz)
		self.Bind(wx.EVT_SPINCTRL, self.onSpinSTBLength, sc)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(10)
		
		
		
		sbox = wx.StaticBox(self, -1, "Blind Faces")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
		v1sz = wx.BoxSizer(wx.VERTICAL)
		v2sz = wx.BoxSizer(wx.VERTICAL)
		
		v1sz.AddSpacer(10)
		v2sz.AddSpacer(10)

		self.cbTopBlind = wx.CheckBox(self, wx.ID_ANY, " Top")
		self.Bind(wx.EVT_CHECKBOX, self.onCheckBlind, self.cbTopBlind)
		v1sz.Add(self.cbTopBlind)
		self.cbBottomBlind = wx.CheckBox(self, wx.ID_ANY, " Bottom")
		self.Bind(wx.EVT_CHECKBOX, self.onCheckBlind, self.cbBottomBlind)
		v2sz.Add(self.cbBottomBlind)

		self.cbLeftBlind = wx.CheckBox(self, wx.ID_ANY, " Left")
		self.Bind(wx.EVT_CHECKBOX, self.onCheckBlind, self.cbLeftBlind)
		v1sz.Add(self.cbLeftBlind)
		self.cbRightBlind = wx.CheckBox(self, wx.ID_ANY, " Right")
		self.Bind(wx.EVT_CHECKBOX, self.onCheckBlind, self.cbRightBlind)
		v2sz.Add(self.cbRightBlind)
		
		self.cbFrontBlind = wx.CheckBox(self, wx.ID_ANY, " Front")
		self.Bind(wx.EVT_CHECKBOX, self.onCheckBlind, self.cbFrontBlind)
		v1sz.Add(self.cbFrontBlind)
		self.cbBackBlind = wx.CheckBox(self, wx.ID_ANY, " Back")
		self.Bind(wx.EVT_CHECKBOX, self.onCheckBlind, self.cbBackBlind)
		v2sz.Add(self.cbBackBlind)
		
		staticboxsizer.AddSpacer(20)
		staticboxsizer.Add(v1sz)
		staticboxsizer.Add(v2sz)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer(10)
		
	
		ohsizer.Add(vsizer)
		ovsizer.Add(ohsizer)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bNew = wx.BitmapButton(self, wx.ID_ANY, self.images.pngNew, size=BUTTONDIM)
		self.bNew.SetToolTip("Create a new box")
		btnSizer.Add(self.bNew, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.bNewPressed, self.bNew)
		
		self.bLoad = wx.BitmapButton(self, wx.ID_ANY, self.images.pngLoad, size=BUTTONDIM)
		self.bLoad.SetToolTip("Load box parameters")
		btnSizer.Add(self.bLoad, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.bLoadPressed, self.bLoad)
		
		self.bSave = wx.BitmapButton(self, wx.ID_ANY, self.images.pngSave, size=BUTTONDIM)
		self.bSave.SetToolTip("Save box parameters")
		btnSizer.Add(self.bSave, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		
		self.bSaveAs = wx.BitmapButton(self, wx.ID_ANY, self.images.pngSaveas, size=BUTTONDIM)
		self.bSaveAs.SetToolTip("Save as")
		btnSizer.Add(self.bSaveAs, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.bSaveAsPressed, self.bSaveAs)
		
		btnSizer.AddSpacer(30)

		self.bCircle = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCircles, size=BUTTONDIM)
		self.bCircle.SetToolTip("Manage Circular Openings")
		btnSizer.Add(self.bCircle, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.bCirclePressed, self.bCircle)

		self.bRects = wx.BitmapButton(self, wx.ID_ANY, self.images.pngRectangles, size=BUTTONDIM)
		self.bRects.SetToolTip("Manage Rectangular Openings")
		btnSizer.Add(self.bRects, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.bRectanglePressed, self.bRects)
		
		btnSizer.AddSpacer(30)

		self.bGCode = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGcode, size=BUTTONDIM)
		self.bGCode.SetToolTip("Generate G Code")
		btnSizer.Add(self.bGCode, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.bGCodePressed, self.bGCode)

		ovsizer.Add(btnSizer)
		ovsizer.AddSpacer(10)

		sizer.Add(ovsizer)
		sizer.AddSpacer(20)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(100)
		self.rbTop = wx.RadioButton(self, wx.ID_ANY, " Top ", style = wx.RB_GROUP )
		self.rbBottom = wx.RadioButton(self, wx.ID_ANY, " Bottom " )
		self.rbLeft = wx.RadioButton(self, wx.ID_ANY, " Left " )
		self.rbRight = wx.RadioButton(self, wx.ID_ANY, " Right " )
		self.rbFront = wx.RadioButton(self, wx.ID_ANY, " Front " )
		self.rbBack = wx.RadioButton(self, wx.ID_ANY, " Back " )
		vsizer.Add(self.rbTop)
		vsizer.AddSpacer(20)
		vsizer.Add(self.rbBottom)
		vsizer.AddSpacer(20)
		vsizer.Add(self.rbLeft)
		vsizer.AddSpacer(20)
		vsizer.Add(self.rbRight)
		vsizer.AddSpacer(20)
		vsizer.Add(self.rbFront)
		vsizer.AddSpacer(20)
		vsizer.Add(self.rbBack)
		self.Bind(wx.EVT_RADIOBUTTON, self.onFaceSelected, self.rbTop )
		self.Bind(wx.EVT_RADIOBUTTON, self.onFaceSelected, self.rbBottom )
		self.Bind(wx.EVT_RADIOBUTTON, self.onFaceSelected, self.rbLeft )
		self.Bind(wx.EVT_RADIOBUTTON, self.onFaceSelected, self.rbRight )
		self.Bind(wx.EVT_RADIOBUTTON, self.onFaceSelected, self.rbFront )
		self.Bind(wx.EVT_RADIOBUTTON, self.onFaceSelected, self.rbBack )
		
		sizer.Add(vsizer)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(10)
		
		self.lblHiLite = wx.StaticText(self, wx.ID_ANY, " "*50, style=wx.ALIGN_CENTRE_HORIZONTAL)
		vsizer.Add(self.lblHiLite,
				flag=wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(10)

		self.gcf = GcFrame(self)
		vsizer.Add(self.gcf)
		
		vsizer.AddSpacer(10)
		
		optsizer = wx.BoxSizer(wx.HORIZONTAL)
		optsizer.AddSpacer(50)

		self.cbGrid = wx.CheckBox(self, wx.ID_ANY, "Draw Grid")
		optsizer.Add(self.cbGrid)
		self.cbGrid.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.onCbGrid, self.cbGrid)
		optsizer.AddSpacer(10)

		self.cbPath = wx.CheckBox(self, wx.ID_ANY, "Path Only")
		optsizer.Add(self.cbPath)
		self.cbPath.SetValue(False)
		self.Bind(wx.EVT_CHECKBOX, self.onCbPath, self.cbPath)
		optsizer.AddSpacer(10)
		
		vsizer.Add(optsizer)
		vsizer.AddSpacer(10)
		
		sizer.Add(vsizer)
		sizer.AddSpacer(10)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		self.bZoomIn = wx.BitmapButton(self, wx.ID_ANY, self.images.pngZoomin, size=BUTTONDIM)
		self.bZoomIn.SetToolTip("Zoom In")
		vsizer.Add(self.bZoomIn)
		self.Bind(wx.EVT_BUTTON, self.bZoomInPressed, self.bZoomIn)

		vsizer.AddSpacer(10)
		
		self.bZoomOut = wx.BitmapButton(self, wx.ID_ANY, self.images.pngZoomout, size=BUTTONDIM)
		self.bZoomOut.SetToolTip("Zoom Out")
		vsizer.Add(self.bZoomOut)
		self.Bind(wx.EVT_BUTTON, self.bZoomOutPressed, self.bZoomOut)

		vsizer.AddSpacer(30)
		
		self.bhlForward = wx.BitmapButton(self, wx.ID_ANY, self.images.pngForward, size=BUTTONDIM)
		self.bhlForward.SetToolTip("HiLite Forward")
		vsizer.Add(self.bhlForward)
		self.Bind(wx.EVT_BUTTON, self.onHiLiteForward, self.bhlForward)

		vsizer.AddSpacer(10)
		
		self.bhlBackward = wx.BitmapButton(self, wx.ID_ANY, self.images.pngBackward, size=BUTTONDIM)
		self.bhlBackward.SetToolTip("HiLite Backward")
		vsizer.Add(self.bhlBackward)
		self.Bind(wx.EVT_BUTTON, self.onHiLiteBackward, self.bhlBackward)

		vsizer.AddSpacer(50)

		self.bReset = wx.BitmapButton(self, wx.ID_ANY, self.images.pngReset, size=BUTTONDIM)
		self.bReset.SetToolTip("Reset View")
		vsizer.Add(self.bReset)
		self.Bind(wx.EVT_BUTTON, self.bResetPressed, self.bReset)
		
		
		vsizer.AddSpacer(10)
		
		sizer.Add(vsizer)
		sizer.AddSpacer(10)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
		self.render()
		
	def keyDown(self, evt):
		print("key down")
		evt.Skip()
		
	def keyUp(self, evt):
		print("key up")
		
	def keyChar(self, evt):
		print("key char: (", evt.GetKeyCode(), ")")
		
	def updateFileName(self, fn):
		self.fileName = fn
		self.displayTitle()
		
	def setModified(self, flag=True):
		if flag == self.modified:
			return
		
		self.modified = flag
		self.displayTitle()
		
	def displayTitle(self):
		txt = TITLE
			
		if self.fileName is not None:
			txt += "  -  " + self.fileName
			
		if self.modified:
			txt += ' *'

		self.SetLabel(txt)
		
	def render(self, fc=None):
		fx = None
		if fc is None:
			fx = self.currentFace
			
		if fc == "Top":
			fx = box.FACE_TOP
		elif fc == "Bottom":
			fx = box.FACE_BOTTOM
		elif fc == "Left":
			fx = box.FACE_LEFT
		elif fc == "Right":
			fx = box.FACE_RIGHT
		elif fc == "Front":
			fx = box.FACE_FRONT
		elif fc == "Back":
			fx = box.FACE_BACK

		if fx is not None:
			p, c, r = self.bx.render(fx, self.toolrad)
			if p is not None:
				self.currentFace = fx
				self.gcf.setData(p, c, r, self.toolrad, self.hiLite[fx])  
				self.updateHiLite()
				self.circles = c
				self.rects = r
			
	def onHiLiteForward(self, e):
		self.hiLite[self.currentFace] = self.gcf.hiLiteForward()
		self.updateHiLite()
			
	def onHiLiteBackward(self, e):
		self.hiLite[self.currentFace] = self.gcf.hiLiteBackward()
		self.updateHiLite()
		
	def updateHiLite(self):
		self.lblHiLite.SetLabel(self.gcf.getHiLitedSegment())
		self.Layout()
			
	def onTextHeight(self, e):
		h = self.tcHeight.GetValue()
		try:
			hv = float(h)
			if hv != self.bx.Height:
				self.bx.setHeight(hv)
				self.tcHeight.SetValue(DIMFORMAT % self.bx.Height)
				self.render();
				self.setModified()
		except:
			self.illegalTcValue("Height")
			self.tcHeight.SetValue(DIMFORMAT % self.bx.Height)
			e.Skip()
			
	def onTextWidth(self, e):
		w = self.tcWidth.GetValue()
		try:
			wv = float(w)
			if wv != self.bx.Width:
				self.bx.setWidth(wv)
				self.tcWidth.SetValue(DIMFORMAT % self.bx.Width)
				self.render();
				self.setModified()
		except:
			self.illegalTcValue("Width")
			self.tcWidth.SetValue(DIMFORMAT % self.bx.Width)
			e.Skip()
			
	def onTextDepth(self, e):
		d = self.tcDepth.GetValue()
		try:
			dv = float(d)
			if dv != self.bx.Depth:
				self.bx.setDepth(dv)
				self.tcDepth.SetValue(DIMFORMAT % self.bx.Depth)
				self.render();
				self.setModified()
		except:
			self.illegalTcValue("Depth")
			self.tcDepth.SetValue(DIMFORMAT % self.bx.Depth)
			e.Skip()
			
	def onTextWall(self, e):
		d = self.tcWall.GetValue()
		try:
			dv = float(d)
			if dv != self.bx.Wall:
				self.bx.setWall(dv, self.toolrad)
				self.tcWall.SetValue(DIMFORMAT % self.bx.Wall)
				self.render();
				self.setModified()
		except:
			self.illegalTcValue("Wall Thickness")
			self.tcWall.SetValue(DIMFORMAT % self.bx.Wall)
			e.Skip()
			
	def onTextToolRad(self, e):
		d = self.tcToolRad.GetValue()
		try:
			dv = float(d)
			self.toolrad = dv
			self.tcToolRad.SetValue(DIMFORMAT % self.toolrad)
			self.render();
		except:
			self.illegalTcValue("Tool Radius")
			self.tcToolRad.SetValue(DIMFORMAT % self.toolrad)
			e.Skip()
			
	def illegalTcValue(self, name):
		dlg = wx.MessageDialog(self,
			"Illegal value for %s.\nRetaining old value" % name,
			'Illegal value entered',
			wx.OK | wx.ICON_INFORMATION
			)
		dlg.ShowModal()
		dlg.Destroy()
			
	def onNoRelief(self, e):
		self.bx.setRelief(box.NRELIEF)
		self.setModified()
		self.render()
		
	def onHRelief(self, e):
		self.bx.setRelief(box.HRELIEF)
		self.setModified()
		self.render()
		
	def onWRelief(self, e):
		self.bx.setRelief(box.WRELIEF)
		self.setModified()
		self.render()
		
	def onFaceSelected(self, e):
		rb = e.GetEventObject()
		l = rb.GetLabel().strip()
		self.render(l)

	def onFSTabs(self, e):
		self.bx.setTabType(box.CORNER_FRONT_SIDE, box.TABS)
		self.setModified()
		self.render()
		
	def onFSSlots(self, e):
		self.bx.setTabType(box.CORNER_FRONT_SIDE, box.SLOTS)
		self.setModified()
		self.render()
		
	def onFTBTabs(self, e):
		self.bx.setTabType(box.CORNER_FRONT_TOP, box.TABS)
		self.setModified()
		self.render()
		
	def onFTBSlots(self, e):
		self.bx.setTabType(box.CORNER_FRONT_TOP, box.SLOTS)
		self.setModified()
		self.render()
		
	def onSTBTabs(self, e):
		self.bx.setTabType(box.CORNER_SIDE_TOP, box.TABS)
		self.setModified()
		self.render()
		
	def onSTBSlots(self, e):
		self.bx.setTabType(box.CORNER_SIDE_TOP, box.SLOTS)
		self.setModified()
		self.render()
		
	def onSpinFSCount(self, e):
		self.bx.setTabCount(box.CORNER_FRONT_SIDE, self.scFSCount.GetValue())
		self.setModified()
		self.render()
		
	def onSpinFSLength(self, e):
		self.bx.setTabLen(box.CORNER_FRONT_SIDE, self.scFSLength.GetValue())
		self.setModified()
		self.render()
		
	def onSpinFTBCount(self, e):
		self.bx.setTabCount(box.CORNER_FRONT_TOP, self.scFTBCount.GetValue())
		self.setModified()
		self.render()
		
	def onSpinFTBLength(self, e):
		self.bx.setTabLen(box.CORNER_FRONT_TOP, self.scFTBLength.GetValue())
		self.setModified()
		self.render()
		
	def onSpinSTBCount(self, e):
		self.bx.setTabCount(box.CORNER_SIDE_TOP, self.scSTBCount.GetValue())
		self.setModified()
		self.render()
		
	def onSpinSTBLength(self, e):
		self.bx.setTabLen(box.CORNER_SIDE_TOP, self.scSTBLength.GetValue())
		self.setModified()
		self.render()
		
	def onCheckBlind(self, e):
		self.bx.setBlindTabs([self.cbTopBlind.IsChecked(), self.cbBottomBlind.IsChecked(),
							  self.cbLeftBlind.IsChecked(), self.cbRightBlind.IsChecked(),
							  self.cbFrontBlind.IsChecked(), self.cbBackBlind.IsChecked()])
		self.setModified()
		self.render()
		
	def bZoomInPressed(self, e):
		self.gcf.zoomIn()
		
	def bZoomOutPressed(self, e):
		self.gcf.zoomOut()
		
	def bResetPressed(self, e):
		self.hiLite = [ 0, 0, 0, 0, 0, 0 ]
		self.gcf.resetView()
		
	def bGCodePressed(self, e):
		dlg = GCodeDlg(self, self.bx, self.toolrad, self.images, self.settings)
		dlg.ShowModal()
		dlg.Destroy()
		
	def bNewPressed(self, e):
		if self.modified:
			dlg = wx.MessageDialog(self, "Are you sure you want to\ncreate a new box?\nyou will lose unsaved changes",
				'Unsaved Changes', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
	
			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return
			
		self.currentFace = box.FACE_TOP
		self.hiLite = [ 0, 0, 0, 0, 0, 0 ]
		self.circles = []
		self.rects = []
		
		self.bx = box.box(100, 200, 200, 6)
		
		self.updateWidgets()
		
		self.updateFileName(None)
		self.setModified(False)
		self.render()
		
	def bLoadPressed(self, e):
		if self.modified:
			dlg = wx.MessageDialog(self, "Are you sure you want to\nload a new file?\nyou will lose unsaved changes",
				'Unsaved Changes', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
	
			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return
			
		wildcardLoad = "Box file(*.box)|*.box" 
		dlg = wx.FileDialog(
			self, message="Choose a file",
			defaultDir=self.settings.boxDirectory, 
			defaultFile="",
			wildcard=wildcardLoad,
			style=wx.FD_OPEN
			)
		path = None
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.settings.boxDirectory = os.path.dirname(path)
			self.updateFileName(path)

		dlg.Destroy()
		
		if path is None:
			return
		
		self.bx.loadBox(path, self.toolrad)
		self.currentFace = box.FACE_TOP
		self.hiLite = [ 0, 0, 0, 0, 0, 0 ]

		self.updateWidgets()	
		
		self.setModified(False)
		self.render()

	def updateWidgets(self):	
		self.tcDepth.SetValue(DIMFORMAT % self.bx.Depth)
		self.tcWidth.SetValue(DIMFORMAT % self.bx.Width)
		self.tcHeight.SetValue(DIMFORMAT % self.bx.Height)
		self.tcWall.SetValue(DIMFORMAT % self.bx.Wall)
		if self.bx.Relief == box.NRELIEF:
			self.rbRlfNone.SetValue(1)
		elif self.bx.Relief == box.WRELIEF:
			self.rbRlfWidth.SetValue(1)
		elif self.bx.Relief == box.HRELIEF:
			self.rbRlfHeight.SetValue(1)
			
		self.scFSCount.SetValue(self.bx.TabCt[box.CORNER_FRONT_SIDE])
		self.scFTBCount.SetValue(self.bx.TabCt[box.CORNER_FRONT_TOP])
		self.scSTBCount.SetValue(self.bx.TabCt[box.CORNER_SIDE_TOP])
		
		self.scFSLength.SetValue(self.bx.TabLen[box.CORNER_FRONT_SIDE])
		self.scFTBLength.SetValue(self.bx.TabLen[box.CORNER_FRONT_TOP])
		self.scSTBLength.SetValue(self.bx.TabLen[box.CORNER_SIDE_TOP])
		
		if self.bx.TabType[box.CORNER_FRONT_SIDE] == box.TABS:
			self.rbFSTabs.SetValue(1)
		else:
			self.rbFSSlots.SetValue(1)
			
		if self.bx.TabType[box.CORNER_FRONT_TOP] == box.TABS:
			self.rbFTBTabs.SetValue(1)
		else:
			self.rbFTBSlots.SetValue(1)
			
		if self.bx.TabType[box.CORNER_SIDE_TOP] == box.TABS:
			self.rbSTBTabs.SetValue(1)
		else:
			self.rbSTBSlots.SetValue(1)
			
		self.cbTopBlind.SetValue(self.bx.BlindTabs[box.FACE_TOP])
		self.cbBottomBlind.SetValue(self.bx.BlindTabs[box.FACE_BOTTOM])
		self.cbLeftBlind.SetValue(self.bx.BlindTabs[box.FACE_LEFT])
		self.cbRightBlind.SetValue(self.bx.BlindTabs[box.FACE_RIGHT])
		self.cbFrontBlind.SetValue(self.bx.BlindTabs[box.FACE_FRONT])
		self.cbBackBlind.SetValue(self.bx.BlindTabs[box.FACE_BACK])
		
	def bSavePressed(self, e):
		if self.fileName is None:
			self.bSaveAsPressed(e)
		else:
			self.doSave(self.fileName)
		
	def bSaveAsPressed(self, e):
		wildcardSave = "Box file(*.box)|*.box" 

		dlg = wx.FileDialog(
			self, message="Save file as ...", defaultDir=self.settings.boxDirectory, 
			defaultFile="", wildcard=wildcardSave, style=wx.FD_SAVE + wx.FD_OVERWRITE_PROMPT
			)
		path = None
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.settings.boxDirectory = os.path.dirname(path)

		dlg.Destroy()
		
		if path is None:
			return
		
		self.doSave(path)
		self.updateFileName(path)

	def doSave(self, path):		
		self.bx.saveBox(path)

		dlg = wx.MessageDialog(self,
			"File: %s" % path,
			'Box Parameters Saved',
			wx.OK | wx.ICON_INFORMATION
			)
		dlg.ShowModal()
		dlg.Destroy()
		self.setModified(False)
		
	def bCirclePressed(self, e):
		dlg = CircleDlg(self, self.circles, self.images)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			self.circles = dlg.circles[:]
			self.bx.setCircles(self.currentFace, self.circles)
			self.render()
		dlg.Destroy()
		
	def bRectanglePressed(self, e):
		dlg = RectangleDlg(self, self.rects, self.images)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			self.rects = dlg.rects[:]
			self.bx.setRectangles(self.currentFace, self.rects)
			self.render()
		dlg.Destroy()
		
	def onCbGrid(self, e):
		self.gcf.setGrid(self.cbGrid.IsChecked())
		
	def onCbPath(self, e):
		self.gcf.setPathOnly(self.cbPath.IsChecked())

	def onClose(self, evt):
		if self.modified:
			dlg = wx.MessageDialog(self, "Are you sure you want to exit with unsaved changes",
				'Unsaved Changes', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
	
			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return
			
		self.settings.saveSettings()
		self.Destroy()
				
class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		self.SetTopWindow(self.frame)
		return True

app = App(False)
app.MainLoop()

	
