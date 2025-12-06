import pygame
from pygame.locals import *

from Megaman import Megaman
from constants import *

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

all_sprites_group = pygame.sprite.Group()

sprite_walking = Megaman(MEGAMAN_WALKING_SPRITE_SHEET,  MEGAMAN_WALKING_SPRITE_WIDTH, MEGAMAN_WALKING_SPRITE_HEIGHT, MEGAMAN_WALKING_SPRITE_SHEET_SIZE, 2)
sprite_shooting = Megaman(MEGAMAN_SHOOTING_SPRITE_SHEET, MEGAMAN_SHOOTING_SPRITE_WIDTH, MEGAMAN_SHOOTING_SPRITE_HEIGHT, MEGAMAN_SHOOTING_SPRITE_SHEET_SIZE, 2)
sprite_jumping = Megaman(MEGAMAN_JUMPING_SPRITE_SHEET, MEGAMAN_JUMPING_SPRITE_WIDTH, MEGAMAN_JUMPING_SPRITE_HEIGHT, MEGAMAN_JUMPING_SPRITE_SHEET_SIZE, 2)

# Add initial sprite to the group
all_sprites_group.add(sprite_walking)
sprite_walking.image = sprite_walking.sprites[0]  # Show initial frame

is_running = True

while is_running:
    screen.fill(COLOR_BLACK)

    for event in pygame.event.get():
        if event.type == QUIT:
            is_running = False

        if event.type == pygame.KEYDOWN and event.key == K_RIGHT:
            all_sprites_group.empty()
            all_sprites_group.add(sprite_walking)
            sprite_walking.walk()

        if event.type == pygame.KEYDOWN and event.key == K_SPACE:
            all_sprites_group.empty()
            all_sprites_group.add(sprite_jumping)
            sprite_jumping.jump()

        if event.type == pygame.KEYDOWN and event.key == K_RETURN:
            all_sprites_group.empty()
            all_sprites_group.add(sprite_shooting)
            sprite_shooting.shoot()

    all_sprites_group.draw(screen)
    all_sprites_group.update()

    pygame.display.flip()

pygame.quit()