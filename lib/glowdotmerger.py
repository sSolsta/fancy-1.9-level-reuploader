"""lib.glowdotmerger

glow dot merging function

how it works:
- glow corners are sorted into "buckets" depending on their angle
    (modulo 90) and colour (other objects are put into the output list)
- for each bucket glow corners are further subdivided into 4 angle
    groups (the 4 corners required to make a glow dot)
    - to merge the glow dots in a bucket, first we get one glow corner
        from one of the angle groups (doesn't matter which one)
    - we then sort the other 3 angle groups to find the closest corner in
        each angle group
    - if all 3 corners are within the arbitrarily-defined error margin,
        we remove them from their angle groups, and then convert one
        of the 4 corners into a glow dot, put it into the output list,
        and discard the other 3 corners
    - otherwise, we put the original corner into the output list and
        continue
    - we repeat this until any of the angle groups are empty, and we put
        the rest of the corners into the output list
- we do this for every bucket and then return the output list

could benefit from multiprocessing
"""

import math as maths
import time

ERROR_MARGIN = 0.125  # arbitrary value, one block is 30 units
GLOW_CORNER_ID = "504"
GLOW_DOT_ID = 1886
NS_PER_LOG = 4000_000_000  # 4 seconds
MIN_NS_PER_LOG = 100_000_000  # 0.1 seconds


def the_fuckening(objects, log = True):
    output = []
    buckets = {}
    if log:
        print()
        print("Sorting glow corners...")
    # sorting objects into buckets (or output)
    for obj in objects:
        if obj.id == GLOW_CORNER_ID:
            obj.init_glow_corner_values()
            buckets.setdefault(obj.merge_group, []).append(obj)
        else:
            output.append(obj)
    if log:
        count = sum(len(x) for x in buckets.values())
        print(f"{count} glow corners sorted, beginning merging")
        processed = 0
        start_time = log_time = time.time_ns()
    
    for bucket in buckets:
        # sorting to angle groups
        angle_groups = [[] for _ in range(4)]
        for obj in buckets[bucket]:
            angle_groups[obj.subgroup].append(obj)
        while min(len(x) for x in angle_groups):
            if log and time.time_ns()-log_time >= NS_PER_LOG:
                print(f"{processed} of {count} glow corners processed")
                log_time += NS_PER_LOG
            # get corner and attempt to find compatible corners
            obj = angle_groups[0].pop()
            fail = False
            for group in angle_groups[1:]:
                group.sort(key = lambda x: maths.dist(obj.centre, x.centre))
                if maths.dist(obj.centre, group[0].centre) > ERROR_MARGIN:
                    fail = True
                    break
            if fail:
                output.append(obj)
                processed += 1
                continue
            # taking average centre and using as centre of glow dot
            centres = (obj.centre, *(x.pop(0).centre for x in angle_groups[1:]))
            obj.x, obj.y = (sum(x) / len(x) for x in zip(*centres))
            
            obj.id = GLOW_DOT_ID
            output.append(obj)
            processed += 4
        # put remaining corners into output
        for group in angle_groups:
            output.extend(group)
            processed += len(group)
        if log and (time.time_ns()-log_time >= MIN_NS_PER_LOG or count == processed):
            print(f"{processed} of {count} glow corners processed")
            log_time = time.time_ns()
    if log:
        final_time = (time.time_ns() - start_time) / (1000_000_000)
        print(f"Completed in {final_time} seconds")
                
    return output
