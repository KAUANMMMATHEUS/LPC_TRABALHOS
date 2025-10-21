import pygame
import math
from core.bullet import Bullet

class TankPlayer:
    SPRITE_ROWS = 8
    SPRITE_COLS = 8
    PIXEL_SIZE = 6

    # 8-directional tank sprites: UP, UP-RIGHT, RIGHT, DOWN-RIGHT, DOWN, DOWN-LEFT, LEFT, UP-LEFT
    TANK_SPRITES = [
        # UP
        [
            '    X   ',
            '    X   ',
            ' XX X XX',
            ' XXXXXXX',
            ' XXXXXXX',
            ' XXXXXXX',
            ' XX   XX',
            ' XX   XX',
        ],
        # UP-RIGHT
        [
            '   XX  X',
            '  XXX X ',
            ' XXXXX  ',
            'XXXXXXXX',
            'XX XXXXX',
            '    XXX ',
            '   XXX  ',
            '   XX   ',
        ],
        # RIGHT
        [
            '        ',
            'XXXXXX  ',
            'XXXXXX  ',
            '  XXX   ',
            '  XXXXXX',
            '  XXX   ',
            'XXXXXX  ',
            'XXXXXX  ',
        ],
        # DOWN-RIGHT
        [
            '   XXX  ',
            ' XXXX   ',
            'XXXXX XX',
            'XXXXX   ',
            '   XXX  ',
            '   XXXXX',
            '  XXXXX ',
            '   XX   ',
        ],
        # DOWN
        [
            ' XX   XX',
            ' XX   XX',
            ' XXXXXXX',
            ' XXXXXXX',
            ' XXXXXXX',
            ' XX X XX',
            '    X   ',
            '    X   ',
        ],
        # DOWN-LEFT
        [
            '   XX   ',
            '  XXX   ',
            '  XXXXX ',
            '   XXXXX',
            '   XXX  ',
            'XXXXX   ',
            'XXXXX XX',
            ' XXXX   ',
        ],
        # LEFT
        [
            '        ',
            '  XXXXXX',
            '  XXXXXX',
            '   XXX  ',
            'XXXXXX  ',
            '   XXX  ',
            '  XXXXXX',
            '  XXXXXX',
        ],
        # UP-LEFT
        [
            ' X  XX  ',
            ' X XXX  ',
            '  XXXXX ',
            'XXXXXXXX',
            'XXXXX XX',
            ' XXX    ',
            '  XXX   ',
            '   XX   ',
        ],
    ]

    def __init__(self, x, y, left, right, up, down, fire, color, angle = 0):
        self.spawn_x = x
        self.spawn_y = y
        self.x = x
        self.y = y
        self.angle = angle
        self.bullet_angle = angle - 90
        self.rect = pygame.Rect(x, y, self.SPRITE_COLS * self.PIXEL_SIZE, self.SPRITE_ROWS * self.PIXEL_SIZE)
        self.keys = dict(left=left, right=right, up=up, down=down, fire=fire)
        self.color = color
        self.last_fire = 0
        self.bullet = None
        self.owner = self
        self.speed = 0

    def get_sprite_index(self):
        ang = (self.angle % 360)
        if ang >= 337.5 or ang < 22.5:
            return 0  # Up
        elif 22.5 <= ang < 67.5:
            return 1  # Up-Right
        elif 67.5 <= ang < 112.5:
            return 2  # Right
        elif 112.5 <= ang < 157.5:
            return 3  # Down-Right
        elif 157.5 <= ang < 202.5:
            return 4  # Down
        elif 202.5 <= ang < 247.5:
            return 5  # Down-Left
        elif 247.5 <= ang < 292.5:
            return 6  # Left
        else:
            return 7  # Up-Left

    def get_center_of_sprite(self):
        center_x = self.x + self.rect.width // 2
        center_y = self.y + self.rect.height // 2
        return center_x, center_y

    def handle_event(self, event, bullets):
        if event.type == pygame.KEYDOWN:
            if (
                event.key == self.keys["fire"]
                and self.bullet is None
                and pygame.time.get_ticks() - self.last_fire > 400
            ):
                bullet_x, bullet_y = self.get_center_of_sprite()
                bullet = Bullet(bullet_x, bullet_y, self.bullet_angle, self)
                bullets.append(bullet)
                self.bullet = bullet
                self.last_fire = pygame.time.get_ticks()
            # Steer bullet left/right after firing
            if self.bullet and self.bullet.alive:
                if event.key == self.keys["left"]:
                    self.bullet.steer_left()
                elif event.key == self.keys["right"]:
                    self.bullet.steer_right()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[self.keys["left"]]:
            self.angle -= 4
            self.bullet_angle = self.angle - 90
        if keys[self.keys["right"]]:
            self.angle += 4
            self.bullet_angle = self.angle - 90
        move_vec = pygame.math.Vector2(0, 0)
        if keys[self.keys["up"]]:
            move_vec = pygame.math.Vector2(3, 0).rotate(-self.angle)
            self.speed = 3
        elif keys[self.keys["down"]]:
            move_vec = pygame.math.Vector2(-2, 0).rotate(-self.angle)
            self.speed = -2
        else:
            self.speed = 0
        self.x += move_vec.x
        self.y += move_vec.y
        self.x = max(0, min(self.x, 800 - self.rect.width))
        self.y = max(0, min(self.y, 600 - self.rect.height))
        self.rect.topleft = (self.x, self.y)
        if self.bullet and not self.bullet.alive:
            self.bullet = None

    def respawn(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        # self.angle = 0
        self.rect.topleft = (self.x, self.y)
        self.bullet = None

    def draw(self, screen):
        sprite = self.TANK_SPRITES[self.get_sprite_index()]
        surf = pygame.Surface((self.SPRITE_COLS * self.PIXEL_SIZE, self.SPRITE_ROWS * self.PIXEL_SIZE), pygame.SRCALPHA)
        for row_idx, row in enumerate(sprite):
            for col_idx, ch in enumerate(row):
                if ch == 'X':
                    pygame.draw.rect(
                        surf,
                        self.color,
                        pygame.Rect(col_idx * self.PIXEL_SIZE, row_idx * self.PIXEL_SIZE, self.PIXEL_SIZE, self.PIXEL_SIZE)
                    )
        screen.blit(surf, (int(self.x), int(self.y)))
