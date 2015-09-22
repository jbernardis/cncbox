import os
import wx

DIMFORMAT = "%8.2f"
BUTTONDIM = (56, 56)

VISIBLEQUEUESIZE = 21

class RectangleDlg(wx.Dialog):
	def __init__(self, parent, rects, images):
		self.parent = parent
		self.rects = rects[:]
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Manage Rectangular Openings", size=(800, 804))
		self.SetBackgroundColour("white")
		
		dsizer = wx.BoxSizer(wx.HORIZONTAL)
		dsizer.AddSpacer((10, 10))
		
		self.images = images
		self.modified = False

		leftsizer = wx.BoxSizer(wx.VERTICAL)
		leftsizer.AddSpacer((10, 10))
		
		self.lbRects = RectanglesCtrl(self, self.rects, self.images)
		leftsizer.Add(self.lbRects);
		leftsizer.AddSpacer((10, 10))

		btnsizer = wx.BoxSizer(wx.HORIZONTAL)		
		btnsizer.AddSpacer((5,5))

		self.bOk = wx.BitmapButton(self, wx.ID_ANY, self.images.pngOk, size=BUTTONDIM)
		self.bOk.SetToolTipString("Dismiss dialog and save")
		btnsizer.Add(self.bOk)
		self.Bind(wx.EVT_BUTTON, self.doOk, self.bOk)
		btnsizer.AddSpacer((5,5))

		self.bCancel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BUTTONDIM)
		self.bCancel.SetToolTipString("Dismiss dialog losing changes")
		btnsizer.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.doCancel, self.bCancel)
		btnsizer.AddSpacer((5,5))

		leftsizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
		
		dsizer.Add(leftsizer)
		dsizer.AddSpacer((10,10))
		
		rightsizer = wx.BoxSizer(wx.VERTICAL)
		rightsizer.AddSpacer((10, 20))

		self.bAdd = wx.BitmapButton(self, wx.ID_ANY, self.images.pngAdd, size=BUTTONDIM)
		self.bAdd.SetToolTipString("Add a new rectangle")
		rightsizer.Add(self.bAdd)
		self.Bind(wx.EVT_BUTTON, self.doAdd, self.bAdd)
		rightsizer.AddSpacer((5,5))

		self.bEdit = wx.BitmapButton(self, wx.ID_ANY, self.images.pngEdit, size=BUTTONDIM)
		self.bEdit.SetToolTipString("Modify current rectangle")
		rightsizer.Add(self.bEdit)
		self.Bind(wx.EVT_BUTTON, self.doEdit, self.bEdit)
		self.bEdit.Enable(False)
		rightsizer.AddSpacer((5,5))

		self.bDelete = wx.BitmapButton(self, wx.ID_ANY, self.images.pngDel, size=BUTTONDIM)
		self.bDelete.SetToolTipString("Delete current rectangle")
		rightsizer.Add(self.bDelete)
		self.Bind(wx.EVT_BUTTON, self.doDelete, self.bDelete)
		self.bDelete.Enable(False)
		rightsizer.AddSpacer((5,5))

		dsizer.Add(rightsizer)
		dsizer.AddSpacer((10,10))
		
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
		dlg = SingleRectangleDlg(self, 0.0, 0.0, 10.0, 10.0, "Add", self.images)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			cx, cy, lx, ly = dlg.getData()
			dlg.Destroy()
			self.lbRects.addItem(cx, cy, lx, ly)
		else:
			dlg.Destroy()
	
	def doEdit(self, e):
		c = self.lbRects.getSelectedData()
		if c is None:
			return
		
		dlg = SingleRectangleDlg(self, c[0][0], c[0][1], c[1], c[2], "Modify", self.images)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			cx, cy, lx, ly = dlg.getData()
			dlg.Destroy()
			self.lbRects.modifySelectedItem(cx, cy, lx, ly)
		else:
			dlg.Destroy()
	
	def doDelete(self, e):
		self.lbRects.deleteItem()
		
class RectanglesCtrl(wx.ListCtrl):	
	def __init__(self, parent, rects, images):
		
		f = wx.Font(8,  wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		dc = wx.ScreenDC()
		dc.SetFont(f)
		fontHeight = dc.GetTextExtent("Xy")[1]
		
		colWidths = [160, 80, 80]
		colTitles = ["Center", "Width", "Height"]
		
		totwidth = 20;
		for w in colWidths:
			totwidth += w
		
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(totwidth, fontHeight*(VISIBLEQUEUESIZE+1)),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.parent = parent		
		self.rects = rects
		self.selectedItem = None
		self.il = wx.ImageList(16, 16)
		self.il.Add(images.pngSelected)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.SetFont(f)
		for i in range(len(colWidths)):
			self.InsertColumn(i, colTitles[i])
			self.SetColumnWidth(i, colWidths[i])
		
		self.SetItemCount(len(self.rects))
		
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
			return fmt % (self.rects[item][0][0], self.rects[item][0][1])
		else:
			return DIMFORMAT % self.rects[item][col]

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
		
		if self.selectedItem > len(self.rects):
			return
		
		del self.rects[self.selectedItem]
		self.selectedItem = None
		self.parent.setSelected(False)
		self.parent.setModified(True)
		
		self.SetItemCount(len(self.rects))
		
	def addItem(self, cx, cy, lx, ly):
		self.rects.append([[cx, cy], lx, ly])
		n = len(self.rects)
		self.assertSelect(n-1)
		self.parent.setSelected(True)
		self.parent.setModified(True)
		self.SetItemCount(n)
		
	def getSelectedData(self):
		if self.selectedItem is None:
			return None
		
		if self.selectedItem > len(self.rects):
			return None
		
		return self.rects[self.selectedItem]
		
	def modifySelectedItem(self, cx, cy, lx, ly):
		if self.selectedItem is None:
			return None
		
		if self.selectedItem > len(self.rects):
			return None
		
		self.rects[self.selectedItem] = [[cx, cy], lx, ly]
		self.RefreshItem(self.selectedItem)

class SingleRectangleDlg(wx.Dialog):
	def __init__(self, parent, cx, cy, lx, ly, title, images):
		self.parent = parent
		self.images = images
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title + " Rectangle")
		self.SetBackgroundColour("white")
		
		dlgsizer = wx.BoxSizer(wx.VERTICAL)
		dlgsizer.AddSpacer((20, 20))
		
		self.cx = cx;
		self.cy = cy;
		self.lx = lx;
		self.ly = ly
		
		t = wx.StaticText(self, wx.ID_ANY, "Center coordinate: ", size=(100, -1))
		tcx = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.cx, size=(70, -1), style=wx.TE_RIGHT)
		tcy = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.cy, size=(70, -1), style=wx.TE_RIGHT)
		self.tcX = tcx
		self.tcY = tcy

		tcx.Bind(wx.EVT_KILL_FOCUS, self.onTextX)
		tcy.Bind(wx.EVT_KILL_FOCUS, self.onTextY)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer((30, 10))
		hb.Add(t)
		hb.Add(tcx)
		hb.AddSpacer((5,5))
		hb.Add(tcy)
		hb.AddSpacer((20, 20))
		
		dlgsizer.Add(hb)
		dlgsizer.AddSpacer((20, 20))
		
		t = wx.StaticText(self, wx.ID_ANY, "Width: ", size=(100, -1))
		tclx = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.lx, size=(70, -1), style=wx.TE_RIGHT)
		self.tcLx = tclx

		tclx.Bind(wx.EVT_KILL_FOCUS, self.onTextLx)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer((30, 10))
		hb.Add(t)
		hb.Add(tclx)
		hb.AddSpacer((5,5))
		
		dlgsizer.Add(hb)
		dlgsizer.AddSpacer((10, 10))
		
		t = wx.StaticText(self, wx.ID_ANY, "Height: ", size=(100, -1))
		tcly = wx.TextCtrl(self, wx.ID_ANY, DIMFORMAT % self.ly, size=(70, -1), style=wx.TE_RIGHT)
		self.tcLy = tcly

		tcly.Bind(wx.EVT_KILL_FOCUS, self.onTextLy)
		
		hb = wx.BoxSizer(wx.HORIZONTAL)
		hb.AddSpacer((30, 10))
		hb.Add(t)
		hb.Add(tcly)
		hb.AddSpacer((5,5))
		
		dlgsizer.Add(hb)
		dlgsizer.AddSpacer((10, 10))
		
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)		
		btnsizer.AddSpacer((5,5))

		self.bOk = wx.BitmapButton(self, wx.ID_ANY, self.images.pngOk, size=BUTTONDIM)
		self.bOk.SetToolTipString("Dismiss dialog and save")
		btnsizer.Add(self.bOk)
		self.Bind(wx.EVT_BUTTON, self.doOk, self.bOk)
		btnsizer.AddSpacer((5,5))

		self.bCancel = wx.BitmapButton(self, wx.ID_ANY, self.images.pngCancel, size=BUTTONDIM)
		self.bCancel.SetToolTipString("Dismiss dialog losing changes")
		btnsizer.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.doCancel, self.bCancel)
		btnsizer.AddSpacer((5,5))
		
		dlgsizer.Add(btnsizer, 1, wx.LEFT, 50)
		dlgsizer.AddSpacer((10, 10))
		
		self.SetSizer(dlgsizer)
		self.Layout()
		self.Fit()
		
	def doOk(self, e):
		self.EndModal(wx.ID_OK)
		
	def doCancel(self, e):
		self.EndModal(wx.ID_CANCEL)
		
	def getData(self):
		return self.cx, self.cy, self.lx, self.ly

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

	def onTextLx(self, e):
		r = self.tcLx.GetValue()
		try:
			rv = float(r)
			if rv != self.lx:
				self.lx = rv
				self.tcLx.SetValue(DIMFORMAT % self.lx)
		except:
			self.illegalTcValue("Width")
			self.tcLx.SetValue(DIMFORMAT % self.lx)
			e.Skip()

	def onTextLy(self, e):
		r = self.tcLy.GetValue()
		try:
			rv = float(r)
			if rv != self.ly:
				self.ly = rv
				self.tcLy.SetValue(DIMFORMAT % self.ly)
		except:
			self.illegalTcValue("Height")
			self.tcLy.SetValue(DIMFORMAT % self.ly)
			e.Skip()
			
	def illegalTcValue(self, name):
		dlg = wx.MessageDialog(self,
			"Illegal value for %s.\nRetaining old value" % name,
			'Illegal value entered',
			wx.OK | wx.ICON_INFORMATION
			)
		dlg.ShowModal()
		dlg.Destroy()




