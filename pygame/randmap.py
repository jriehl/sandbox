#! /usr/bin/env python
# ______________________________________________________________________
"""Module randmap
Generate a random map.
$Id: randmap.py,v 1.1 2005/10/10 20:22:03 jriehl Exp $
"""
# ______________________________________________________________________
# Module imports

import random

# ______________________________________________________________________

NORTH = 1
SOUTH = NORTH << 1
WEST = SOUTH << 1
EAST = WEST << 1
ENTRANCE = EAST << 1
ROOM = ENTRANCE << 1
ALL = NORTH | SOUTH | WEST | EAST
MAX = ROOM
directions = [NORTH, SOUTH, WEST, EAST]

reverseDirectionMap = { NORTH : SOUTH,
                        SOUTH : NORTH,
                        WEST : EAST,
                        EAST : WEST }

# ______________________________________________________________________

def addDirections (mymap, coord, dir):
    mymap[coord[1]][coord[0]] |= dir

# ______________________________________________________________________

def fillRect (mymap, x, y, width, height, value):
    print((x, y, width, height))
    for cy in range(y, y + height):
        for cx in range(x, x + width):
            mymap[cy][cx] = value

# ______________________________________________________________________

def orRect (mymap, x, y, width, height, value):
    print((x, y, width, height))
    for cy in range(y, y + height):
        for cx in range(x, x + width):
            mymap[cy][cx] |= value

# ______________________________________________________________________

def addRoom (mymap, box):
    print(box)
    x, y, width, height = box
    orRect(mymap, x + 1, y + 1, width - 1, height - 1,
           NORTH | SOUTH | WEST | EAST | ROOM)
    v0 = SOUTH | WEST | EAST
    v1 = NORTH | WEST | EAST | ROOM
    y1 = y + height - 1
    for i in range(x + 1, x + width - 1):
        mymap[y][i] |= v0
        mymap[y1][i] |= v1
    v0 = EAST | SOUTH | NORTH
    v1 = WEST | SOUTH | NORTH | ROOM
    x1 = x + width - 1
    for j in range(y + 1, y + height - 1):
        mymap[j][x] |= v0
        mymap[j][x1] |= v1
    mymap[y][x] |= SOUTH | EAST
    mymap[y1][x] |= NORTH | EAST
    mymap[y][x1] |= SOUTH | WEST
    mymap[y1][x1] |= NORTH | WEST | ROOM

# ______________________________________________________________________

def calcCoord (x, y, dir):
    assert dir in directions
    if dir == NORTH:
        return (x, y - 1)
    elif dir == SOUTH:
        return (x, y + 1)
    elif dir == WEST:
        return (x - 1, y)
    return (x + 1, y)

# ______________________________________________________________________

def isValidCoord (bbox, coord):
    return ((coord[0] >= bbox[0]) and
            (coord[0] < (bbox[0] + bbox[2])) and
            (coord[1] >= bbox[1]) and
            (coord[1] < (bbox[1] + bbox[3])))

# ______________________________________________________________________

def separateFlags (value):
    result = []
    mask = MAX
    while mask > 0:
        if (value & mask) > 0:
            result.append(mask)
        mask >>= 1
    return result

# ______________________________________________________________________

def getDirectionList (mymap, coord):
    return separateFlags(mymap[coord[1]][coord[0]])

# ______________________________________________________________________

def eliminateDeadEnds (mymap, times = 1):
    for iteration in range(times):
        for y in range(len(mymap)):
            crntRow = mymap[y]
            for x in range(len(crntRow)):
                dList = separateFlags(crntRow[x])
                if len(dList) == 1:
                    # Dead end
                    mymap[y][x] = 0
                    neighbor = calcCoord(x, y, dList[0])
                    mask = ~(reverseDirectionMap[dList[0]])
                    mymap[neighbor[1]][neighbor[0]] &= mask

# ______________________________________________________________________

def generateMaze (width, height):
    bbox = (0,0,width, height)
    mymap = [0] * height
    mymap = list(map(lambda x : [x] * width, mymap))
    visited = []
    sx = random.randrange(0, width)
    sy = random.randrange(0, height)
    mymap[sy][sx] |= ENTRANCE
    visited.append((sx, sy))
    mazeSize = width * height
    while len(visited) < mazeSize:
        crntSpot = random.choice(visited)
        placeToGo = True
        while placeToGo:
            dirs = directions[:]
            while len(dirs) > 0:
                dir = random.choice(dirs)
                dirs.remove(dir)
                target = calcCoord(crntSpot[0], crntSpot[1], dir)
                if (isValidCoord(bbox, target) and
                    (0 == mymap[target[1]][target[0]])):
                    break
            if len(dirs) == 0:
                placeToGo = False
            else:
                addDirections(mymap, crntSpot, dir)
                addDirections(mymap, target, reverseDirectionMap[dir])
                crntSpot = target
                visited.append(crntSpot)
    return mymap

# ______________________________________________________________________

def addRandomRooms (mymap, bbox, dimRange, count = 1):
    for iteration in range(count):
        x0, y0, w, h = bbox
        x = random.randrange(0, w - dimRange[0] + 1)
        y = random.randrange(0, h - dimRange[0] + 1)
        dx = random.randrange(dimRange[0], min(dimRange[1], w - x + 1))
        dy = random.randrange(dimRange[0], min(dimRange[1], h - y + 1))
        addRoom(mymap, (x, y, dx, dy))

# ______________________________________________________________________
# Main

def main ():
    def goinNorth (d):
        c0 = "#"
        if (d & ROOM) > 0:
            c0 = "."
        if (d & NORTH) > 0:
            return c0 + "."
        return c0 + "#"
    def goinWest (d):
        c0 = "."
        if (d & ENTRANCE) > 0:
            c0 = ">"
        elif d == 0:
            c0 = "#"
        if (d & WEST) > 0:
            return "." + c0
        return "#" + c0
    maze = generateMaze(39, 19)
    addRandomRooms(maze, (0, 0, 39, 19), (2, 10), random.randrange(4,15))
    eliminateDeadEnds(maze, 10)
    for row in maze:
        print("%s#" % ''.join(map(goinNorth, row)))
        print("%s#" % ''.join(map(goinWest, row)))
    print("#" * 79)

# ______________________________________________________________________

if __name__ == "__main__":
    main()

# ______________________________________________________________________
# End of randmap.py
