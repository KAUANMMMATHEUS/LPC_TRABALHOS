import pygame.sprite
from constants import *

def get_image(sheet, frame, width, height, scale, colour):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), ((frame * width), 0, width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    image.set_colorkey(colour)

    return image

class Megaman(pygame.sprite.Sprite):

    def __init__(self, sprite_sheet, sprite_width, sprite_height, sprite_quantity, sprite_scale):
        super().__init__()

        try:
            sprite_sheet_image = pygame.image.load(sprite_sheet).convert_alpha()
            print(f"Successfully loaded sprite sheet: {sprite_sheet}")
        except Exception as e:
            print(f"Error loading sprite sheet {sprite_sheet}: {str(e)}")

        self.sprites = []

        for frame_index in range(sprite_quantity):
            self.sprites.append(get_image(sprite_sheet_image, frame_index, sprite_width, sprite_height, sprite_scale, COLOR_WHITE))

        self.index = 0
        self.image = self.sprites[self.index]

        self.rect = self.image.get_rect()

        self.rect.topleft = 100, 100

        self.animate = False

    def update(self):
        if self.animate:
            self.index = self.index + 0.05
            if self.index >= len(self.sprites):
                self.index = 0
                self.animate = False
            self.image = self.sprites[int(self.index)]

            self.move(1, 0)

    def move(self, d_x, d_y):
        self.rect.x += d_x
        self.rect.y += d_y

        if self.rect.x >= (SCREEN_WIDTH - 24):
            self.rect.x = 100

    def walk(self):
        self.animate = True
        self.image = self.sprites[0]  # Ensure initial sprite is visible

    def shoot(self):
        self.animate = True
        self.image = self.sprites[0]  # Ensure initial sprite is visible

    def jump(self):
        self.animate = True
        self.image = self.sprites[0]  # Ensure initial sprite is visible


    def walk(self):
        self.attack()


    def jump(self):
        self.attack()


    def shoot(self):
        self.attack()


    def attack(self):
        self.animate = True