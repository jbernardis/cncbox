import os
import wx
import box

DEPTHFORMAT = "%8.2f"
RATEFORMAT = "%8.2f"
INTFORMAT = "%3d"
BUTTONDIM = (56, 56)
BTNSPACING = 10

VISIBLEQUEUESIZE = 21

class GCodeDlg(wx.Dialog):
	def __init__(self, parent, bx, toolrad, images, settings):
		self.parent = parent
		self.bx = bx
		self.toolrad = toolrad
		self.settings = settings
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Generate G Code")
		self.SetBackgroundColour("white")
		
		self.depthPerCut = 1.0
		self.feedG1XY = 50.0
		self.feedG1Z = 50.0
		self.feedG0XY = 70.0
		self.feedG0Z = 70.0
		self.safeZ = 1.0
		self.extraDepth = 0.5
		self.sigDigits = 4
		self.offsetX = 0
		self.offsetY = 0
		
		self.images = images
		
		dsizer = wx.BoxSizer(wx.VERTICAL)
		dsizer.AddSpacer((10, 10))
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer((20, 20))
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		
		sbox = wx.StaticBox(self, -1, "Choose face")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		staticboxsizer.AddSpacer((130,10))
		self.rbTop = wx.RadioButton(self, wx.ID_ANY, " Top ", style = wx.RB_GROUP )
		self.rbBottom = wx.RadioButton(self, wx.ID_ANY, " Bottom " )
		self.rbLeft = wx.RadioButton(self, wx.ID_ANY, " Left " )
		self.rbRight = wx.RadioButton(self, wx.ID_ANY, " Right " )
		self.rbFront = wx.RadioButton(self, wx.ID_ANY, " Front " )
		self.rbBack = wx.RadioButton(self, wx.ID_ANY, " Back " )
		staticboxsizer.Add(self.rbTop, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbBottom, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbLeft, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbRight, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbFront, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbBack, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		self.rbTop.SetValue(True)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer((20, 20))
		
		t = wx.StaticText(self, wx.ID_ANY, "Depth per Cut: ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, DEPTHFORMAT % self.depthPerCut, size=(70, -1), style=wx.TE_RIGHT)
		self.tcDPC = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextDPC)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP, 5)
		hb.Add(tc)
		vsizer.Add(hb)
		vsizer.AddSpacer((5, 5))
		
		t = wx.StaticText(self, wx.ID_ANY, "Extra Depth: ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, DEPTHFORMAT % self.extraDepth, size=(70, -1), style=wx.TE_RIGHT)
		self.tcExtraDepth = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextExtraDepth)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP, 5)
		hb.Add(tc)
		vsizer.Add(hb)
		vsizer.AddSpacer((5, 5))
		
		t = wx.StaticText(self, wx.ID_ANY, "Safe Z Height: ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, DEPTHFORMAT % self.safeZ, size=(70, -1), style=wx.TE_RIGHT)
		self.tcSafeZ = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextSafeZ)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP, 5)
		hb.Add(tc)
		vsizer.Add(hb)
		vsizer.AddSpacer((5, 5))
		
		t = wx.StaticText(self, wx.ID_ANY, "Digits/Accuracy: ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, INTFORMAT % self.sigDigits, size=(70, -1), style=wx.TE_RIGHT)
		self.tcSigDigits = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextSigDigits)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP, 5)
		hb.Add(tc)
		vsizer.Add(hb)
		vsizer.AddSpacer((5, 5))
		
		hsizer.Add(vsizer)
		hsizer.AddSpacer((20, 20))
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		
		sbox = wx.StaticBox(self, -1, "Cut direction - inside cuts")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		staticboxsizer.AddSpacer((140,10))
		self.rbICW = wx.RadioButton(self, wx.ID_ANY, " Clockwise ", style = wx.RB_GROUP )
		self.rbICCW = wx.RadioButton(self, wx.ID_ANY, " Counter Clockwise " )
		staticboxsizer.Add(self.rbICW, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbICCW, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		self.rbICW.SetValue(True)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer((20, 20))
		
		sbox = wx.StaticBox(self, -1, "Cut direction - outside cuts")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		staticboxsizer.AddSpacer((140,10))
		self.rbOCW = wx.RadioButton(self, wx.ID_ANY, " Clockwise ", style = wx.RB_GROUP )
		self.rbOCCW = wx.RadioButton(self, wx.ID_ANY, " Counter Clockwise " )
		staticboxsizer.Add(self.rbOCW, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbOCCW, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		self.rbOCCW.SetValue(True)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer((20, 20))

		sbox = wx.StaticBox(self, -1, "Origin")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		staticboxsizer.AddSpacer((140,10))
		self.rbUL = wx.RadioButton(self, wx.ID_ANY, " Upper Left ", style = wx.RB_GROUP )
		self.rbUR = wx.RadioButton(self, wx.ID_ANY, " Upper Right " )
		self.rbCTR = wx.RadioButton(self, wx.ID_ANY, " Center " )
		self.rbLL = wx.RadioButton(self, wx.ID_ANY, " Lower Left " )
		self.rbLR = wx.RadioButton(self, wx.ID_ANY, " Lower Right " )
		staticboxsizer.Add(self.rbUL, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbUR, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbCTR, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbLL, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbLR, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		self.rbCTR.SetValue(True)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer((20, 20))

		hsizer.Add(vsizer)
		hsizer.AddSpacer((20, 20))
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		
		sbox = wx.StaticBox(self, -1, "Measurement System")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

		staticboxsizer.AddSpacer((140,10))
		self.rbMetric = wx.RadioButton(self, wx.ID_ANY, " Metric ", style = wx.RB_GROUP )
		self.rbImperial = wx.RadioButton(self, wx.ID_ANY, " Imperial " )
		staticboxsizer.Add(self.rbMetric, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		staticboxsizer.Add(self.rbImperial, 1, wx.LEFT, 10)
		staticboxsizer.AddSpacer((10, 10))
		self.rbMetric.SetValue(True)
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer((20, 20))
		
		sbox = wx.StaticBox(self, -1, "Feed Rates")
		staticboxsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
		
		t = wx.StaticText(self, wx.ID_ANY, "XY (G0): ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, RATEFORMAT % self.feedG0XY, size=(70, -1), style=wx.TE_RIGHT)
		self.tcG0XY = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextG0XY)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP+wx.LEFT, 5)
		hb.Add(tc)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer((5, 5))
		
		t = wx.StaticText(self, wx.ID_ANY, "Z (G0): ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, RATEFORMAT % self.feedG0Z, size=(70, -1), style=wx.TE_RIGHT)
		self.tcG0Z = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextG0Z)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP+wx.LEFT, 5)
		hb.Add(tc)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer((5, 5))

		t = wx.StaticText(self, wx.ID_ANY, "XY (G1): ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, RATEFORMAT % self.feedG1XY, size=(70, -1), style=wx.TE_RIGHT)
		self.tcG1XY = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextG1XY)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP+wx.LEFT, 5)
		hb.Add(tc)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer((5, 5))
		
		t = wx.StaticText(self, wx.ID_ANY, "Z (G1): ", size=(80, -1))
		tc = wx.TextCtrl(self, wx.ID_ANY, RATEFORMAT % self.feedG1Z, size=(70, -1), style=wx.TE_RIGHT)
		self.tcG1Z = tc

		tc.Bind(wx.EVT_KILL_FOCUS, self.onTextG1Z)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.Add(t, 1, wx.TOP+wx.LEFT, 5)
		hb.Add(tc)
		staticboxsizer.Add(hb)
		staticboxsizer.AddSpacer((5, 15))
		
		self.cbFeed = wx.CheckBox(self, wx.ID_ANY, "Add Rates to GCode")
		self.Bind(wx.EVT_CHECKBOX, self.onCbFeed, self.cbFeed)
		self.cbFeed.SetValue(True)
		
		staticboxsizer.Add(self.cbFeed, 1, wx.LEFT, 20)
		staticboxsizer.AddSpacer((5, 5))
		
		vsizer.Add(staticboxsizer)
		vsizer.AddSpacer((20, 20))
		
		hsizer.Add(vsizer)
		hsizer.AddSpacer((20, 20))
		
		dsizer.Add(hsizer)
		dsizer.AddSpacer((20, 20))

		btnsizer = wx.BoxSizer(wx.HORIZONTAL)		

		self.bGCode = wx.BitmapButton(self, wx.ID_ANY, self.images.pngGcode, size=BUTTONDIM)
		self.bGCode.SetToolTipString("Generate G Code")
		btnsizer.Add(self.bGCode, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.doGCode, self.bGCode)

		self.bExit = wx.BitmapButton(self, wx.ID_ANY, self.images.pngExit, size=BUTTONDIM)
		self.bExit.SetToolTipString("Dismiss dialog")
		btnsizer.Add(self.bExit, 1, wx.LEFT + wx.RIGHT, BTNSPACING)
		self.Bind(wx.EVT_BUTTON, self.doExit, self.bExit)

		dsizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
		
		dsizer.AddSpacer((10,10))
		
		self.SetSizer(dsizer)  
		dsizer.Fit(self)
		
	def doExit(self, e):
		self.EndModal(wx.ID_OK)
		
	def onTextG0XY(self, e):
		d = self.tcG0XY.GetValue()
		try:
			dv = float(d)
			self.feedG0XY = dv
			self.tcG0XY.SetValue(RATEFORMAT % self.feedG0XY)

		except:
			self.illegalTcValue("Feed Rate XY (G0)")
			self.tcG0XY.SetValue(RATEFORMAT % self.feedG0XY)
			e.Skip()
		
	def onTextG0Z(self, e):
		d = self.tcG0Z.GetValue()
		try:
			dv = float(d)
			self.feedG0Z = dv
			self.tcG0Z.SetValue(RATEFORMAT % self.feedG0Z)

		except:
			self.illegalTcValue("Feed Rate Z (G0)")
			self.tcG0Z.SetValue(RATEFORMAT % self.feedG0Z)
			e.Skip()
		
	def onTextG1XY(self, e):
		d = self.tcG1XY.GetValue()
		try:
			dv = float(d)
			self.feedG1XY = dv
			self.tcG1XY.SetValue(RATEFORMAT % self.feedG1XY)

		except:
			self.illegalTcValue("Feed Rate XY (G1)")
			self.tcG1XY.SetValue(RATEFORMAT % self.feedG1XY)
			e.Skip()
		
	def onTextG1Z(self, e):
		d = self.tcG1Z.GetValue()
		try:
			dv = float(d)
			self.feedG1Z = dv
			self.tcG1Z.SetValue(RATEFORMAT % self.feedG1Z)

		except:
			self.illegalTcValue("Feed Rate Z (G1)")
			self.tcG1Z.SetValue(RATEFORMAT % self.feedG1Z)
			e.Skip()
		
	def onTextDPC(self, e):
		d = self.tcDPC.GetValue()
		try:
			dv = float(d)
			self.depthPerCut = dv
			self.tcDPC.SetValue(DEPTHFORMAT % self.depthPerCut)

		except:
			self.illegalTcValue("Depth Per Cut")
			self.tcDPC.SetValue(DEPTHFORMAT % self.depthPerCut)
			e.Skip()
		
	def onTextSafeZ(self, e):
		d = self.tcSafeZ.GetValue()
		try:
			dv = float(d)
			self.safeZ = dv
			self.tcSafeZ.SetValue(DEPTHFORMAT % self.safeZ)

		except:
			self.illegalTcValue("Safe Z Height")
			self.tcSafeZ.SetValue(DEPTHFORMAT % self.safeZ)
			e.Skip()
		
	def onTextExtraDepth(self, e):
		d = self.tcExtraDepth.GetValue()
		try:
			dv = float(d)
			self.extraDepth = dv
			self.tcExtraDepth.SetValue(DEPTHFORMAT % self.extraDepth)

		except:
			self.illegalTcValue("Depth Extra Depth")
			self.tcExtraDepth.SetValue(DEPTHFORMAT % self.extraDepth)
			e.Skip()
		
	def onTextSigDigits(self, e):
		d = self.tcSigDigits.GetValue()
		try:
			dv = int(d)
			if dv <= 0:
				self.illegalTcValue("Digits of Accuracy")
				self.tcSigDigits.SetValue(INTFORMAT % self.sigDigits)
			else:
				self.sigDigits = dv
				self.tcSigDigits.SetValue(INTFORMAT % self.sigDigits)

		except:
			self.illegalTcValue("Digits of Accuracy")
			self.tcSigDigits.SetValue(INTFORMAT % self.sigDigits)
			e.Skip()
			
	def illegalTcValue(self, name):
		dlg = wx.MessageDialog(self,
			"Illegal value for %s.\nRetaining old value" % name,
			'Illegal value entered',
			wx.OK | wx.ICON_INFORMATION
			)
		dlg.ShowModal()
		dlg.Destroy()
			
	def onCbFeed(self, e):
		f = self.cbFeed.GetValue()
		self.tcG0XY.Enable(f)
		self.tcG0Z.Enable(f)
		self.tcG1XY.Enable(f)
		self.tcG1Z.Enable(f)
		
	def doGCode(self, e):
		gcode = []
		ft = box.FACE_TOP
		if self.rbTop.GetValue():
			ft = box.FACE_TOP
		elif self.rbBottom.GetValue():
			ft = box.FACE_BOTTOM
		elif self.rbLeft.GetValue():
			ft = box.FACE_LEFT
		elif self.rbRight.GetValue():
			ft = box.FACE_RIGHT
		elif self.rbFront.GetValue():
			ft = box.FACE_FRONT
		elif self.rbBack.GetValue():
			ft = box.FACE_BACK
			
		self.offsetX = 0
		self.offsetY = 0
		
		fw, fh = self.bx.getFaceDim(ft)
		dx = fw / 2.0
		dy = fh / 2.0
		
		if self.rbUL.GetValue():
			self.offsetX = dx
			self.offsetY = -dy
		
		elif self.rbUR.GetValue():
			self.offsetX = -dx
			self.offsetY = -dy
		
		elif self.rbLL.GetValue():
			self.offsetX = dx
			self.offsetY = dy
			
		elif self.rbLR.GetValue():
			self.offsetX = -dx
			self.offsetY = dy
			
		icw = True
		if self.rbICCW.GetValue():
			icw = False
			
		ocw = True
		if self.rbOCCW.GetValue():
			ocw = False
			
		if self.rbImperial.GetValue():
			gcode.append("G20")
		else:
			gcode.append("G21")
	
		self.fmt = "%0." + str(self.sigDigits) + "f"
		self.addSpeed = self.cbFeed.GetValue()
				
		pts, crc, rct = self.bx.render(ft, self.toolrad)
		totalDepth = self.bx.Wall
		
		gcode.append(("G0 Z" + self.fmt + self.addSpeedTerm("G0Z")) % self.safeZ)
			
		steps = []
		d = self.depthPerCut
		while d < totalDepth:
			steps.append(-d)
			d += self.depthPerCut
		steps.append(-(totalDepth + self.extraDepth))
		
		if icw:
			cmd = "G2"
		else:
			cmd = "G3"

		if len(crc) > 0:
			gcode.append("; circles")		
		for c in crc:
			crad = c[1] - self.toolrad
			gcode.append(("; New circle - center (" + self.fmt + "," + self.fmt + ") radius " + self.fmt + "(" + self.fmt +")")
						 % (self.normalX(c[0][0]), self.normalY(c[0][1]), c[1], crad))
			gcode.append(("G0 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G0XY")) 
						% (self.normalX(c[0][0]), self.normalY(c[0][1] - crad)))
			for p in steps:
				gcode.append(("G1 Z" + self.fmt + self.addSpeedTerm("G1Z")) % p)
				gcode.append((cmd+" J" + self.fmt + " X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G1XY"))
						% (crad, self.normalX(c[0][0]), self.normalY(c[0][1]) - crad))
			
			gcode.append(("G0 Z" + self.fmt + self.addSpeedTerm("G0Z")) % self.safeZ)
			
		if len(rct) > 0:
			gcode.append("; rectangles")
		for r in rct:
			dx = r[1]/2.0 - self.toolrad
			dy = r[2]/2.0 - self.toolrad
			cx = r[0][0]
			cy = r[0][1]
			gcode.append(("; New rectangle - center (" + self.fmt + "," + self.fmt + ") width " + self.fmt + "(" + self.fmt +") height " + self.fmt + "(" + self.fmt +")")
						% (self.normalX(cx), self.normalY(cy), r[1], r[1]-2*self.toolrad, r[2], r[2]-2*self.toolrad))	
			if icw:
				rpts = [ [-dx, dy], [dx, dy], [dx, -dy], [-dx, -dy] ]
			else:
				rpts = [ [dx, -dy], [dx, dy], [-dx, dy], [-dx, -dy] ]

			gcode.append(("G0 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G0XY")) 
						% (self.normalX(cx-dx), self.normalY(cy-dy)))
			for p in steps:
				gcode.append(("G1 Z" + self.fmt + self.addSpeedTerm("G1Z")) % p)
				for rp in rpts:
					gcode.append(("G1 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G1XY")) 
								% (self.normalX(cx+rp[0]), self.normalY(cy+rp[1])))

			gcode.append(("G0 Z" + self.fmt + self.addSpeedTerm("G0Z")) % self.safeZ)
			
		gcode.append("; perimeter")
		if ocw:
			data = pts
		else:
			data = pts[::-1]
			
		gcode.append(("G0 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G0XY")) 
					% (self.normalX(data[0][0]), self.normalY(data[0][1])))
		
		for p in steps:
			gcode.append(("; layer at depth "+DEPTHFORMAT) % p)
			gcode.append(("G1 Z" + self.fmt + self.addSpeedTerm("G1Z")) % p)
			for d in range(1, len(data)):
				gcode.append(("G1 X" + self.fmt + " Y" + self.fmt + self.addSpeedTerm("G1XY")) 
						% (self.normalX(data[d][0]), self.normalY(data[d][1])))

		gcode.append(("G0 Z" + self.fmt + self.addSpeedTerm("G0Z")) % self.safeZ)
		self.saveGCodeFile(gcode)
		
	def saveGCodeFile(self, gcode):
		wildcardSave = "G Code file(*.nc)|*.nc" 

		dlg = wx.FileDialog(
			self, message="Save file as ...", defaultDir=self.settings.gcodeDirectory, 
			defaultFile="", wildcard=wildcardSave, style=wx.SAVE + wx.FD_OVERWRITE_PROMPT
			)
		path = None
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.settings.gcodeDirectory = os.path.dirname(path)

		dlg.Destroy()
		
		if path is None:
			return

		try:
			fp = open(path, "w")
		except:
			dlg = wx.MessageDialog(self,
				"Unable to open file: " + path,
				'Error',
				wx.OK | wx.ICON_ERROR
				)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		for g in gcode:
			fp.write("%s\n" % g)
		
		fp.close()
		dlg = wx.MessageDialog(self,
			"File: %s" % path,
			'G-Code Saved',
			wx.OK | wx.ICON_INFORMATION
			)
		dlg.ShowModal()
		dlg.Destroy()
			
	def normalX(self, x):
		return x+self.offsetX
	
	def normalY(self, y):
		return y+self.offsetY
			
	def addSpeedTerm(self, stype):
		if not self.addSpeed:
			return ""
		
		if stype == "G0XY":
			return " F"+self.fmt % self.feedG0XY
		if stype == "G0Z":
			return " F"+self.fmt % self.feedG0Z
		if stype == "G1XY":
			return " F"+self.fmt % self.feedG1XY
		if stype == "G1Z":
			return " F"+self.fmt % self.feedG1Z
		
		return ""
