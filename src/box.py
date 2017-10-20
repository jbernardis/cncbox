import face

import ConfigParser

CORNER_FRONT_SIDE = 0
CORNER_FRONT_TOP = 1
CORNER_SIDE_TOP = 2

cornerTypes = [CORNER_FRONT_SIDE, CORNER_FRONT_TOP, CORNER_SIDE_TOP]

FACE_TOP = 0
FACE_BOTTOM = 1
FACE_LEFT = 2
FACE_RIGHT = 3
FACE_FRONT = 4
FACE_BACK = 5

faceTypes = [FACE_TOP, FACE_BOTTOM, FACE_LEFT, FACE_RIGHT, FACE_FRONT, FACE_BACK]

TABS = 0
SLOTS = 1

NRELIEF = 0
HRELIEF = 1
WRELIEF = 2

class box:
	def __init__(self, h, w, d, thk):
		self.Width = w
		self.Height = h
		self.Depth = d
		self.Wall = thk
		
		self.TabCt = [0, 0, 0]
		self.TabLen = [10, 10, 10]
		self.TabType = [TABS, TABS, TABS]
		self.Relief = NRELIEF
		
		self.BlindTabs = [False, False, False, False, False, False]
		
		self.currentFace = None
		self.initFaces()
		
	def initFaces(self):
		self.faces = [None, None, None, None, None, None]
		self.faces[FACE_TOP]	= face.face(self.Depth, self.Width, self.Wall)
		self.faces[FACE_TOP].setTabType(face.FHEIGHT, SLOTS)
		self.faces[FACE_TOP].setTabType(face.FWIDTH, SLOTS)
		
		self.faces[FACE_BOTTOM] = face.face(self.Depth, self.Width, self.Wall)
		self.faces[FACE_BOTTOM].setTabType(face.FHEIGHT, SLOTS)
		self.faces[FACE_BOTTOM].setTabType(face.FWIDTH, SLOTS)
		
		self.faces[FACE_LEFT]   = face.face(self.Height, self.Depth, self.Wall)
		self.faces[FACE_LEFT].setTabType(face.FHEIGHT, SLOTS)
		self.faces[FACE_LEFT].setTabType(face.FWIDTH, TABS)
		
		self.faces[FACE_RIGHT]  = face.face(self.Height, self.Depth, self.Wall)
		self.faces[FACE_RIGHT].setTabType(face.FHEIGHT, SLOTS)
		self.faces[FACE_RIGHT].setTabType(face.FWIDTH, TABS)
		
		self.faces[FACE_FRONT]  = face.face(self.Height, self.Width, self.Wall)
		self.faces[FACE_FRONT].setTabType(face.FWIDTH, TABS)
		self.faces[FACE_FRONT].setTabType(face.FWIDTH, TABS)

		self.faces[FACE_BACK]   = face.face(self.Height, self.Width, self.Wall)
		self.faces[FACE_BACK].setTabType(face.FWIDTH, TABS)
		self.faces[FACE_BACK].setTabType(face.FWIDTH, TABS)

		for fc in self.faces:
			fc.setNoRelief()
			
	def saveBox(self, fn):
		config = ConfigParser.SafeConfigParser()

		section = 'box'
		config.add_section(section)
		config.set(section, 'width', str(self.Width))
		config.set(section, 'height', str(self.Height))
		config.set(section, 'depth', str(self.Depth))
		config.set(section, 'wall', str(self.Wall))
		config.set(section, 'tabcount', str(self.TabCt))
		config.set(section, 'tablength', str(self.TabLen))
		config.set(section, 'tabtype', str(self.TabType))
		config.set(section, 'relief', str(self.Relief))
		
		section = "blindtabs"
		config.add_section(section)
		for f in faceTypes:
			config.set(section, "face_%d" % f, str(self.BlindTabs[f]))

		for f in faceTypes:
			c = self.faces[f].renderCircles()
			if len(c) != 0:
				section = "face_%d_circles" % f
				config.add_section(section)
				config.set(section, "cx", str([x[0][0] for x in c]))
				config.set(section, "cy", str([y[0][1] for y in c]))
				config.set(section, "radii", str([r[1] for r in c]))
			r = self.faces[f].renderRects()
			if len(r) != 0:
				section = "face_%d_rectangles" % f
				config.add_section(section)
				config.set(section, "cx", str([x[0][0] for x in r]))
				config.set(section, "cy", str([y[0][1] for y in r]))
				config.set(section, "width", str([w[1] for w in r]))
				config.set(section, "height", str([h[2] for h in r]))
		
		with open(fn, 'wb') as configfile:
			config.write(configfile)
			
	def loadBox(self, fn, toolrad):
		s = ""
		config = ConfigParser.SafeConfigParser()
		config.read(fn)

		section = 'box'	  
		if config.has_section(section):
			for n, v in config.items(section):
				if n == 'width':
					try:
						w = float(v)
					except:
						print "invalid value in box file for width"
						w = 100
					self.setWidth(w)
				elif n == 'height':
					try:
						h = float(v)
					except:
						print "invalid value in box file for height"
						h = 100
					self.setHeight(h)
				elif n == 'depth':
					try:
						d = float(v)
					except:
						print "invalid value in box file for depth"
						d = 100
					self.setDepth(d)
				elif n == 'wall':
					try:
						w = float(v)
					except:
						print "invalid value in box file for wall"
						w = 6
					self.setWall(w, toolrad)

				elif n == 'tabcount':
					try:
						exec("s=%s" % v)
					except:
						print "invalid value in box file for tabcount"
						s = [0, 0, 0]
					for c in cornerTypes:
						self.setTabCount(c, s[c])
				elif n == 'tablength':
					try:
						exec("s=%s" % v)
					except:
						print "invalid value in box file for tablength"
						s = [10, 10, 10]
					for c in cornerTypes:
						self.setTabLen(c, s[c])
				elif n == 'tabtype':
					try:
						exec("s=%s" % v)
					except:
						print "invalid value in box file for tabtype"
						s = [0, 0, 0]
					for c in cornerTypes:
						self.setTabType(c, s[c])
				elif n == 'relief':
					try:
						r = int(v)
					except:
						print "invalid value in box file for relief"
						r = NRELIEF
					self.setRelief(r)
				else:
					print "Unknown parameter: %s" % n
		
		section = "blindtabs"
		if config.has_section(section):
			for f in faceTypes:
				try:
					flg = config.get(section, "face_%d" % f)
					if flg.startswith("T") or flg.startswith("t"):
						flg = True
					else:
						flg = False
				except:
					flg = False
				self.BlindTabs[f] = flg
					
		for f in faceTypes:
			section = "face_%d_circles" % f
			if config.has_section(section):
				cx = ""
				cy = ""
				rad = ""
				try:
					cxs = config.get(section, "cx")
					exec("cx=%s" % cxs)
					cys = config.get(section, "cy")
					exec("cy=%s" % cys)
					rads = config.get(section, "radii")
					exec("rad=%s" % rads)
				except:
					print "Unable to process section %s" % section
					continue
				
				lx = len(cx);
				ly = len(cy)
				lr = len(rad)
				if lx != ly or ly != lr or lr != lx:
					print "Invalid data for section %s" % section
					continue
				
				c = []
				for i in range(lx):
					c.append([[cx[i], cy[i]], rad[i]])
					
				self.setCircles(f, c)
				
			section = "face_%d_rectangles" % f
			if config.has_section(section):
				cx = ""
				cy = ""
				lx = ""
				ly = ""
				try:
					cxs = config.get(section, "cx")
					exec("cx=%s" % cxs)
					cys = config.get(section, "cy")
					exec("cy=%s" % cys)
					lxs = config.get(section, "width")
					exec("lx=%s" % lxs)
					lys = config.get(section, "height")
					exec("ly=%s" % lys)
				except:
					print "Unable to process section %s" % section
					continue
				
				lencx = len(cx);
				lency = len(cy)
				lenlx = len(lx)
				lenly = len(ly)
				if lencx != lency or lency != lenlx or lenlx != lenly:
					print "Invalid data for section %s" % section
					continue
				
				r = []
				for i in range(lencx):
					r.append([[cx[i], cy[i]], lx[i], ly[i]])
					
				self.setRectangles(f, r)

			
	def setHeight(self, nh):
		self.Height = nh
		self.faces[FACE_LEFT].setHeight(nh)
		self.faces[FACE_RIGHT].setHeight(nh)
		self.faces[FACE_FRONT].setHeight(nh)
		self.faces[FACE_BACK].setHeight(nh)
		
	def setWidth(self, nw):
		self.Width = nw
		self.faces[FACE_TOP].setWidth(nw)
		self.faces[FACE_BOTTOM].setWidth(nw)
		self.faces[FACE_FRONT].setWidth(nw)
		self.faces[FACE_BACK].setWidth(nw)
		
	def setDepth(self, nd):
		self.Depth = nd
		self.faces[FACE_TOP].setHeight(nd)
		self.faces[FACE_BOTTOM].setHeight(nd)
		self.faces[FACE_LEFT].setWidth(nd)
		self.faces[FACE_RIGHT].setWidth(nd)
		
	def setWall(self, nw, toolrad):
		self.Wall = nw
		for fc in self.faces:
			fc.setWall(nw)
			
		self.render(self.currentFace, toolrad)
		
	def setBlindTabs(self, bt):
		self.BlindTabs = bt
		
	def getFaceDim(self, ft):
		return self.faces[ft].getDim()

	def setRelief(self, rt):
		self.Relief = rt
		if rt == NRELIEF:
			for fc in self.faces:
				fc.setNoRelief()
		elif rt == HRELIEF:
			for fc in self.faces:
				fc.setHRelief()
		elif rt == WRELIEF:
			for fc in self.faces:
				fc.setWRelief()
			
	def setTabCount(self, cornerType, n):
		self.TabCt[cornerType] = n
		if cornerType == CORNER_FRONT_SIDE:
			self.faces[FACE_FRONT].setTabCount(face.FHEIGHT, n)
			self.faces[FACE_BACK].setTabCount(face.FHEIGHT, n)
			self.faces[FACE_LEFT].setTabCount(face.FHEIGHT, n)
			self.faces[FACE_RIGHT].setTabCount(face.FHEIGHT, n)
		elif cornerType == CORNER_FRONT_TOP:
			self.faces[FACE_FRONT].setTabCount(face.FWIDTH, n)
			self.faces[FACE_BACK].setTabCount(face.FWIDTH, n)
			self.faces[FACE_TOP].setTabCount(face.FWIDTH, n)
			self.faces[FACE_BOTTOM].setTabCount(face.FWIDTH, n)
		elif cornerType == CORNER_SIDE_TOP:
			self.faces[FACE_LEFT].setTabCount(face.FWIDTH, n)
			self.faces[FACE_RIGHT].setTabCount(face.FWIDTH, n)
			self.faces[FACE_TOP].setTabCount(face.FHEIGHT, n)
			self.faces[FACE_BOTTOM].setTabCount(face.FHEIGHT, n)
		
	def setTabLen(self, cornerType, l):
		self.TabLen[cornerType] = l
		if cornerType == CORNER_FRONT_SIDE:
			self.faces[FACE_FRONT].setTabLen(face.FHEIGHT, l)
			self.faces[FACE_BACK].setTabLen(face.FHEIGHT, l)
			self.faces[FACE_LEFT].setTabLen(face.FHEIGHT, l)
			self.faces[FACE_RIGHT].setTabLen(face.FHEIGHT, l)
		elif cornerType == CORNER_FRONT_TOP:
			self.faces[FACE_FRONT].setTabLen(face.FWIDTH, l)
			self.faces[FACE_BACK].setTabLen(face.FWIDTH, l)
			self.faces[FACE_TOP].setTabLen(face.FWIDTH, l)
			self.faces[FACE_BOTTOM].setTabLen(face.FWIDTH, l)
		elif cornerType == CORNER_SIDE_TOP:
			self.faces[FACE_LEFT].setTabLen(face.FWIDTH, l)
			self.faces[FACE_RIGHT].setTabLen(face.FWIDTH, l)
			self.faces[FACE_TOP].setTabLen(face.FHEIGHT, l)
			self.faces[FACE_BOTTOM].setTabLen(face.FHEIGHT, l)
		
	def setTabType(self, cornerType, tt):
		self.TabType[cornerType] = tt;
		tt2 = TABS
		if tt == TABS:
			tt2 = SLOTS
			
		if cornerType == CORNER_FRONT_SIDE:
			self.faces[FACE_FRONT].setTabType(face.FHEIGHT, tt)
			self.faces[FACE_BACK].setTabType(face.FHEIGHT, tt)
			self.faces[FACE_LEFT].setTabType(face.FHEIGHT, tt2)
			self.faces[FACE_RIGHT].setTabType(face.FHEIGHT, tt2)
		elif cornerType == CORNER_FRONT_TOP:
			self.faces[FACE_FRONT].setTabType(face.FWIDTH, tt)
			self.faces[FACE_BACK].setTabType(face.FWIDTH, tt)
			self.faces[FACE_TOP].setTabType(face.FWIDTH, tt2)
			self.faces[FACE_BOTTOM].setTabType(face.FWIDTH, tt2)
		elif cornerType == CORNER_SIDE_TOP:
			self.faces[FACE_LEFT].setTabType(face.FWIDTH, tt)
			self.faces[FACE_RIGHT].setTabType(face.FWIDTH, tt)
			self.faces[FACE_TOP].setTabType(face.FHEIGHT, tt2)
			self.faces[FACE_BOTTOM].setTabType(face.FHEIGHT, tt2)
			
	def setCircles(self, facetype, c):
		self.faces[facetype].setCircles(c)
		
	def setRectangles(self, facetype, r):
		self.faces[facetype].setRectangles(r)

	def render(self, faceType, toolrad, blindDepth = False):
		if faceType is None:
			return 
		
		if faceType == FACE_TOP:
			adj = [self.BlindTabs[FACE_LEFT], self.BlindTabs[FACE_BACK], self.BlindTabs[FACE_RIGHT], self.BlindTabs[FACE_FRONT]]
		elif faceType == FACE_BOTTOM:
			adj = [self.BlindTabs[FACE_RIGHT], self.BlindTabs[FACE_BACK], self.BlindTabs[FACE_LEFT], self.BlindTabs[FACE_FRONT]]
		elif faceType == FACE_LEFT:
			adj = [self.BlindTabs[FACE_BOTTOM], self.BlindTabs[FACE_BACK], self.BlindTabs[FACE_TOP], self.BlindTabs[FACE_FRONT]]
		elif faceType == FACE_LEFT:
			adj = [self.BlindTabs[FACE_TOP], self.BlindTabs[FACE_BACK], self.BlindTabs[FACE_BOTTOM], self.BlindTabs[FACE_FRONT]]
		elif faceType == FACE_FRONT:
			adj = [self.BlindTabs[FACE_LEFT], self.BlindTabs[FACE_TOP], self.BlindTabs[FACE_RIGHT], self.BlindTabs[FACE_BOTTOM]]
		elif faceType == FACE_BACK:
			adj = [self.BlindTabs[FACE_RIGHT], self.BlindTabs[FACE_TOP], self.BlindTabs[FACE_LEFT], self.BlindTabs[FACE_BOTTOM]]
		else:
			return
			
		self.currentFace = faceType 
		
		print "rendering face %d blind = %s" % (faceType, blindDepth)
		
		return self.faces[faceType].render(toolrad, blindDepth, self.BlindTabs[faceType], adj)
		