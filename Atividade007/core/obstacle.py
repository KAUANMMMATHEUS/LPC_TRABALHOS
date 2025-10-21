import pygame

class Obstacle:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)

    def draw(self, screen):
        pygame.draw.rect(screen, (128, 128, 128), self.rect)
