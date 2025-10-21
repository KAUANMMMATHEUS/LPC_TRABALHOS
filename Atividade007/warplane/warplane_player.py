import pygame
from core.bullet import Bullet

class WarplanePlayer:
    WIDTH = 50
    HEIGHT = 20

    def __init__(self, x, y, left, right, up, down, fire, color):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.keys = dict(left=left, right=right, up=up, down=down, fire=fire)
        self.color = color
        self.last_fire = 0
        self.owner = self

    def handle_event(self, event, bullets):
        if event.type == pygame.KEYDOWN:
            if event.key == self.keys["fire"] and pygame.time.get_ticks() - self.last_fire > 400:
                bullet = Bullet(self.x+self.WIDTH//2, self.y+self.HEIGHT//2, self.angle, self)
                bullets.append(bullet)
                self.last_fire = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[self.keys["left"]]:
            self.angle -= 2
        if keys[self.keys["right"]]:
            self.angle += 2
        if keys[self.keys["up"]]:
            self.speed = 5
        elif keys[self.keys["down"]]:
            self.speed = -2
        else:
            self.speed = 0
        self.x += self.speed * pygame.math.Vector2(1,0).rotate(-self.angle).x
        self.y += self.speed * pygame.math.Vector2(1,0).rotate(-self.angle).y
        self.x = max(0, min(self.x, 800-self.WIDTH))
        self.y = max(0, min(self.y, 600-self.HEIGHT))
        self.rect.topleft = (self.x, self.y)

    def respawn(self):
        self.x = 100 if self.color == (255,0,0) else 700
        self.y = 300
        self.angle = 0
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(surf, self.color, [(0,10),(35,0),(49,10),(35,19)])
        rotated = pygame.transform.rotate(surf, self.angle)
        screen.blit(rotated, rotated.get_rect(center=self.rect.center))
