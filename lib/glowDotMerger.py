import math as maths
import time

ERROR_MARGIN = 0.125 # arbitrary value, one block is 30 units
GLOW_CORNER_ID = 504
GLOW_DOT_ID = 1886
NS_PER_LOG = 5 * 1000*1000*1000 # 5 seconds

def checkCompatibility(obj1, obj2):
    return 1 if (
        (maths.dist(obj1.getImpliedPos(), obj2.getImpliedPos()) <= ERROR_MARGIN)
        and (obj1.getColour(default = 3) == obj2.getColour(default = 3))
        and (obj2.getAdjustedAngle() in obj1.getCompatibleAngles())
        ) else 0

def merge(objects, logging = False):
    output = []
    glowCorners = []
    for obj in objects:
        list = glowCorners if obj.getObjID() == GLOW_CORNER_ID else output
        list.append(obj)
    if logging:
        count = len(glowCorners)
        getTime = time.time_ns()
        print(f"0 out of {count} glow corners processed")
    
    while glowCorners:
        if logging:
            if (time.time_ns() - getTime >= NS_PER_LOG):
                print(f"{(count - len(glowCorners))} out of {count} glow corners processed")
                getTime += NS_PER_LOG
        
        obj = glowCorners.pop()
        # find glow corners that are potentially part of the same glow dot as the selected object
        candidates = [x for x in glowCorners if checkCompatibility(obj, x)]
        if len(candidates) < 3:
            output.append(obj)
            continue
        # for each angle, find the closest corner to the implied centre
        closestCorners = []
        for angle in obj.getCompatibleAngles():
            variableName = [x for x in candidates if x.getAdjustedAngle() == angle]
            if variableName:
                variableName.sort(key = lambda x: maths.dist(obj.getImpliedPos(), x.getImpliedPos()))
                closestCorners.append(variableName.pop(0))
        if len(closestCorners) < 3:
            output.append(obj)
            continue
        # prevent selected corners from being processed again
        for corner in closestCorners:
            glowCorners.pop(glowCorners.index(corner))
        # turn first object into our glow dot and put into the output
        closestCorners.append(obj)
        averagePos = [sum(y) / len(y) for y in zip(*[x.getPos() for x in closestCorners])]
        obj.setPos(averagePos).setAngle(0).setObjID(GLOW_DOT_ID) # return self is one hell of a drug you should try it
        
        output.append(obj)
    if logging:
        print(f"{count} out of {count} glow corners processed")
    return output