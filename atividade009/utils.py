# utils.py
import pygame
from constants import ASSETS_DIR


def load_image(filename, size=None, fallback_color=(255, 255, 255)):
    path = ASSETS_DIR / filename
    if path.exists():
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    surf = pygame.Surface(size or (40, 40), pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf


def load_sound(filename, volume=1.0):
    path = ASSETS_DIR / filename
    if path.exists():
        snd = pygame.mixer.Sound(path.as_posix())
        snd.set_volume(volume)
        return snd
    return None


def draw_health_bar(surface, center_pos, width, height, hp, max_hp):
    ratio = max(0.0, min(1.0, hp / max_hp))
    x = center_pos[0] - width // 2
    y = center_pos[1] - height // 2
    pygame.draw.rect(surface, (100, 0, 0), (x, y, width, height))
    pygame.draw.rect(surface, (0, 200, 0), (x, y, int(width * ratio), height))
    pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 1)


def tint_surface(surf, tint_color):
    tinted = surf.copy()
    r, g, b = tint_color
    tint_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    tint_surf.fill((r, g, b, 0))
    tinted.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted


def draw_multiline_center(surface, text, font, color, center_x, start_y, max_width, line_height=None):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        if not current:
            current = w
        else:
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = w
    if current:
        lines.append(current)

    if line_height is None:
        line_height = font.get_linesize()

    y = start_y
    for line in lines:
        surf = font.render(line, True, color)
        rect = surf.get_rect(center=(center_x, y))
        surface.blit(surf, rect)
        y += line_height
    return y
