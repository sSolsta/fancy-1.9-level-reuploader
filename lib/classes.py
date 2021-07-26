import math as maths

TENSQRTTWO = 10 * maths.sqrt(2)

def roundToSignificantDigits(input, digits):
    return input if input == 0 else round(input, -int(maths.floor(maths.log10(abs(input)))) + (digits - 1))

class LevelObject(object):
    '''
    not a complete implementation of a proper level object class, just enough
    functionality is implemented to let me do glow dot merging and layer fixing in 1.9 levels.
    '''
    def __init__(self):
        self.data = {}
        self.cache = {
            "adjAngle": None,
            "impliedPos": None,
            "compatAngles": None
            }
    
    def fromString(self, str):
        data = str.split(",")
        data = {int(k):v for k,v in zip(data[0::2], data[1::2])}
        self.data = data
        return self
    
    def toString(self):
        return ",".join([",".join((str(x), str(self.data[x]))) for x in self.data])
        
    def setValues(self, values):
        self.data.update({int(k):values[k] for k in values})
        return self
    
    def getObjID(self):
        return int(self.data[1])
        
    def setObjID(self, value):
        self.setValues({1: value})
        return self
    
    def getXPos(self):
        return float(self.data[2])
        
    def setXPos(self, value, round = True):
        # gd rounds obj coords to 6 significant digits for some reason and i haven't tested what happens if you don't
        if round: 
            value = roundToSignificantDigits(value, 6)
        self.setValues({2: value})
        return self
    
    def getYPos(self):
        return float(self.data[3])
        
    def setYPos(self, value, round = True):
        if round:
            value = roundToSignificantDigits(value, 6)
        self.setValues({3: value})
        return self
    
    def getPos(self):
        return (self.getXPos(), self.getYPos())
        
    def setPos(self, pos, round = True):
        self.setXPos(pos[0], round)
        self.setYPos(pos[1], round)
        return self
    
    def getAngle(self):
        return int(self.data.get(6, 0))
        
    def setAngle(self, value):
        self.setValues({6: value})
        return self
        
    # can't be bothered figuring out every object's default colour as i don't need to for what i'm doing
    def getColour(self, default = None):
        return int(self.data.get(19, default))
        
    # used in layer fixing
    def setLayer(self, value):
        self.setValues({24: value})
        return self
    
    # accounts for vertical and horizontal mirroring, used for glow dot merging
    def getAdjustedAngle(self):
        if self.cache["adjAngle"] == None:
            offset = (int(self.data.get(4, 0)) * 3) ^ int(self.data.get(5, 0))
            self.cache["adjAngle"] = (self.getAngle() - (offset * 90)) % 360
        return self.cache["adjAngle"]
        
    # also used for glow dot merging
    def getCompatibleAngles(self):
        if self.cache["compatAngles"] == None:
            self.cache["compatAngles"] = [(self.getAdjustedAngle() + x) % 360 for x in (90, 180, 270)]
        return self.cache["compatAngles"]
    
    # gets implied centre of glow dot
    def getImpliedXPos(self):
        angle = maths.radians(self.getAdjustedAngle() + 135)
        return self.getXPos() + (maths.sin(angle) * TENSQRTTWO)
    
    # same as above
    def getImpliedYPos(self):
        angle = maths.radians(self.getAdjustedAngle() + 135)
        return self.getYPos() + (maths.cos(angle) * TENSQRTTWO)
    
    # me too
    def getImpliedPos(self):
        if self.cache["impliedPos"] == None:
            self.cache["impliedPos"] = (self.getImpliedXPos(), self.getImpliedYPos())
        return self.cache["impliedPos"]
        