import math, array, random

import pygame
import pygame.locals as pgl

SPEED = 10
ANGLE_SPEED = int(SPEED / math.sqrt(2))
SCREENRECT = pygame.Rect(0, 0, 640, 480)
RIGHT, UP, LEFT, DOWN = range(4)
SIZE = 32
GRID_X_SIZE = SCREENRECT.width // SIZE

class TriangleSprite(pygame.sprite.Sprite):
    def __init__(self, *args, **kws):
        super(TriangleSprite, self).__init__(*args, **kws)
        self.size = SIZE #// 2
        self.base_image = pygame.Surface((self.size, self.size), pgl.SRCALPHA).convert_alpha()
        self.base_image.fill((0, 0, 0, 0))
        pygame.draw.polygon(self.base_image, (255, 255, 255, 255),
                            ((0, 0), (0, self.size - 1), (self.size - 1, self.size // 2 - 1)))
        self.base_images = tuple(pygame.transform.rotate(self.base_image, angle)
                                 for angle in (90 * index for index in range(4)))
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.direction = RIGHT
        self.clampping_methods = {
            (-1, -1): self._clamp_up_left,
            (-1, 0) : self._clamp_left,
            (-1, 1) : self._clamp_down_left,
            (0, -1) : self._clamp_up,
            (0, 1) : self._clamp_down,
            (1, -1) : self._clamp_up_right,
            (1, 0) : self._clamp_right,
            (1, 1) : self._clamp_down_right,
        }

    def _clamp_down_right(self, rect, obstructions):
        x2, y2 = rect.topleft
        x3, y3 = rect.bottomright
        x3 -= 1
        y3 -= 1
        gx2 = x2 // SIZE
        gx3 = x3 // SIZE
        gy2 = y2 // SIZE
        gy3 = y3 // SIZE
        upperright = obstructions[gx3 + (gy2 * GRID_X_SIZE)]
        lowerright = obstructions[gx3 + (gy3 * GRID_X_SIZE)]
        lowerleft = obstructions[gx2 + (gy3 * GRID_X_SIZE)]
        if upperright:
            rect.clamp_ip(pygame.Rect((gx3 - 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
        if lowerleft:
            rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy3 - 1) * SIZE, SIZE * 2, SIZE))
        elif lowerright and not upperright:
            ox0 = gx3 * SIZE
            oy0 = gy3 * SIZE
            dx = x3 - ox0
            dy = y3 - oy0
            if dx < dy:
                rect.clamp_ip(pygame.Rect((gx3 - 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
            elif dx == dy:
                rect.clamp_ip(pygame.Rect((gx3 - 1) * SIZE, (gy3 - 1) * SIZE, SIZE, SIZE))
            else:
                rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy3 - 1) * SIZE, SIZE * 2, SIZE))
        self.rect = rect

    def _clamp_up_right(self, rect, obstructions):
        x2, y2 = rect.topleft
        x3, y3 = rect.bottomright
        x3 -= 1
        y3 -= 1
        gx2 = x2 // SIZE
        gx3 = x3 // SIZE
        gy2 = y2 // SIZE
        gy3 = y3 // SIZE
        upperleft = obstructions[gx2 + (gy2 * GRID_X_SIZE)]
        upperright = obstructions[gx3 + (gy2 * GRID_X_SIZE)]
        lowerright = obstructions[gx3 + (gy3 * GRID_X_SIZE)]
        if upperleft:
            rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy2 + 1) * SIZE, SIZE * 2, SIZE))
        if lowerright:
            rect.clamp_ip(pygame.Rect((gx3 - 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
        elif upperright and not upperleft:
            ox0 = gx3 * SIZE
            oy1 = (gy2 * SIZE) + SIZE - 1
            dx = x3 - ox0
            dy = oy1 - y2
            if dx < dy:
                rect.clamp_ip(pygame.Rect((gx3 - 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
            elif dx == dy:
                rect.clamp_ip(pygame.Rect((gx3 - 1) * SIZE, (gy2 + 1) * SIZE, SIZE, SIZE))
            else:
                rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy2 + 1) * SIZE, SIZE * 2, SIZE))
        self.rect = rect

    def _clamp_down_left(self, rect, obstructions):
        x2, y2 = rect.topleft
        x3, y3 = rect.bottomright
        x3 -= 1
        y3 -= 1
        gx2 = x2 // SIZE
        gx3 = x3 // SIZE
        gy2 = y2 // SIZE
        gy3 = y3 // SIZE
        upperleft = obstructions[gx2 + (gy2 * GRID_X_SIZE)]
        lowerleft = obstructions[gx2 + (gy3 * GRID_X_SIZE)]
        lowerright = obstructions[gx3 + (gy3 * GRID_X_SIZE)]
        if upperleft:
            rect.clamp_ip(pygame.Rect((gx2 + 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
        if lowerright:
            rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy3 - 1)* SIZE, SIZE * 2, SIZE))
        elif lowerleft and not upperleft:
            ox1 = (gx2 * SIZE) + SIZE - 1
            oy0 = gy3 * SIZE
            dx = ox1 - x2
            dy = y3 - oy0
            if dx < dy:
                rect.clamp_ip(pygame.Rect((gx2 + 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
            elif dx == dy:
                rect.clamp_ip(pygame.Rect((gx2 + 1) * SIZE, (gy3 - 1) * SIZE, SIZE, SIZE))
            else:
                rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy3 - 1)* SIZE, SIZE * 2, SIZE))
        self.rect = rect

    def _clamp_up_left(self, rect, obstructions):
        x2, y2 = rect.topleft
        x3, y3 = rect.bottomright
        x3 -= 1
        y3 -= 1
        gx2 = x2 // SIZE
        gx3 = x3 // SIZE
        gy2 = y2 // SIZE
        gy3 = y3 // SIZE
        upperleft = obstructions[gx2 + (gy2 * GRID_X_SIZE)]
        lowerleft = obstructions[gx2 + (gy3 * GRID_X_SIZE)]
        upperright = obstructions[gx3 + (gy2 * GRID_X_SIZE)]
        if lowerleft:
            rect.clamp_ip(pygame.Rect((gx2 + 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
        if upperright:
            rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy2 + 1) * SIZE, SIZE * 2, SIZE))
        elif upperleft and not lowerleft:
            ox1 = (gx2 * SIZE) + SIZE - 1 # obstruction lower right
            oy1 = (gy2 * SIZE) + SIZE - 1
            dx = ox1 - x2 # ox1 > x2 so abs(x2 - ox1) = -(x2 - ox1) = this
            dy = oy1 - y2
            if dx < dy:
                rect.clamp_ip(pygame.Rect((gx2 + 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
            elif dx == dy:
                rect.clamp_ip(pygame.Rect((gx2 + 1) * SIZE, (gy2 + 1) * SIZE, SIZE, SIZE))
            else:
                rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy2 + 1) * SIZE, SIZE * 2, SIZE))
        self.rect = rect

    def _clamp_up(self, rect, obstructions):
        x2, y2 = rect.topleft
        x3 = rect.right - 1
        gx2 = x2 // SIZE
        gx3 = x3 // SIZE
        gy2 = y2 // SIZE
        if obstructions[gx2 + (gy2 * GRID_X_SIZE)] or obstructions[gx3 + (gy2 * GRID_X_SIZE)]:
            rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy2 + 1) * SIZE, SIZE * 2, SIZE))
        self.rect = rect

    def _clamp_left(self, rect, obstructions):
        x2, y2 = rect.topleft
        y3 = rect.bottom - 1
        gx2 = x2 // SIZE
        gy2 = y2 // SIZE
        gy3 = y3 // SIZE
        if obstructions[gx2 + (gy2 * GRID_X_SIZE)] or obstructions[gx2 + (gy3 * GRID_X_SIZE)]:
            rect.clamp_ip(pygame.Rect((gx2 + 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
        self.rect = rect

    def _clamp_down(self, rect, obstructions):
        x2, y3 = rect.bottomleft
        y3 -= 1
        x3 = rect.right - 1
        gx2 = x2 // SIZE
        gx3 = x3 // SIZE
        gy3 = y3 // SIZE
        if obstructions[gx2 + (gy3 * GRID_X_SIZE)] or obstructions[gx3 + (gy3 * GRID_X_SIZE)]:
            rect.clamp_ip(pygame.Rect(gx2 * SIZE, (gy3 - 1) * SIZE, SIZE * 2, SIZE))
        self.rect = rect

    def _clamp_right(self, rect, obstructions):
        x3, y2 = rect.topright
        x3 -= 1
        y3 = rect.bottom - 1
        gx3 = x3 // SIZE
        gy2 = y2 // SIZE
        gy3 = y3 // SIZE
        if obstructions[gx3 + (gy2 * GRID_X_SIZE)] or obstructions[gx3 + (gy3 * GRID_X_SIZE)]:
            rect.clamp_ip(pygame.Rect((gx3 - 1) * SIZE, gy2 * SIZE, SIZE, SIZE * 2))
        self.rect = rect

    def _move_within_obstructions(self, dx, dy, obstructions):
        rect = self.rect.move(dx, dy).clamp(SCREENRECT)
        dx_sign = (0 < dx) - (dx < 0)
        dy_sign = (0 < dy) - (dy < 0)
        clampping_method = self.clampping_methods.get((dx_sign, dy_sign))
        clampping_method(rect, obstructions)

    def move(self, dx, dy, obstructions):
        if dx or dy:
            old_direction = self.direction
            direction = {-1: UP,   0: old_direction, 1: DOWN}[dy]
            direction = {-1: LEFT, 0: direction, 1: RIGHT}[dx]
            if direction != old_direction:
                self.direction = direction
                self.image = self.base_images[direction]
            speed = SPEED
            if dx and dy:
                speed = ANGLE_SPEED
            dx *= speed
            dy *= speed
            self._move_within_obstructions(dx, dy, obstructions)

SENSITIVITY = 0.333

def handle_axis(axis_value):
    if axis_value < -SENSITIVITY:
        return -1
    elif axis_value > SENSITIVITY:
        return 1
    return 0

def handle_joystick(x_axis, y_axis, joystick):
    if not x_axis:
        x_axis = handle_axis(joystick.get_axis(0))
    if not y_axis:
        y_axis = handle_axis(joystick.get_axis(1))
    return x_axis, y_axis

def main():
    pygame.init()
    pygame.joystick.init()
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    screen = pygame.display.set_mode(SCREENRECT.size)
    background = pygame.Surface(SCREENRECT.size).convert()
    background.fill((0, 127, 0))
    grid_y_size = SCREENRECT.height // SIZE
    grid_size = GRID_X_SIZE * grid_y_size
    grid = array.array('B', [random.choice((0, 0, 0, 1)) for _ in range(grid_size)])
    grid[0] = 0
    the_rect = pygame.Rect(0, 0, SIZE, SIZE)
    for index in range(grid_size):
        if grid[index]:
            pygame.draw.rect(background, (0, 63, 0), the_rect)
        the_rect.move_ip(SIZE, 0)
        if the_rect.x >= SCREENRECT.width:
            the_rect.x = 0
            the_rect.y += SIZE
    screen.blit(background, (0, 0))
    pygame.display.update()
    clock = pygame.time.Clock()
    sprites = pygame.sprite.RenderUpdates()
    triangle = TriangleSprite(sprites)
    while True:
        for event in pygame.event.get():
            if (event.type == pgl.QUIT) or ((event.type == pgl.KEYDOWN) and (event.key == pgl.K_ESCAPE)):
                return
        sprites.clear(screen, background)
        keys = pygame.key.get_pressed()
        x_axis = keys[pgl.K_RIGHT] - keys[pgl.K_LEFT]
        y_axis = keys[pgl.K_DOWN] - keys[pgl.K_UP]
        if joystick:
            x_axis, y_axis = handle_joystick(x_axis, y_axis, joystick)
        triangle.move(x_axis, y_axis, grid)
        sprites.update()
        dirty = sprites.draw(screen)
        pygame.display.update(dirty)
        clock.tick(30)

if __name__ == '__main__':
    main()
