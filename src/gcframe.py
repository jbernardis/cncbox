import wx, math

MAXZOOM = 10
MINZOOM = 0.5
ZOOMDELTA = 0.1

def triangulate(p1, p2):
	dx = p2[0] - p1[0]
	dy = p2[1] - p1[1]
	d = math.sqrt(dx*dx + dy*dy)
	return d

dk_Gray = wx.Colour(79, 79, 79)
lt_Gray = wx.Colour(138, 138, 138)


class GcFrame (wx.Window):
	def __init__(self, parent):
		self.parent = parent
		self.scale = 1
		self.zoom = 1
		self.offsety = 200
		self.offsetx = -200
		self.startPos = (0, 0)
		self.startOffset = (0, 0)
		self.buildarea = (400, 400)
		self.shiftX = 0
		self.shiftY = 0
		self.showGrid = True
		self.data = None
		self.circles = []
		self.rects = []
		self.toolRad = 1;
		self.hiLite = 0
		self.pathOnly = False;
		
		self.sz = [x * self.scale + 2*self.shiftX for x in self.buildarea]
		
		wx.Window.__init__(self, parent, size=self.sz)
				
		self.initBuffer()
		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
		self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
		self.Bind(wx.EVT_MOTION, self.onMotion)
		self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel, self)
		
	def onSize(self, evt):
		self.initBuffer()
		
	def onPaint(self, evt):
		dc = wx.BufferedPaintDC(self, self.buffer)
		
	def onLeftDown(self, evt):
		self.startPos = evt.GetPosition()
		self.startOffset = (self.offsetx, self.offsety)
		self.CaptureMouse()
		self.SetFocus()
		
	def onLeftUp(self, evt):
		if self.HasCapture():
			self.ReleaseMouse()
			
	def onMotion(self, evt):
		if evt.Dragging() and evt.LeftIsDown():
			x, y = evt.GetPosition()
			dx = x - self.startPos[0]
			dy = y - self.startPos[1]
			self.offsetx = self.startOffset[0] - dx/(2*self.zoom)
			self.offsety = self.startOffset[1] - dy/(2*self.zoom)
			self.redrawGraph()
			
		evt.Skip()
		
	def onMouseWheel(self, evt):
		if evt.ShiftDown(): 
			if self.model is not None:
				if evt.GetWheelRotation() < 0:
					if self.currentlx < len(self.model)-1:
						lx = self.currentlx + 1
						self.setLayer(lx)
				else:
					if self.currentlx > 0:
						lx = self.currentlx - 1
						self.setLayer(lx)
						
		else: # zoom in or out
			if evt.GetWheelRotation() < 0:
				self.zoomIn()
			else:
				self.zoomOut()
					
	def zoomIn(self):
		if (self.zoom+ZOOMDELTA) <= MAXZOOM:
			zoom = self.zoom + ZOOMDELTA
			self.setZoom(zoom)

	def zoomOut(self):
		if (self.zoom-ZOOMDELTA) >= MINZOOM:
			zoom = self.zoom - ZOOMDELTA
			self.setZoom(zoom)
			
	def resetView(self):
		self.zoom = 1
		self.offsetx = -200
		self.offsety = 200
		self.hiLite = 0
		self.redrawGraph()
		
	def refresh(self):
		self.redrawGraph()
		
	def initBuffer(self):
		w, h = self.GetClientSize()
		print(w, h)
		self.buffer = wx.Bitmap(self.sz[0], self.sz[1])
		self.redrawGraph()
		
	def setData(self, p, c, r, trad, hlseg):
		self.data = p[:]
		self.circles = c
		self.rects = r 
		self.toolRad = trad
		self.hiLite = hlseg
		self.redrawGraph()
		
	def hiLiteForward(self):
		if self.hiLite < (len(self.data)-1):
			self.hiLite += 1
			self.redrawGraph()
		return self.hiLite
	
	def hiLiteBackward(self):
		if self.hiLite > 0:
			self.hiLite -= 1
			self.redrawGraph()
		return self.hiLite
		
	def setZoom(self, zoom):
		if zoom > self.zoom:
			oldzoom = self.zoom
			self.zoom = zoom
			cx = self.offsetx + self.buildarea[0]/oldzoom/2.0
			cy = self.offsety - self.buildarea[1]/oldzoom/2.0
			self.offsetx = cx - self.buildarea[0]/self.zoom/2.0
			self.offsety = cy + self.buildarea[1]/self.zoom/2.0
		else:
			oldzoom = self.zoom
			self.zoom = zoom
			cx = self.offsetx + self.buildarea[0]/oldzoom/2.0
			cy = self.offsety - self.buildarea[1]/oldzoom/2.0
			self.offsetx = cx - self.buildarea[0]/self.zoom/2.0
			self.offsety = cy + self.buildarea[1]/self.zoom/2.0
		if self.offsetx < -self.buildarea[0]:
			self.offsetx = -self.buildarea[0]
		if self.offsetx > (self.buildarea[0]-self.buildarea[0]/self.zoom):
			self.offsetx = self.buildarea[0]-self.buildarea[0]/self.zoom
			
		if self.offsety < (-self.buildarea[1]+self.buildarea[1]/self.zoom):
			self.offsety = -self.buildarea[1]+self.buildarea[1]/self.zoom
		if self.offsety > self.buildarea[1]:
			self.offsety = self.buildarea[1]

		self.redrawGraph()

	def drawGraph(self, dc):
		dc.SetBackground(wx.Brush("black"))
		dc.Clear()
		
		self.drawGrid(dc)
		self.drawCircles(dc)
		self.drawRects(dc)
		self.drawPoints(dc)
			
	def setGrid(self, gf):
		self.showGrid = gf
		self.redrawGraph()
		
	def setPathOnly(self, pof):
		self.pathOnly = pof
		self.redrawGraph()

	def drawGrid(self, dc):
		if not self.showGrid:
			return
		ytop = (-self.buildarea[1] - self.offsety)*self.zoom*self.scale
		if ytop < -self.buildarea[1]: ytop = -self.buildarea[1]
		ytop += self.buildarea[1]

		ybottom = (self.buildarea[1] - self.offsety)*self.zoom*self.scale
		if ybottom > self.buildarea[1]*self.scale: ybottom = self.buildarea[1]*self.scale
		ybottom += self.buildarea[1]

		for x in range(-self.buildarea[0], self.buildarea[0], 10):
			if x == 0:
				dc.SetPen(wx.Pen("red", 1))
			elif x%50 == 0:
				dc.SetPen(wx.Pen(lt_Gray, 1))
			else:
				dc.SetPen(wx.Pen(dk_Gray, 1))
			x = (x - self.offsetx)*self.zoom*self.scale
			if x >= -self.buildarea[0]*self.scale and x <= self.buildarea[0]*self.scale:
				dc.DrawLine(x+self.shiftX, ytop+self.shiftY, x+self.shiftX, ybottom+self.shiftY)
			
		xleft = (-self.buildarea[0] - self.offsetx)*self.zoom*self.scale
		if xleft <-self.buildarea[0]: xleft = -self.buildarea[0]

		xright = (self.buildarea[0] - self.offsetx)*self.zoom*self.scale
		if xright > self.buildarea[0]*self.scale: xright = self.buildarea[0]*self.scale

		for y in range(-self.buildarea[1], self.buildarea[1], 10):
			if y == 0:
				dc.SetPen(wx.Pen("red", 1))
			elif y%50 == 0:
				dc.SetPen(wx.Pen(lt_Gray, 1))
			else:
				dc.SetPen(wx.Pen(dk_Gray, 1))
			y = (y - self.offsety)*self.zoom*self.scale
			if y >= -self.buildarea[1]*self.scale and y <= self.buildarea[1]*self.scale:
				y += self.buildarea[1]
				dc.DrawLine(xleft+self.shiftX, y+self.shiftY, xright+self.shiftX, y+self.shiftY)

	def redrawGraph(self):
		dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)

		self.drawGraph(dc)

		del dc
		self.Refresh()
		self.Update()
			
	def drawPoints(self, dc):
		if self.data is None:
			return
		
		if len(self.data) <= 1:
			return
		
		for i in range(1, len(self.data)):
			self.drawLine(dc, self.data[i-1], self.data[i], i == self.hiLite)

	def drawCircles(self, dc):
		for ctr, r in self.circles:
			p = [ctr[0], ctr[1]-(r-self.toolRad)]
			self.drawArc(dc, p, p, ctr)
	
	def drawRects(self, dc):
		for ctr, w, h in self.rects:
			xa = ctr[0] - (w/2.0-self.toolRad)
			ya = ctr[1] - (h/2.0-self.toolRad)
			xb = ctr[0] + (w/2.0-self.toolRad)
			yb = ctr[1] + (h/2.0-self.toolRad)
			self.drawLine(dc, [xa, ya], [xa, yb])
			self.drawLine(dc, [xa, yb], [xb, yb])
			self.drawLine(dc, [xb, yb], [xb, ya])
			self.drawLine(dc, [xb, ya], [xa, ya])

	def drawLine(self, dc, start, end, hlFlag=False):
		if hlFlag:
			c = "red"
		else:
			c = "green"
			
		if self.pathOnly:
			w = 1;
		else:
			w = self.toolRad * 2 * self.scale * self.zoom
			
		(x1, y1) = self.transform(start[0], start[1])
		(x2, y2) = self.transform(end[0], end[1])

		dc.SetPen(wx.Pen(c, w))
		dc.DrawLine(x1, y1, x2, y2)
		
	def getHiLitedSegment(self):
		if self.hiLite == 0:
			return ""

		i = self.hiLite		
		return "(%f,%f) => (%f,%f)" % (self.data[i-1][0], self.data[i-1][1], self.data[i][0], self.data[i][1])

	def drawArc(self, dc, start, end, center):				
		c = "green"
		if self.pathOnly:
			w = 1
		else:	
			w = self.toolRad * 2  * self.scale * self.zoom
		
		(x1, y1) = self.transform(start[0], start[1])
		(x2, y2) = self.transform(end[0], end[1])
		(xc, yc) = self.transform(center[0], center[1])

		dc.SetPen(wx.Pen(c, w))
		dc.SetBrush(wx.TRANSPARENT_BRUSH)

		dc.DrawArc(x1, y1, x2, y2, xc, yc)
				
	def transform(self, ptx, pty):
		x = (ptx - self.offsetx)*self.zoom*self.scale
		y = (pty + self.offsety)*self.zoom*self.scale
		return (x+self.shiftX, self.buildarea[1]-(y+self.shiftY))
