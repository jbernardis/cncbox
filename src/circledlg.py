import os
import wx

DIMFORMAT = "%8.2f"
BUTTONDIM = (56, 56)

VISIBLEQUEUESIZE = 21

class CircleDlg(wx.Dialog):
	def __init__(self, parent, circles, images):
		self.parent = parent
		self.circles = circles[:]
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Manage Circular Openings", size=(800, 804))
		self.SetBackgroundColour("white")
		
		dsizer = wx.BoxSizer(wx.HORIZONTAL)
		dsizer.AddSpacer(10)
		
		self.images = images
		self.modified = False

		leftsizer = wx.BoxSizer(wx.VERTICAL)
		leftsizer.AddSpacer(10)
		
		self.lbCircles = CirclesCtrl(self, self.circles, self.images)
		leftsizer.Add(self.lbCircles);
		leftsizer.AddSpacer(10)

		btnsizer = wx.BoxSizer(wx.HORIZONTAL)		
		btnsizer.AddSpacer(5)

		self.bOk = wx.BitmapButton(self, wx.ID_ANY, self.images.pngOk, size=BUTTONDIM)
		self.bOk.SetToolTip("Dismiss dialog and save")
		btnsizer.Add(self.bOk)
		self.Bind(wx.EVT_BUTTON, self.doOk, self.bOk)
		btnsizer.AddSpacer(5)

		self.bCancel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BUTTONDIM)
		self.bCancel.SetToolTip("Dismiss dialog losing changes")
		btnsizer.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.doCancel, self.bCancel)
		btnsizer.AddSpacer(5)

		leftsizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
		
		dsizer.Add(leftsizer)
		dsizer.AddSpacer(10)
		
		rightsizer = wx.BoxSizer(wx.VERTICAL)
		rightsizer.AddSpacer(20)

		self.bAdd = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAdd, size=BUTTONDIM)
		self.bAdd.SetToolTip("Add a new circle")
		rightsizer.Add(self.bAdd)
		self.Bind(wx.EVT_BUTTON, self.doAdd, self.bAdd)
		rightsizer.AddSpacer(5)

		self.bEdit = wx.BitmapButton(self, wx.ID_ANY, self.images.pngEdit, size=BUTTONDIM)
		self.bEdit.SetToolTip("Modify current circle")
		rightsizer.Add(self.bEdit)
		self.Bind(wx.EVT_BUTTON, self.doEdit, self.bEdit)
		self.bEdit.Enable(False)
		rightsizer.AddSpacer(5)

		self.bDelete = wx.BitmapButton(self, wx.ID_ANY, self.images.pngDel, size=BUTTONDIM)
		self.bDelete.SetToolTip("Delete current circle")
		rightsizer.Add(self.bDelete)
		self.Bind(wx.EVT_BUTTON, self.doDelete, self.bDelete)
		self.bDelete.Enable(False)
		rightsizer.AddSpacer(5)

		dsizer.Add(rightsizer)
		dsizer.AddSpacer(10)
		
		self.SetSizer(dsizer)  
		dsizer.Fit(self)
		
	def setSelected(self, flag=True):
		try:
			self.bEdit.Enable(flag)
			self.bDelete.Enable(flag)
		except:
			pass
		
	def setModified(self, flag=True):
		self.modified = flag
		
	def doOk(self, e):
		self.EndModal(wx.ID_OK)
		
	def doCancel(self, e):
		if self.modified:
			dlg = wx.MessageDialog(self, "Are you sure you want to exit with unsaved changes",
				'Unsaved Changes', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
	
			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)
		
	def doAdd(self, e):
		dlg = SingleCircleDlg(self, 0.0, 0.0, 10.0, "Add", self.images)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			cx, cy, r = dlg.getData()
			dlg.Destroy()
			self.lbCircles.addItem(cx, cy, r)
		else:
			dlg.Destroy()
	
	def doEdit(self, e):
		c = self.lbCircles.getSelectedData()
		if c is None:
			return
		
		dlg = SingleCircleDlg(self, c[0][0], c[0][1], c[1], "Modify", self.images)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			cx, cy, r = dlg.getData()
			dlg.Destroy()
			self.lbCircles.modifySelectedItem(cx, cy, r)
		else:
			dlg.Destroy()
		
		
	
	def doDelete(self, e):
		self.lbCircles.deleteItem()
		
class CirclesCtrl(wx.ListCtrl):	
	def __init__(self, parent, circles, images):
		
		f = wx.Font(8,  wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		dc = wx.ScreenDC()
		dc.SetFont(f)
		fontHeight = dc.GetTextExtent("Xy")[1]
		
		colWidths = [160, 80]
		colTitles = ["Center", "Radius"]
		
		totwidth = 20;
		for w in colWidths:
			totwidth += w
		
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(totwidth, fontHeight*(VISIBLEQUEUESIZE+1)),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.parent = parent		
		self.circles = circles
		self.selectedItem = None
		self.il = wx.ImageList(16, 16)
		self.il.Add(images.pngSelected)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.SetFont(f)
		for i in range(len(colWidths)):
			self.InsertColumn(i, colTitles[i])
			self.SetColumnWidth(i, colWidths[i])
		
		self.SetItemCount(len(self.circles))
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.doListSelect)
		self.parent.setSelected(False)
		
	def doListSelect(self, evt):
		self.assertSelect(evt.m_itemIndex)
		
	def assertSelect(self, sx):
		x = self.selectedItem
		self.selectedItem = sx
		self.parent.setSelected(True)
		if x is not None:
			self.RefreshItem(x)
		
	def OnGetItemText(self, item, col):
		if col == 0:
			fmt = "(" + DIMFORMAT + ", " + DIMFORMAT + ")"
			return fmt % (self.circles[item][0][0], self.circles[item][0][1])
		else:
			return DIMFORMAT % self.circles[item][col]

	def OnGetItemImage(self, item):
		if item == self.selectedItem:
			return 0
		else:
			return -1
	
	def OnGetItemAttr(self, item):
		return None
	
	def deleteItem(self):
		if self.selectedItem is None:
			return
		
		if self.selectedItem > len(self.circles):
			return
		
		del self.circles[self.selectedItem]
		self.selectedItem = None
		self.parent.setSelected(False)
		self.parent.setModified(True)
		
		self.SetItemCount(len(self.circles))
		
	def addItem(self, cx, cy, r):
		self.circles.append([[cx, cy], r])
		n = len(self.circles)
		self.assertSelect(n-1)
		self.parent.setSelected(True)
		self.parent.setModified(True)
		self.SetItemCount(n)
		
	def getSelectedData(self):
		if self.selectedItem is None:
			return None
		
		if self.selectedItem > len(self.circles):
			return None
		
		return self.circles[self.selectedItem]
		
	def modifySelectedItem(self, cx, cy, r):
		if self.selectedItem is None:
			return None
		
		if self.selectedItem > len(self.circles):
			return None
		
		self.circles[self.selectedItem] = [[cx, cy], r]
		self.RefreshItem(self.selectedItem)

class SingleCircleDlg(wx.Dialog):
	def __init__(self, parent, cx, cy, rad, title, images):
		self.parent = parent
		self.images = images
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title + " Circle")
		self.SetBackgroundColour("white")
		
		dlgsizer = wx.BoxSizer(wx.VERTICAL)
		dlgsizer.AddSpacer(20)
		
		self.cx = cx;
		self.cy = cy;
		self.rad = rad;
		
		t = wx.StaticText(self, wx.ID_ANY, "Center coordinate: ", size=(100, -1))
		tcx = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.cx, size=(70, -1), style=wx.TE_RIGHT)
		tcy = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.cy, size=(70, -1), style=wx.TE_RIGHT)
		self.tcX = tcx
		self.tcY = tcy

		tcx.Bind(wx.EVT_KILL_FOCUS, self.onTextX)
		tcy.Bind(wx.EVT_KILL_FOCUS, self.onTextY)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer(30)
		hb.Add(t)
		hb.Add(tcx)
		hb.AddSpacer(5)
		hb.Add(tcy)
		hb.AddSpacer(20)
		
		dlgsizer.Add(hb)
		dlgsizer.AddSpacer(20)
		
		t = wx.StaticText(self, wx.ID_ANY, "Radius: ", size=(100, -1))
		tcrad = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.rad, size=(70, -1), style=wx.TE_RIGHT)
		self.tcRad = tcrad

		tcrad.Bind(wx.EVT_KILL_FOCUS, self.onTextRad)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer(30)
		hb.Add(t)
		hb.Add(tcrad)
		hb.AddSpacer(5)
		
		dlgsizer.Add(hb)
		dlgsizer.AddSpacer(10)
		
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)		
		btnsizer.AddSpacer(5)

		self.bOk = wx.BitmapButton(self, wx.ID_ANY, self.images.pngOk, size=BUTTONDIM)
		self.bOk.SetToolTip("Dismiss dialog and save")
		btnsizer.Add(self.bOk)
		self.Bind(wx.EVT_BUTTON, self.doOk, self.bOk)
		btnsizer.AddSpacer(5)

		self.bCancel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BUTTONDIM)
		self.bCancel.SetToolTip("Dismiss dialog losing changes")
		btnsizer.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.doCancel, self.bCancel)
		btnsizer.AddSpacer(5)
		
		dlgsizer.Add(btnsizer, 1, wx.LEFT, 50)
		dlgsizer.AddSpacer(10)
		
		self.SetSizer(dlgsizer)
		self.Layout()
		self.Fit()
		
	def doOk(self, e):
		self.EndModal(wx.ID_OK)
		
	def doCancel(self, e):
		self.EndModal(wx.ID_CANCEL)
		
	def getData(self):
		return self.cx, self.cy, self.rad

	def onTextX(self, e):
		x = self.tcX.GetValue()
		try:
			xv = float(x)
			if xv != self.cx:
				self.cx = xv
				self.tcX.SetValue(DIMFORMAT % self.cx)
		except:
			self.illegalTcValue("X")
			self.tcX.SetValue(DIMFORMAT % self.cx)
			e.Skip()

	def onTextY(self, e):
		y = self.tcY.GetValue()
		try:
			yv = float(y)
			if yv != self.cy:
				self.cy = yv
				self.tcY.SetValue(DIMFORMAT % self.cy)
		except:
			self.illegalTcValue("Y")
			self.tcY.SetValue(DIMFORMAT % self.cy)
			e.Skip()

	def onTextRad(self, e):
		r = self.tcRad.GetValue()
		try:
			rv = float(r)
			if rv != self.rad:
				self.rad = rv
				self.tcRad.SetValue(DIMFORMAT % self.rad)
		except:
			self.illegalTcValue("Radius")
			self.tcRad.SetValue(DIMFORMAT % self.rad)
			e.Skip()
			
	def illegalTcValue(self, name):
		dlg = wx.MessageDialog(self,
			"Illegal value for %s.\nRetaining old value" % name,
			'Illegal value entered',
			wx.OK | wx.ICON_INFORMATION
			)
		dlg.ShowModal()
		dlg.Destroy()




