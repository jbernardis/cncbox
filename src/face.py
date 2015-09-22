from math import fabs

FWIDTH = 0
FHEIGHT = 1

TABS = 0
SLOTS = 0

class face:
    def __init__(self, h, w, thk):
        self.height = h
        self.width = w
        self.thickness = thk
        self.htabtype = TABS
        self.wtabtype = TABS
        self.htabct = 0
        self.wtabct = 0
        self.htablen = 10
        self.wtablen = 10
        self.htabs = []
        self.wtabs = []
        self.hrelief = False
        self.wrelief = False
        self.rects = []
        self.circles = []
        
    def getDim(self):
        return self.width, self.height
        
    def setRectangles(self, r):
        self.rects = r[:]
        
    def setCircles(self, c):
        self.circles = c[:]
        
    def setWall(self, w):
        self.thickness = w 
        
    def setHeight(self, h):
        self.height = h
        self.calcHTabs()
        
    def calcHTabs(self):
        if self.htabct > 0:
            self.htabs = []
            step = self.height/float(self.htabct+1.0)
            loc = 0;
            for i in range(self.htabct):
                loc += step
                self.htabs.append((loc, self.htablen))
               
    def setWidth(self, w):
        self.width = w 
        self.calcWTabs()
        
    def calcWTabs(self):
        if self.wtabct > 0:
            self.wtabs = []
            step = self.width/float(self.wtabct+1.0)
            loc = 0;
            for i in range(self.wtabct):
                loc += step
                self.wtabs.append((loc, self.wtablen))
            
    def setHRelief(self):
        self.hrelief = True
        self.wrelief = False

    def setWRelief(self):
        self.hrelief = False
        self.wrelief = True

    def setNoRelief(self):
        self.hrelief = False
        self.wrelief = False
        
    def setTabType(self, horw, t):
        if horw == FWIDTH:
            self.wtabtype = t 
        else:
            self.htabtype = t 
            
    def setTabLen(self, horw, l):
        if horw == FWIDTH:
            self.wtablen = l 
            self.calcWTabs()
        else:
            self.htablen = l 
            self.calcHTabs()
        
    def setTabCount(self, horw, n):
        if horw == FWIDTH:
            self.wtabct = n 
            self.calcWTabs()
        else:
            self.htabct = n 
            self.calcHTabs()
        
    def render(self, toolrad):
        sides = []
        sides.append(self.renderHSide([-self.width/2.0, -self.height/2.0], [-self.width/2.0, self.height/2.0], -1, toolrad))
        sides.append(self.renderWSide([-self.width/2.0, self.height/2.0], [self.width/2.0, self.height/2.0], 1, toolrad))
        sides.append(self.renderHSide([self.width/2.0, self.height/2.0], [self.width/2.0, -self.height/2.0], 1, toolrad))
        sides.append(self.renderWSide([self.width/2.0, -self.height/2.0], [-self.width/2.0, -self.height/2.0], -1, toolrad))
        
        sxMod = len(sides)
        for sx in range(sxMod):
            sx2 = (sx+1) % sxMod

            x1 = sides[sx][-1][0]
            x2 = sides[sx2][0][0]
            
            if fabs(x1) < fabs(x2):
                sides[sx][-1][0] = x1
                sides[sx2][0][0] = x1
            else:
                sides[sx][-1][0] = x2
                sides[sx2][0][0] = x2
                
            y1 = sides[sx][-1][1]
            y2 = sides[sx2][0][1]
            
            if fabs(y1) < fabs(y2):
                sides[sx][-1][1] = y1
                sides[sx2][0][1] = y1
            else:
                sides[sx][-1][1] = y2
                sides[sx2][0][1] = y2
                
        points = [sides[0][0]]
        for s in sides:
            points.extend(s[1:])
            
        c = self.renderCircles()
        r = self.renderRects()
        return points, c, r
    
    def renderCircles(self):
        return [[x[0], x[1]] for x in self.circles]
     
    def renderRects(self):
        return [[x[0], x[1], x[2]] for x in self.rects]
    
    def renderHSide(self, start, end, outDir, toolrad):
        points = []
        td = outDir*toolrad
        if self.htabct == 0:
            points.append([start[0]+td, start[1]+td])
            points.append([end[0]+td, end[1]-td])
        else:
            if self.htabtype == TABS:
                x = start[0]-outDir*self.thickness+td
                xp = start[0]+td
                points.append([x, start[1]+td])
                for t in self.htabs:
                    points.append([x, start[1]-outDir*(t[0]-t[1]/2.0)+td])
                    if self.wrelief:
                        points.append([x, start[1]-outDir*(t[0]-t[1]/2.0)])
                        points.append([x, start[1]-outDir*(t[0]-t[1]/2.0)+td])
                    elif self.hrelief:
                        points.append([x-td, start[1]-outDir*(t[0]-t[1]/2.0)+td])
                        points.append([x, start[1]-outDir*(t[0]-t[1]/2.0)+td])
                    points.append([xp, start[1]-outDir*(t[0]-t[1]/2.0)+td])
                    points.append([xp, start[1]-outDir*(t[0]+t[1]/2.0)-td])
                    points.append([x, start[1]-outDir*(t[0]+t[1]/2.0)-td])
                    if self.wrelief:
                        points.append([x, start[1]-outDir*(t[0]+t[1]/2.0)])
                        points.append([x, start[1]-outDir*(t[0]+t[1]/2.0)-td])
                    elif self.hrelief:
                        points.append([x-td, start[1]-outDir*(t[0]+t[1]/2.0)-td])
                        points.append([x, start[1]-outDir*(t[0]+t[1]/2.0)-td])
                points.append([x, end[1]-td])
            else:
                x = start[0]+td
                xp = start[0]+td-outDir*self.thickness
                points.append([x, start[1]+td])
                for t in self.htabs:
                    points.append([x, start[1]-outDir*(t[0]-t[1]/2.0)-td])
                    points.append([xp, start[1]-outDir*(t[0]-t[1]/2.0)-td])
                    if self.wrelief:
                        points.append([xp, start[1]-outDir*(t[0]-t[1]/2.0)])
                        points.append([xp, start[1]-outDir*(t[0]-t[1]/2.0)-td])
                    elif self.hrelief:
                        points.append([xp-td, start[1]-outDir*(t[0]-t[1]/2.0)-td])
                        points.append([xp, start[1]-outDir*(t[0]-t[1]/2.0)-td])
                    points.append([xp, start[1]-outDir*(t[0]+t[1]/2.0)+td])
                    if self.wrelief:
                        points.append([xp, start[1]-outDir*(t[0]+t[1]/2.0)])
                        points.append([xp, start[1]-outDir*(t[0]+t[1]/2.0)+td])
                    elif self.hrelief:
                        points.append([xp-td, start[1]-outDir*(t[0]+t[1]/2.0)+td])
                        points.append([xp, start[1]-outDir*(t[0]+t[1]/2.0)+td])
                    points.append([x, start[1]-outDir*(t[0]+t[1]/2.0)+td])
                points.append([x, end[1]-td])
            
        return points
        
    def renderWSide(self, start, end, outDir, toolrad):
        points = []
        td = outDir*toolrad
        if self.wtabct == 0:
            points.append([start[0]-td, start[1]+td])
            points.append([end[0]+td, end[1]+td])
        else:
            if self.wtabtype == TABS:
                y = start[1]-outDir*self.thickness+td
                yp = start[1]+td
                points.append([start[0]-td, y])
                for t in self.wtabs:
                    points.append([start[0]+outDir*(t[0]-t[1]/2.0)-td, y])
                    if self.hrelief:
                        points.append([start[0]+outDir*(t[0]-t[1]/2.0)-td, y-td])
                        points.append([start[0]+outDir*(t[0]-t[1]/2.0)-td, y])
                    elif self.wrelief:
                        points.append([start[0]+outDir*(t[0]-t[1]/2.0), y])
                        points.append([start[0]+outDir*(t[0]-t[1]/2.0)-td, y])
                    points.append([start[0]+outDir*(t[0]-t[1]/2.0)-td, yp])
                    points.append([start[0]+outDir*(t[0]+t[1]/2.0)+td, yp])
                    points.append([start[0]+outDir*(t[0]+t[1]/2.0)+td, y])
                    if self.hrelief:
                        points.append([start[0]+outDir*(t[0]+t[1]/2.0)+td, y-td])
                        points.append([start[0]+outDir*(t[0]+t[1]/2.0)+td, y])
                    elif self.wrelief:
                        points.append([start[0]+outDir*(t[0]+t[1]/2.0), y])
                        points.append([start[0]+outDir*(t[0]+t[1]/2.0)+td, y])
    
                points.append([end[0]+td, y])
            else:
                y = start[1]+td
                yp = start[1]+td-outDir*self.thickness
                points.append([start[0]-td, y])
                for t in self.wtabs:
                    points.append([start[0]+outDir*(t[0]-t[1]/2.0)+td, y])
                    points.append([start[0]+outDir*(t[0]-t[1]/2.0)+td, yp])
                    if self.hrelief:
                        points.append([start[0]+outDir*(t[0]-t[1]/2.0)+td, yp-td])
                        points.append([start[0]+outDir*(t[0]-t[1]/2.0)+td, yp])
                    elif self.wrelief:
                        points.append([start[0]+outDir*(t[0]-t[1]/2.0), yp])
                        points.append([start[0]+outDir*(t[0]-t[1]/2.0)+td, yp])
                    points.append([start[0]+outDir*(t[0]+t[1]/2.0)-td, yp])
                    if self.hrelief:
                        points.append([start[0]+outDir*(t[0]+t[1]/2.0)-td, yp-td])
                        points.append([start[0]+outDir*(t[0]+t[1]/2.0)-td, yp])
                    elif self.wrelief:
                        points.append([start[0]+outDir*(t[0]+t[1]/2.0), yp])
                        points.append([start[0]+outDir*(t[0]+t[1]/2.0)-td, yp])
                    points.append([start[0]+outDir*(t[0]+t[1]/2.0)-td, y])
    
                points.append([end[0]+td, y])
            
        return points
