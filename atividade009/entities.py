# entities.py
import random
import pygame

from constants import (
    PLAYER_SPEED,
    PLAYER_SIZE,
    BULLET_SPEED,
    BULLET_SIZE,
    EXPLOSION_FRAMES,
    EXPLOSION_SIZE,
    EXPLOSION_DURATION,
    ZOMBIE_SIZE,
    ZOMBIE_SPEED,
    ZOMBIE_MAX_HP,
    PLAYER_MAX_HP,
    WORLD_WIDTH, WORLD_HEIGHT, WIDTH, HEIGHT,
    PISTOL_COOLDOWN

)
from utils import load_image, draw_health_bar, tint_surface


class Player:
    def __init__(self, world_pos):
        self.world_pos = world_pos
        self.sprites = {}
        self._load_sprites()
        self.direction_name = "down"
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.12
        self.image = self.sprites[self.direction_name][self.frame_index]
        self.rect = self.image.get_rect()
        self.speed = PLAYER_SPEED
        self.last_shot_time = 0
        self.pistol_cooldown = BULLET_SPEED * 0 + 250  # preserva o valor 250 sem mudar lógica

        self.base_max_hp = PLAYER_MAX_HP
        self.max_hp = self.base_max_hp
        self.hp = self.max_hp

        self.damage_multiplier = 1
        self.max_ammo = 120
        self.ammo = 30
        self.grenades = 1
        self.hit_cooldown = 500
        self.last_hit_time = 0

    def _load_sprites(self):
        for d in ("up", "down", "left", "right"):
            frames = []
            if d in ("up", "down"):
                size = (int(PLAYER_SIZE[0] * 0.75), PLAYER_SIZE[1])
            else:
                size = PLAYER_SIZE
            for i in range(6):
                frames.append(load_image(f"player_{d}_{i}.png", size))
            self.sprites[d] = frames

    @property
    def screen_pos(self):
        return pygame.Vector2(WIDTH // 2, HEIGHT // 2)

    def update(self, dt, keys, gamepad_dir=None):
        vec = pygame.Vector2(0, 0)
        # prefer gamepad direction if provided
        if gamepad_dir is not None and isinstance(gamepad_dir, pygame.Vector2) and gamepad_dir.length_squared() > 0:
            vec = gamepad_dir
        else:
            if keys[pygame.K_w]:
                vec.y -= 1
            if keys[pygame.K_s]:
                vec.y += 1
            if keys[pygame.K_a]:
                vec.x -= 1
            if keys[pygame.K_d]:
                vec.x += 1

        moving = vec.length_squared() > 0
        if moving:
            if abs(vec.x) > abs(vec.y):
                self.direction_name = "right" if vec.x > 0 else "left"
            else:
                self.direction_name = "down" if vec.y > 0 else "up"
            vec = vec.normalize()
            self.world_pos += vec * self.speed * dt

        half = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.world_pos.x = max(half.x, min(self.world_pos.x, WORLD_WIDTH - half.x))
        self.world_pos.y = max(half.y, min(self.world_pos.y, WORLD_HEIGHT - half.y))

        self._update_animation(dt, moving)

    def _update_animation(self, dt, moving):
        if moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % 6
        else:
            self.frame_index = 0
        self.image = self.sprites[self.direction_name][self.frame_index]

    def can_shoot(self, t):
        return (t - self.last_shot_time) >= PISTOL_COOLDOWN and self.ammo > 0

    def shoot(self, dir_vec, bullets, t):
        if not self.can_shoot(t):
            return
        b = Bullet(self.world_pos.copy(), dir_vec.normalize())
        bullets.append(b)
        self.ammo -= 1
        self.last_shot_time = t


class Bullet:
    def __init__(self, pos, direction):
        self.world_pos = pos
        self.direction = direction
        self.speed = BULLET_SPEED
        base = load_image("bullet.png", BULLET_SIZE)
        angle = 0
        if direction.x > 0:
            angle = -90
        elif direction.x < 0:
            angle = 90
        elif direction.y > 0:
            angle = 180
        self.image = pygame.transform.rotate(base, angle)
        self.rect = self.image.get_rect()
        self.max_distance = 800
        self.traveled_distance = 0
        self.alive = True

    def update(self, dt):
        self.move(dt)

    def move(self, dt):
        move = self.direction * self.speed * dt
        self.world_pos += move
        self.traveled_distance += move.length()
        if self.world_pos.x < 0 or self.world_pos.x > WORLD_WIDTH:
            pass
        if self.world_pos.y < 0 or self.world_pos.y > WORLD_HEIGHT:
            pass

    def is_expired(self):
        if self.traveled_distance >= self.max_distance:
            return True
        if not (0 <= self.world_pos.x <= WORLD_WIDTH):
            return True
        if not (0 <= self.world_pos.y <= WORLD_HEIGHT):
            return True
        return False


class Explosion:
    frames = []

    @classmethod
    def load_frames(cls):
        if cls.frames:
            return
        for f in EXPLOSION_FRAMES:
            cls.frames.append(load_image(f, EXPLOSION_SIZE))

    def __init__(self, pos):
        Explosion.load_frames()
        self.world_pos = pos
        self.start = pygame.time.get_ticks()
        self.frame = 0
        self.image = Explosion.frames[0]
        self.rect = self.image.get_rect()

    def update(self):
        elapsed = pygame.time.get_ticks() - self.start
        self.frame = min(2, int((elapsed / EXPLOSION_DURATION) * 3))
        self.image = Explosion.frames[self.frame]
        return elapsed >= EXPLOSION_DURATION

    def draw(self, surf, cam):
        pos = self.world_pos - cam
        self.rect.center = (int(pos.x), int(pos.y))
        surf.blit(self.image, self.rect)


class Enemy:
    _sprites = {}

    def __init__(self, pos, is_boss=False):
        self.world_pos = pos
        if not Enemy._sprites:
            self._load_sprites()

        self.is_boss = is_boss
        self.direction = "down"
        self.frame = 0
        self.timer = 0

        multiplier = random.choices(
            [1.0, 1.75, 2.5, 3.0],
            weights=[2, 5, 2, 0.1],
            k=1
        )[0]
        self.speed = ZOMBIE_SPEED * multiplier

        if self.is_boss:
            scale = 2.5
            self.sprites = {}
            for d, frames in Enemy._sprites.items():
                scaled_frames = []
                for img in frames:
                    w = int(img.get_width() * scale)
                    h = int(img.get_height() * scale)
                    scaled = pygame.transform.smoothscale(img, (w, h))
                    scaled = tint_surface(scaled, (0, 45, 0))
                    scaled_frames.append(scaled)
                self.sprites[d] = scaled_frames
                self.speed *= 0.95
        else:
            self.sprites = Enemy._sprites

        self.max_hp = ZOMBIE_MAX_HP * (10 if self.is_boss else 1)
        self.hp = self.max_hp

        self.image = self.sprites["down"][0]
        self.rect = self.image.get_rect()

    @classmethod
    def _load_sprites(cls):
        for d in ("up", "down", "left", "right"):
            cls._sprites[d] = [load_image(f"zombie_{d}_{i}.png", ZOMBIE_SIZE) for i in range(6)]

    def update(self, dt, player_pos):
        vec = player_pos - self.world_pos
        if vec.length_squared() > 0:
            self.world_pos += vec.normalize() * self.speed * dt
            self.direction = (
                "right"
                if abs(vec.x) > abs(vec.y) and vec.x > 0
                else "left"
                if abs(vec.x) > abs(vec.y)
                else "down"
                if vec.y > 0
                else "up"
            )
            self.timer += dt
            if self.timer >= 0.15:
                self.timer = 0
                self.frame = (self.frame + 1) % 6
                self.image = self.sprites[self.direction][self.frame]

    def draw(self, surf, cam):
        pos = self.world_pos - cam
        self.rect.center = (int(pos.x), int(pos.y))
        surf.blit(self.image, self.rect)

        bar_width = 60 if not self.is_boss else 140
        draw_health_bar(
            surf,
            (self.rect.centerx, self.rect.top - 8),
            bar_width,
            6,
            self.hp,
            self.max_hp,
        )


class Item:
    def __init__(self, pos, t):
        self.world_pos = pos
        self.type = t
        if t == "medkit":
            self.image = load_image("medkit.png", (48, 48))
        elif t == "bullet_pack":
            self.image = load_image("bullet_pack.png", (48, 48))
        elif t == "double_bullets":
            self.image = load_image("double_bullets.png", (48, 48))
        elif t == "armor":
            self.image = load_image("armor.png", (48, 48))
        elif t == "grenade":
            self.image = load_image("grenade.png", (48, 48))
        else:
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(pos.x, pos.y))

    def draw(self, surf, cam):
        pos = self.world_pos - cam
        self.rect.center = (int(pos.x), int(pos.y))
        surf.blit(self.image, self.rect)


class Grenade:
    def __init__(self, pos, fuse_time=3000):
        self.world_pos = pos
        self.fuse_time = fuse_time
        self.start_time = pygame.time.get_ticks()
        self.image = load_image("grenade.png", (48, 48))
        self.rect = self.image.get_rect(center=(pos.x, pos.y))

    def update(self):
        now = pygame.time.get_ticks()
        return (now - self.start_time) >= self.fuse_time

    def draw(self, surf, cam):
        pos = self.world_pos - cam
        self.rect.center = (int(pos.x), int(pos.y))
        surf.blit(self.image, self.rect)
