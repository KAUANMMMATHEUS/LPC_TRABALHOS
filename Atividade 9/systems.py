
import math
from random import uniform

import pygame as pg

import config as C
from sprites import Asteroid, Ship, UFO
from utils import Vec, rand_edge_pos, rand_unit_vec


class World:

    def __init__(self):
        self.ship = Ship(Vec(C.WIDTH / 2, C.HEIGHT / 2))
        self.bullets = pg.sprite.Group()
        self.ufo_bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group(self.ship)
        self.score = 0
        self.lives = C.START_LIVES
        self.wave = 0
        self.wave_cool = C.WAVE_DELAY
        self.safe = C.SAFE_SPAWN_TIME
        self.ufo_timer = C.UFO_SPAWN_EVERY

    def start_wave(self, sound=None):
        self.wave += 1
        count = 3 + self.wave
        for _ in range(count):
            pos = rand_edge_pos()
            while (pos - self.ship.pos).length() < 150:
                pos = rand_edge_pos()
            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed
            self.spawn_asteroid(pos, vel, "L")

    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str):
        a = Asteroid(pos, vel, size)
        self.asteroids.add(a)
        self.all_sprites.add(a)

    def spawn_ufo(self, sound=None):
        small = uniform(0, 1) < 0.5
        y = uniform(0, C.HEIGHT)
        x = 0 if uniform(0, 1) < 0.5 else C.WIDTH
        ufo = UFO(Vec(x, y), small)
        self.ufos.add(ufo)
        self.all_sprites.add(ufo)
        if sound:
            sound.play('ufo_small' if small else 'ufo_large', loops=3)

    def try_fire(self, sound=None):
        if len(self.bullets) >= C.MAX_BULLETS:
            return
        b = self.ship.fire()
        if b:
            self.bullets.add(b)
            self.all_sprites.add(b)
            if sound:
                sound.play('shoot')

    def hyperspace(self, sound=None):
        self.ship.hyperspace()
        self.score = max(0, self.score - C.HYPERSPACE_COST)
        if sound:
            sound.play('hyperspace')

    def update(self, dt: float, keys, sound=None):
        self.all_sprites.update(dt)
        self.ship.control(keys, dt, sound)

        if self.safe > 0:
            self.safe -= dt
            self.ship.invuln = 0.5
        self.ufo_timer -= dt
        if self.ufo_timer <= 0:
            self.spawn_ufo(sound)
            self.ufo_timer = C.UFO_SPAWN_EVERY

        for ufo in self.ufos:
            if ufo.small:
                ufo.pursue(self.ship.pos)
            if ufo.fire_cool <= 0:
                bullet = ufo.fire(self.ship.pos)
                self.ufo_bullets.add(bullet)
                self.all_sprites.add(bullet)
                if sound:
                    sound.play('ufo_shoot')

        self.handle_collisions(sound)

        if not self.asteroids and self.wave_cool <= 0:
            self.start_wave(sound)
            self.wave_cool = C.WAVE_DELAY
        elif not self.asteroids:
            self.wave_cool -= dt

    def handle_collisions(self, sound=None):
        hits = pg.sprite.groupcollide(
            self.asteroids,
            self.bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in hits.items():
            self.split_asteroid(ast, sound)

        if self.ship.invuln <= 0 and self.safe <= 0:
            for ast in self.asteroids:
                if (ast.pos - self.ship.pos).length() < (ast.r + self.ship.r):
                    self.ship_die(sound)
                    break
            for ufo in self.ufos:
                if (ufo.pos - self.ship.pos).length() < (ufo.r + self.ship.r):
                    self.ship_die(sound)
                    break
            for bullet in self.ufo_bullets:
                if (bullet.pos - self.ship.pos).length() < (bullet.r + self.ship.r):
                    self.ship_die(sound)
                    bullet.kill()
                    break

        for ufo in list(self.ufos):
            for ast in self.asteroids:
                if (ufo.pos - ast.pos).length() < (ufo.r + ast.r):
                    if sound:
                        sound.stop('ufo_small' if ufo.small else 'ufo_large')
                        sound.play('explosion_medium')
                    ufo.kill()
                    break

            for b in list(self.bullets):
                if (ufo.pos - b.pos).length() < (ufo.r + b.r):
                    score = (C.UFO_SMALL["score"] if ufo.small
                             else C.UFO_BIG["score"])
                    self.score += score
                    if sound:
                        sound.stop('ufo_small' if ufo.small else 'ufo_large')
                        sound.play('explosion_medium')

                    if not ufo.small:
                        y = uniform(0, C.HEIGHT)
                        x = C.WIDTH if ufo.pos.x < C.WIDTH / 2 else 0
                        new_ufo = UFO(Vec(x, y), False)
                        self.ufos.add(new_ufo)
                        self.all_sprites.add(new_ufo)
                        if sound:
                            sound.play('ufo_large', loops=3)

                    ufo.kill()
                    b.kill()

    def split_asteroid(self, ast: Asteroid, sound=None):
        self.score += C.AST_SIZES[ast.size]["score"]
        split = C.AST_SIZES[ast.size]["split"]
        pos = Vec(ast.pos)

        if sound:
            if ast.size == "L":
                sound.play('explosion_large')
            elif ast.size == "M":
                sound.play('explosion_medium')
            else:
                sound.play('explosion_small')

        ast.kill()
        for s in split:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * 1.2
            self.spawn_asteroid(pos, dirv * speed, s)

    def ship_die(self, sound=None):
        if sound:
            sound.play('ship_explode')
            sound.stop('thrust')

        self.lives -= 1
        self.ship.pos.xy = (C.WIDTH / 2, C.HEIGHT / 2)
        self.ship.vel.xy = (0, 0)
        self.ship.angle = -90
        self.ship.invuln = C.SAFE_SPAWN_TIME
        self.safe = C.SAFE_SPAWN_TIME
        if self.lives < 0:
            self.__init__()

    def draw(self, surf: pg.Surface, font: pg.font.Font):
        for spr in self.all_sprites:
            spr.draw(surf)

        pg.draw.line(surf, (60, 60, 60), (0, 50), (C.WIDTH, 50), width=1)
        txt = f"SCORE {self.score:06d}   LIVES {self.lives}   WAVE {self.wave}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (10, 10))
