#! /usr/bin/env python
# ______________________________________________________________________
"""Module tileplay

$Id: tileplay.py,v 1.1 2005/10/10 20:22:03 jriehl Exp $
"""
# ______________________________________________________________________
# Module imports

import random, os.path
import tkinter

#import basic pygame modules
import pygame
from pygame.locals import *

import randmap

from randmap import NORTH, SOUTH, EAST, WEST, ENTRANCE, ROOM, ALL, MAX

# ______________________________________________________________________

OBS = MAX << 1

defaultMazeTileMap = {
    0                            : 0,
    NORTH                        : 9,
    SOUTH                        : 8,
    SOUTH | NORTH                : 1,
    WEST                         : 11,
    WEST | NORTH                 : 6,
    WEST | SOUTH                 : 4,
    WEST | SOUTH | NORTH         : 15,
    EAST                         : 10,
    EAST | NORTH                 : 5,
    EAST | SOUTH                 : 3,
    EAST | SOUTH | NORTH         : 14,
    EAST | WEST                  : 2,
    EAST | WEST | NORTH          : 12,
    EAST | WEST | SOUTH          : 13,
    EAST | WEST | SOUTH | NORTH  : 16,
    ENTRANCE                     : 19,
    ROOM                         : 17,
    OBS                          : 7
    }

# ______________________________________________________________________

class TileMap (object):
    # ____________________________________________________________
    def __init__ (self, tileSurf, tileSize, mapSize):
        self.tileSurf = tileSurf
        self.tileSize = tileSize
        self.entrance = 0, 0
        self.makeMap(mapSize)

    # ____________________________________________________________
    def makeMap (self, mapSize, ival = 0):
        dx, dy = mapSize
        result = [ival] * dy
        result = list(map(lambda x: [x] * dx, result))
        self.map = result
        self.mapSize = mapSize
        self.boundRect = Rect(0, 0, dx, dy)

    # ____________________________________________________________
    def getTileRect (self, index):
        dx, dy = self.tileSize
        tilesPerRow = self.tileSurf.get_width() // dx
        tileX = (index % tilesPerRow) * dx
        tileY = (index // tilesPerRow) * dy
        return Rect(tileX, tileY, dx, dy)

    # ____________________________________________________________
    def blitMap (self, surface, sourceRect, destPos, ofs = 0):
        x, y, xDim, yDim = sourceRect
        dx, dy = self.tileSize
        destY = destPos[1]
        myMap = self.map
        for cy in range(y, y + yDim):
            destX = destPos[0]
            for cx in range(x, x + xDim):
                iconIndex = myMap[cy][cx]
                tileRect = self.getTileRect(iconIndex)
                surface.blit(self.tileSurf, (destX, destY), tileRect)
                destX += dx + ofs
            destY += dy + ofs

    # ____________________________________________________________
    def randomMaze (self, mazeTileMap = None):
        if mazeTileMap == None:
            mazeTileMap = defaultMazeTileMap
        width, height = self.mapSize
        mazeBox = (0, 0, (width - 1) // 2, (height - 1) // 2)
        print(mazeBox)
        maze = randmap.generateMaze(mazeBox[2], mazeBox[3])
        randmap.addRandomRooms(maze, mazeBox, (2, 10), random.randrange(4, 15))
        randmap.eliminateDeadEnds(maze, 5)
        randmap.fillRect(self.map, 0, 0, width, height, 0)
        # __________________________________________________
        # Mark obstructed squares
        for y in range(len(maze)):
            mazeRow = maze[y]
            for x in range(len(mazeRow)):
                v = mazeRow[x]
                mx = x << 1
                my = y << 1
                somethingHere = (v > 0)
                # My so called CENTER
                if (v & ENTRANCE) > 0:
                    self.map[my + 1][mx + 1] = ENTRANCE
                    print("ENTRANCE:{}".format((mx + 1, my + 1)))
                    self.entrance = mx + 1, my + 1
                elif somethingHere:
                    self.map[my + 1][mx + 1] = ROOM
                # NORTH WEST
                if (v & ROOM) > 0:
                    self.map[my][mx] = ROOM
                elif somethingHere:
                    self.map[my][mx] = ALL
                # NORTH
                if (v & NORTH) > 0:
                    self.map[my][mx + 1] = ROOM
                elif somethingHere:
                    self.map[my][mx + 1] = ALL
                # WEST
                if (v & WEST) > 0:
                    self.map[my + 1][mx] = ROOM
                elif somethingHere:
                    self.map[my + 1][mx] = ALL
                # SOUTH and EAST - These will be overwritten by the EAST,
                # SOUTH, and SOUTH EAST neighbors in a later iteration if they
                # are not obstructed.
                if somethingHere:
                    self.map[my + 2][mx] = ALL
                    self.map[my + 2][mx + 1] = ALL
                    self.map[my][mx + 2] = ALL
                    self.map[my + 1][mx + 2] = ALL
                    self.map[my + 2][mx + 2] = ALL
        mx = (len(mazeRow) << 1) - 1
        for my in range(len(self.map)):
            if self.map[my][mx] != 0:
                self.map[my][mx + 1] = ALL
        my = (len(maze) << 1) - 1
        for mx in range(len(mazeRow) << 1):
            if self.map[my][mx] != 0:
                self.map[my + 1][mx] = ALL
        # __________________________________________________
        # Contour walls
        # This is kinda weird because we are inverting the meaning of the
        # flags.  They no longer represent connections between squares, but
        # connections between walls.  Therefore a tile mapping from a number
        # with the NORTH bit set should illustrate that an obstruction extends
        # to the North.
        for my in range(len(self.map)):
            for mx in range(len(self.map[0])):
                if self.map[my][mx] == ALL:
                    v = ALL
                    if ((my == 0) or (self.map[my - 1][mx] & ALL == 0)):
                        v &= ~NORTH
                    if ((my == (len(self.map) - 1)) or
                        (self.map[my + 1][mx] & ALL == 0)):
                        v &= ~SOUTH
                    if ((mx == 0) or (self.map[my][mx - 1] & ALL == 0)):
                        v &= ~WEST
                    if ((mx == (len(self.map[0]) - 1)) or
                        (self.map[my][mx + 1] & ALL == 0)):
                        v &= ~EAST
                    if v > 0:
                        self.map[my][mx] = v
                    else:
                        self.map[my][mx] = OBS
        # __________________________________________________
        # Translate to the tile set.
        translateRow = lambda row : list(map(mazeTileMap.__getitem__, row))
        self.map = list(map(translateRow, self.map))

# ______________________________________________________________________
# Main routine

class EditorAppData (object):
    # ____________________________________________________________
    def __init__ (self, screen, tileMap):
        self.crntTileIndex = 0
        self.dx = 0
        self.dy = 0
        self.dt = 0
        self.crntView = Rect(0, 0, 15, 15)
        self.screen = screen
        self.tileMap = tileMap
        self.tileCount = ((tileMap.tileSurf.get_width() // 32) *
                          (tileMap.tileSurf.get_height() // 32))

    # ____________________________________________________________
    def doIncTile (self):
        if self.crntTileIndex < self.tileCount - 1:
            self.crntTileIndex += 1
            self.showCrntTile()

    # ____________________________________________________________
    def doDecTile (self):
        if self.crntTileIndex > 0:
            self.crntTileIndex -= 1
            self.showCrntTile()

    # ____________________________________________________________
    def showCrntTile (self):
        tileRects = []
        underflow = max(0, self.crntTileIndex + 5 - self.tileCount)
        minTile = max(0, self.crntTileIndex - 4 - underflow)
        overflow = min(self.crntTileIndex - 4, 0)
        maxTile = min(self.tileCount - 1, self.crntTileIndex + 4 - overflow)
        y = 1
        self.screen.fill((0, 0, 0, 255), (480, 0, 34, 480))
        for index in range(minTile, maxTile + 1):
            tileRect = self.tileMap.getTileRect(index)
            if index == self.crntTileIndex:
                self.screen.fill((255, 255, 255, 255), (480, y - 1, 1, 34))
                self.screen.fill((255, 255, 255, 255), (513, y - 1, 1, 34))
                self.screen.fill((255, 255, 255, 255), (480, y - 1, 34, 1))
                self.screen.fill((255, 255, 255, 255), (480, y + 33, 34, 1))
            self.screen.blit(self.tileMap.tileSurf, (481, y), tileRect)
            y += 34

    # ____________________________________________________________
    def updateView (self):
        dx = self.dx
        dy = self.dy
        dt = self.dt
        if dx != 0 or dy != 0:
            tx = self.crntView[0] + dx
            ty = self.crntView[1] + dy
            maxX = self.tileMap.mapSize[0] - self.crntView[2] + 1
            maxY = self.tileMap.mapSize[1] - self.crntView[3] + 1
            if (tx >= 0) and (tx < maxX):
                self.crntView[0] = tx
            if (ty >= 0) and (ty < maxY):
                self.crntView[1] = ty
        if dt != 0:
            if dt > 0:
                self.doIncTile()
            else:
                self.doDecTile()
        self.tileMap.blitMap(self.screen, self.crntView, (0,0), 0)

    # ____________________________________________________________
    def doSetTile (self, x, y, tileIndex = None):
        if tileIndex == None:
            tileIndex = self.crntTileIndex
        self.tileMap.map[y][x] = tileIndex

# ______________________________________________________________________

def main ():
    pygame.init()
    screenRect = Rect(0, 0, 514, 480)
    winstyle = 0
    bestdepth = pygame.display.mode_ok(screenRect.size, winstyle, 32)
    screen = pygame.display.set_mode(screenRect.size, winstyle, bestdepth)
    tileSurf = pygame.image.load("data/grid-1.1.bmp").convert()
    tileMap = TileMap(tileSurf, (32, 32), (63, 63))
    appData = EditorAppData(screen, tileMap)
    appData.showCrntTile()
    tk = tkinter.Tk()
    b = tkinter.Button(tk, text = "Up!", command = appData.doIncTile)
    b.pack()
    b = tkinter.Button(tk, text = "Down", command = appData.doDecTile)
    b.pack()
    tk.update()
    while True:
        # Get an event.
        event = pygame.event.poll()
        # Do something about it!
        if (event.type == QUIT):
            break
        elif (event.type == KEYDOWN):
            if (event.key == K_ESCAPE):
                break
            elif (event.key == 270):
                appData.dt += 1
                #appData.doIncTile()
            elif (event.key == 269):
                appData.dt -= 1
                #appData.doDecTile()
            elif (event.key == 273):
                appData.dy -= 1
            elif (event.key == 274):
                appData.dy += 1
            elif (event.key == 275):
                appData.dx += 1
            elif (event.key == 276):
                appData.dx -= 1
            elif (event.key == ord("r")):
                tileMap.randomMaze()
            else:
                print(event.key)
        elif (event.type == KEYUP):
            if (event.key == 273):
                appData.dy += 1
            elif (event.key == 274):
                appData.dy -= 1
            elif (event.key == 275):
                appData.dx -= 1
            elif (event.key == 276):
                appData.dx += 1
            elif (event.key == 270):
                appData.dt -= 1
                #appData.doIncTile()
            elif (event.key == 269):
                appData.dt += 1
                #appData.doDecTile()
        elif (event.type == MOUSEBUTTONDOWN):
            if (event.button in (1,3)):
                x, y = event.pos
                mapX = appData.crntView[0] + (x // 32)
                mapY = appData.crntView[1] + (y // 32)
                if appData.crntView.contains(mapX, mapY, 1, 1):
                    if (event.button == 1):
                        appData.doSetTile(mapX, mapY)
                    elif (event.button == 3):
                        appData.doSetTile(mapX, mapY, 0)
            elif (event.button == 4):
                appData.doIncTile()
            elif (event.button == 5):
                appData.doDecTile()
        appData.updateView()
        # Swap the display buffer all while avoiding fully loading the machine.
        pygame.display.flip()
        pygame.time.wait(10)
        tk.update()

# ______________________________________________________________________

if __name__ == "__main__":
    main()

# ______________________________________________________________________
# End of tileplay.py
