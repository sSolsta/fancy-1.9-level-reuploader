import math as maths
import time

ERROR_MARGIN = 0.125 # arbitrary value, one block is 30 units
GLOW_CORNER_ID = "504"
GLOW_DOT_ID = 1886
NS_PER_LOG = 4 * 1000*1000*1000 # 4 seconds
MIN_NS_PER_LOG = 100*1000*1000 # 0.1 seconds


def theFuckening(objects, log = True):
    output = []
    buckets = {}
    if log:
        print()
        print("Sorting glow corners...")
    for obj in objects:
        if obj[1] == GLOW_CORNER_ID:
            obj.initGlowCornerValues()
            buckets.setdefault(obj.mergeGroup, []).append(obj)
        else:
            output.append(obj)
    if log:
        count = sum(len(x) for x in buckets.values())
        print(f"{count} glow corners sorted, beginning merging")
        processed = 0
        startTime = logTime = time.time_ns()
    
    for bucket in buckets:
        angleGroups = [[], [], [], []]
        for obj in buckets[bucket]:
            angleGroups[obj.subgroup].append(obj)
        while min(len(x) for x in angleGroups):
            if log and ((time.time_ns() - logTime) >= NS_PER_LOG):
                print(f"{processed} of {count} glow corners processed")
                logTime += NS_PER_LOG
            obj = angleGroups[0].pop()
            fail = False
            for group in angleGroups[1:]:
                group.sort(key = lambda x: maths.dist(obj.centre, x.centre))
                if maths.dist(obj.centre, group[0].centre) > ERROR_MARGIN:
                    fail = True
                    break
            if fail:
                output.append(obj)
                processed += 1
                continue
            obj[2], obj[3] = [sum(y) / len(y) for y in zip(*([obj.centre] + [x.pop(0).centre for x in angleGroups[1:]]))]
            obj[1] = GLOW_DOT_ID
            output.append(obj)
            processed += 4
        for group in angleGroups:
            output.extend(group)
            processed += len(group)
        if log and (((time.time_ns() - logTime) >= MIN_NS_PER_LOG) or (count == processed)):
            print(f"{processed} of {count} glow corners processed")
            logTime = time.time_ns()
    if log:
        finalTime = (time.time_ns() - startTime) / (1000*1000*1000)
        print(f"Completed in {finalTime} seconds")
                
    return output