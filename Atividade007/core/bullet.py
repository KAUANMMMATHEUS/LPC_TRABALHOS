import pygame
import math

class Bullet:
    SPEED = 7
    SIZE = 6

    def __init__(self, x, y, angle, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.alive = True

    def update(self):
        rad = math.radians(-self.angle)
        self.x += self.SPEED * math.cos(rad)
        self.y += self.SPEED * math.sin(rad)
        self.rect.topleft = (self.x, self.y)
        # Bullet disappears if off screen (no ricochet yet)
        if not (0 <= self.x <= 800 and 0 <= self.y <= 600):
            self.alive = False

    def steer_left(self):
        self.angle -= 4

    def steer_right(self):
        self.angle += 4

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, (255, 255, 0), self.rect)
