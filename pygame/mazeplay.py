import array
import random

from spriteplay import SCREENRECT, TriangleSprite, handle_joystick
from tileplay import TileMap

import pygame
from pygame.locals import *

MAZE_WIDTH = 64
MAZE_HEIGHT = 64

def print_obstructions(grid):
    for index in range(len(grid)):
        if index % 20 == 0:
            print()
        print(grid[index], end='')
    print()

def obstructions_from_map(tile_map, source_rect):
    x_range = range(source_rect.x, source_rect.x + source_rect.width)
    y_range = range(source_rect.y, source_rect.y + source_rect.height)
    xy_range = ((x, y) for y in y_range for x in x_range)
    return array.array('B', (tile_map.map[y][x] < 17 for (x, y) in xy_range))

def find_empty_tile(tile_map):
    x_range = range(tile_map.mapSize[0])
    y_range = range(tile_map.mapSize[1])
    xy_range = ((x, y) for y in y_range for x in x_range if tile_map.map[y][x] == 17)
    return random.choice(tuple(xy_range))

def main():
    pygame.init()
    pygame.joystick.init()
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    screen = pygame.display.set_mode(SCREENRECT.size)
    tile_surface = pygame.image.load('data/grid-1.1.bmp').convert()
    tile_map = TileMap(tile_surface, (32, 32), (MAZE_WIDTH, MAZE_HEIGHT))
    tile_map.randomMaze()
    exit_x, exit_y = find_empty_tile(tile_map)
    exit_rect = Rect(exit_x, exit_y, 1, 1)
    tile_map.map[exit_y][exit_x] = 18
    print('Exit:', (exit_x, exit_y))
    entrance_x, entrance_y = tile_map.entrance
    view_rect = Rect(entrance_x - 10, entrance_y - 7, 20, 15).clamp(tile_map.boundRect)
    clock = pygame.time.Clock()
    sprites = pygame.sprite.RenderUpdates()
    triangle = TriangleSprite(sprites)
    triangle.rect.move_ip((entrance_x - view_rect.x) * 32, (entrance_y - view_rect.y) * 32)
    grid = obstructions_from_map(tile_map, view_rect)
    stay_rect = Rect(32, 32, 18 * 32, 13 * 32)
    stay_x, stay_y = stay_rect.bottomright
    while True:
        for event in pygame.event.get():
            if (event.type == QUIT) or ((event.type == KEYDOWN) and (event.key == K_ESCAPE)):
                return
        keys = pygame.key.get_pressed()
        x_axis = keys[K_RIGHT] - keys[K_LEFT]
        y_axis = keys[K_DOWN] - keys[K_UP]
        if joystick:
            x_axis, y_axis = handle_joystick(x_axis, y_axis, joystick)
        triangle.move(x_axis, y_axis, grid)
        if view_rect.contains(exit_rect):
            exit_pixel_rect = Rect((exit_x - view_rect.x) * 32, (exit_y - view_rect.y) * 32, 32, 32)
            if exit_pixel_rect.colliderect(triangle.rect):
                tile_map = TileMap(tile_surface, (32, 32), (MAZE_WIDTH, MAZE_HEIGHT))
                tile_map.randomMaze()
                exit_x, exit_y = find_empty_tile(tile_map)
                exit_rect = Rect(exit_x, exit_y, 1, 1)
                tile_map.map[exit_y][exit_x] = 18
                print('Exit:', (exit_x, exit_y))
                entrance_x, entrance_y = tile_map.entrance
                view_rect = Rect(entrance_x - 10, entrance_y - 7, 20, 15).clamp(tile_map.boundRect)
                triangle.rect.x = (entrance_x - view_rect.x) * 32
                triangle.rect.y = (entrance_y - view_rect.y) * 32
                grid = obstructions_from_map(tile_map, view_rect)
                continue
        if not stay_rect.contains(triangle.rect):
            # Scroll
            sprite_x0, sprite_y0 = triangle.rect.topleft
            sprite_x1, sprite_y1 = triangle.rect.bottomright
            if sprite_x0 < 32:
                view_rect.move_ip(-1, 0)
                triangle.rect.move_ip(32, 0)
            elif sprite_x1 >= stay_x:
                view_rect.move_ip(1, 0)
                triangle.rect.move_ip(-32, 0)
            if sprite_y0 < 32:
                view_rect.move_ip(0, -1)
                triangle.rect.move_ip(0, 32)
            elif sprite_y1 >= stay_y:
                view_rect.move_ip(0, 1)
                triangle.rect.move_ip(0, -32)
            grid = obstructions_from_map(tile_map, view_rect)
        tile_map.blitMap(screen, view_rect, (0, 0))
        sprites.draw(screen)
        pygame.display.update()
        clock.tick(30)

if __name__ == '__main__':
    main()
