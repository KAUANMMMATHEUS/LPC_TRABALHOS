# game.py
import sys
import random
import pygame

from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    WORLD_WIDTH,
    WORLD_HEIGHT,
    SPAWN_INTERVAL,
    BULLET_HIT_RADIUS,
    EXPLOSION_RADIUS,
    ZOMBIE_TOUCH_RADIUS,
    START_LORE,
    GAME_OVER_LORE,
    VICTORY_LORE,
    PLAYER_ARMOR_MAX_HP,
    ASSETS_DIR,
    PLAYER_MAX_HP,
    GAMEPAD_AXIS_DEADZONE,
    GP_BUTTON_SHOOT_SET,
    GP_BUTTON_MEDKIT_SET,
    GP_BUTTON_SHOP_SET,
)
from utils import load_image, load_sound, draw_multiline_center, draw_health_bar
from entities import Player, Enemy, Item, Grenade, Explosion


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.snd_gun = load_sound("gunshot.wav", 0.8)
        self.snd_power = load_sound("powerup.wav", 0.7)
        self.snd_hit = [
            load_sound("player_hit_1.wav"),
            load_sound("player_hit_2.wav"),
            load_sound("player_hit_3.wav"),
        ]
        self.snd_zwalk = load_sound("zombie_walk.wav", 0.5)
        self.snd_zhit = load_sound("zombie_hit.wav", 0.6)

        self.background = self.load_background()
        self.fog = self.create_fog()

        # joystick support
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            try:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print("Joystick connected:", self.joystick.get_name())
            except Exception:
                self.joystick = None

        start = pygame.Vector2(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.player = Player(start)
        self.bullets = []
        self.enemies = self.spawn_enemies()
        self.items = []
        self.explosions = []
        self.active_grenades = []

        now = pygame.time.get_ticks()
        self.last_spawn = now
        self.start_time = None
        self.end_time = None

        self.zombies_killed = 0
        self.next_boss_kill = 25

        self.state = "start"

    def load_background(self):
        bg = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
        p = ASSETS_DIR / "background.png"
        if p.exists():
            img = pygame.image.load(p).convert()
            img = pygame.transform.smoothscale(img, (WORLD_WIDTH, WORLD_HEIGHT))
            bg.blit(img, (0, 0))
        else:
            bg.fill((30, 30, 30))
        return bg

    def spawn_enemies(self):
        center = pygame.Vector2(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        return [
            Enemy(center + pygame.Vector2(200, 0)),
            Enemy(center + pygame.Vector2(-200, -100)),
            Enemy(center + pygame.Vector2(0, 200)),
        ]

    def create_fog(self):
        fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        c = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        maxd = pygame.Vector2(WIDTH, HEIGHT).length() / 2
        inner = maxd * 0.25
        outer = maxd * 0.9
        for y in range(HEIGHT):
            for x in range(WIDTH):
                d = pygame.Vector2(x, y).distance_to(c)
                if d <= inner:
                    a = 0
                elif d >= outer:
                    a = 255
                else:
                    t = (d - inner) / (outer - inner)
                    a = int(t * 255)
                fog.set_at((x, y), (0, 0, 0, a))
        return fog

    def spawn_zombie(self):
        side = random.choice(["t", "b", "l", "r"])
        if side == "t":
            pos = pygame.Vector2(random.randint(0, WORLD_WIDTH), 0)
        elif side == "b":
            pos = pygame.Vector2(random.randint(0, WORLD_WIDTH), WORLD_HEIGHT)
        elif side == "l":
            pos = pygame.Vector2(0, random.randint(0, WORLD_HEIGHT))
        else:
            pos = pygame.Vector2(WORLD_WIDTH, random.randint(0, WORLD_HEIGHT))
        self.enemies.append(Enemy(pos))

    def spawn_boss_zombie(self):
        side = random.choice(["t", "b", "l", "r"])
        if side == "t":
            pos = pygame.Vector2(random.randint(0, WORLD_WIDTH), 0)
        elif side == "b":
            pos = pygame.Vector2(random.randint(0, WORLD_WIDTH), WORLD_HEIGHT)
        elif side == "l":
            pos = pygame.Vector2(0, random.randint(0, WORLD_HEIGHT))
        else:
            pos = pygame.Vector2(WORLD_WIDTH, random.randint(0, WORLD_HEIGHT))
        self.enemies.append(Enemy(pos, is_boss=True))

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.events()
            if self.state == "playing":
                self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False

                if self.state == "start":
                    if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                        now = pygame.time.get_ticks()
                        self.start_time = now
                        self.last_spawn = now
                        self.state = "playing"

                elif self.state == "playing":
                    if e.key == pygame.K_SPACE:
                        self.shoot()
                    if e.key == pygame.K_g:
                        self.throw_grenade()

                elif self.state in ("game_over", "victory"):
                    if e.key in (pygame.K_RETURN):
                        self.__init__()
            # joystick button events
            if e.type == pygame.JOYBUTTONDOWN:
                btn = e.button
                if self.state == "start":
                    # accept any face/start button to begin
                    if btn in GP_BUTTON_SHOOT_SET or btn in GP_BUTTON_SHOP_SET:
                        now = pygame.time.get_ticks()
                        self.start_time = now
                        self.last_spawn = now
                        self.state = "playing"
                elif self.state == "playing":
                    # face buttons -> shoot
                    if btn in GP_BUTTON_SHOOT_SET:
                        self.shoot()
                    # shoulder / secondary -> grenade
                    if btn in GP_BUTTON_MEDKIT_SET:
                        self.throw_grenade()
                elif self.state in ("game_over", "victory"):
                    if btn in GP_BUTTON_SHOOT_SET:
                        self.__init__()
            # joystick hat (d-pad) could be used for menu navigation if needed
            if e.type == pygame.JOYHATMOTION:
                # e.value is tuple (x, y)
                hat_x, hat_y = e.value
                # start screen: pressing up/down does nothing special here
                pass

    def shoot(self):
        d = self.player.direction_name
        v = pygame.Vector2(0, 0)
        if d == "up":
            v.y = -1
        if d == "down":
            v.y = 1
        if d == "left":
            v.x = -1
        if d == "right":
            v.x = 1
        if v.length_squared() == 0:
            return
        t = pygame.time.get_ticks()
        before = self.player.ammo
        self.player.shoot(v, self.bullets, t)
        if self.player.ammo < before and self.snd_gun:
            self.snd_gun.play()

    def throw_grenade(self):
        if self.player.grenades <= 0:
            return
        self.player.grenades -= 1
        pos = self.player.world_pos.copy()
        self.active_grenades.append(Grenade(pos))

    def maybe_drop_item(self, enemy_pos):
        if random.random() < 0.30:
            return
        if len(self.items) >= 20:
            return
        possible = ["medkit", "bullet_pack", "armor", "grenade"]
        weights = [2, 5, 2, 1]
        if self.zombies_killed >= 10:
            possible.append("double_bullets")
            weights.append(0.1)
        t = random.choices(possible, weights=weights, k=1)[0]
        self.items.append(Item(enemy_pos.copy(), t))

    def update(self, dt):
        keys = pygame.key.get_pressed()
        # poll joystick axes for left stick movement if available
        gamepad_dir = None
        if self.joystick is not None:
            try:
                ax0 = self.joystick.get_axis(0)
                ax1 = self.joystick.get_axis(1)
                # apply deadzone
                if abs(ax0) < GAMEPAD_AXIS_DEADZONE:
                    ax0 = 0.0
                if abs(ax1) < GAMEPAD_AXIS_DEADZONE:
                    ax1 = 0.0
                gamepad_dir = pygame.Vector2(ax0, ax1)
            except Exception:
                gamepad_dir = None

        self.player.update(dt, keys, gamepad_dir)

        for e in self.enemies:
            e.update(dt, self.player.world_pos)

        for b in self.bullets:
            b.update(dt)

        for b in self.bullets:
            if not b.alive:
                continue
            for z in self.enemies:
                if z.hp <= 0:
                    continue
                if (z.world_pos - b.world_pos).length_squared() <= BULLET_HIT_RADIUS**2:
                    z.hp -= self.player.damage_multiplier
                    b.alive = False
                    if self.snd_zhit:
                        self.snd_zhit.play()
                    break

        for z in self.enemies:
            if z.hp <= 0:
                self.zombies_killed += 1
                self.maybe_drop_item(z.world_pos)

                if self.zombies_killed >= self.next_boss_kill:
                    self.spawn_boss_zombie()
                    self.next_boss_kill += 25

        self.enemies = [z for z in self.enemies if z.hp > 0]
        self.bullets = [b for b in self.bullets if not b.is_expired() and b.alive]

        for ex in self.explosions[:]:
            if ex.update():
                for z in self.enemies:
                    if (z.world_pos - ex.world_pos).length() <= EXPLOSION_RADIUS:
                        z.hp -= 3
                self.explosions.remove(ex)

        for g in self.active_grenades[:]:
            if g.update():
                self.explosions.append(Explosion(g.world_pos.copy()))
                self.active_grenades.remove(g)

        for it in self.items[:]:
            if (it.world_pos - self.player.world_pos).length_squared() <= 40**2:
                if it.type == "medkit":
                    self.player.hp = min(self.player.hp + 5, PLAYER_MAX_HP)

                elif it.type == "bullet_pack":
                    self.player.ammo = min(
                        self.player.ammo + 15, self.player.max_ammo
                    )

                elif it.type == "double_bullets":
                    self.player.damage_multiplier = 2

                elif it.type == "armor":
                    new_max = min(self.player.max_hp + 2, PLAYER_ARMOR_MAX_HP)
                    self.player.max_hp = new_max
                    self.player.hp += 2

                elif it.type == "grenade":
                    self.player.grenades += 1

                if self.snd_power:
                    self.snd_power.play()
                self.items.remove(it)

        for z in self.enemies:
            if (z.world_pos - self.player.world_pos).length_squared() <= ZOMBIE_TOUCH_RADIUS**2:
                now = pygame.time.get_ticks()
                if now - self.player.last_hit_time >= self.player.hit_cooldown:
                    self.player.hp -= 5
                    self.player.last_hit_time = now

                    hit_sounds = [s for s in self.snd_hit if s is not None]
                    if hit_sounds:
                        random.choice(hit_sounds).play()

                    if self.player.hp <= 0 and self.state == "playing":
                        self.state = "game_over"
                        self.end_time = now
                break

        now = pygame.time.get_ticks()
        if now - self.last_spawn >= SPAWN_INTERVAL:
            self.spawn_zombie()
            self.last_spawn = now

        if self.start_time is None:
            elapsed_ms = 0
        else:
            elapsed_ms = now - self.start_time

        if self.state == "playing":
            if elapsed_ms >= 5 * 60 * 1000 or self.zombies_killed >= 100:
                self.state = "victory"
                self.end_time = now

    def cam(self):
        return self.player.world_pos - pygame.Vector2(WIDTH // 2, HEIGHT // 2)

    def draw(self):
        if self.state == "start":
            self.draw_start_screen()
        elif self.state == "playing":
            self.draw_game()
            self.debug()
        elif self.state in ("game_over", "victory"):
            self.draw_end_screen()
        pygame.display.flip()

    def draw_game(self):
        cam = self.cam()
        self.screen.blit(self.background, -cam)

        for it in self.items:
            it.draw(self.screen, cam)

        for g in self.active_grenades:
            g.draw(self.screen, cam)

        for z in self.enemies:
            z.draw(self.screen, cam)

        for b in self.bullets:
            pos = b.world_pos - cam
            b.rect.center = (int(pos.x), int(pos.y))
            self.screen.blit(b.image, b.rect)

        for ex in self.explosions:
            ex.draw(self.screen, cam)

        self.player.rect.center = (
            int(self.player.screen_pos.x),
            int(self.player.screen_pos.y),
        )
        self.screen.blit(self.player.image, self.player.rect)

        draw_health_bar(
            self.screen,
            (int(self.player.screen_pos.x), int(self.player.screen_pos.y) - 50),
            80,
            8,
            self.player.hp,
            self.player.max_hp,
        )

        self.screen.blit(self.fog, (0, 0))

    def draw_start_screen(self):
        self.screen.fill((5, 5, 8))

        title_font = pygame.font.SysFont("consolas", 42, bold=True)
        text_font = pygame.font.SysFont("consolas", 22)
        small_font = pygame.font.SysFont("consolas", 18)

        title = "Vila Morta: Último Quarteirão"
        t_surf = title_font.render(title, True, (0, 220, 120))
        t_rect = t_surf.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(t_surf, t_rect)

        obj = "Objetivo: sobreviva 5 minutos OU mate 100 zumbis."
        o_surf = text_font.render(obj, True, (230, 230, 230))
        o_rect = o_surf.get_rect(center=(WIDTH // 2, 140))
        self.screen.blit(o_surf, o_rect)

        draw_multiline_center(
            self.screen,
            START_LORE,
            small_font,
            (200, 200, 200),
            WIDTH // 2,
            200,
            max_width=WIDTH - 100,
            line_height=24,
        )

        hint1 = "WASD: mover   |   ESPAÇO: atirar   |   G: granada"
        h1_surf = small_font.render(hint1, True, (180, 180, 180))
        h1_rect = h1_surf.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        self.screen.blit(h1_surf, h1_rect)

        hint2 = "Pressione ESPAÇO ou ENTER para começar"
        h2_surf = small_font.render(hint2, True, (0, 220, 120))
        h2_rect = h2_surf.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.screen.blit(h2_surf, h2_rect)

    def draw_end_screen(self):
        self.screen.fill((0, 0, 0))

        big_font = pygame.font.SysFont("consolas", 40, bold=True)
        text_font = pygame.font.SysFont("consolas", 22)
        small_font = pygame.font.SysFont("consolas", 18)

        victory = (self.state == "victory")
        title = "VITÓRIA" if victory else "GAME OVER"
        color = (0, 230, 120) if victory else (220, 40, 40)

        t_surf = big_font.render(title, True, color)
        t_rect = t_surf.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(t_surf, t_rect)

        if self.start_time is not None:
            base_time = self.end_time if self.end_time is not None else pygame.time.get_ticks()
            elapsed_sec = (base_time - self.start_time) // 1000
        else:
            elapsed_sec = 0

        stats_line = f"Tempo sobrevivido: {elapsed_sec}s   |   Zumbis mortos: {self.zombies_killed}"
        s_surf = text_font.render(stats_line, True, (230, 230, 230))
        s_rect = s_surf.get_rect(center=(WIDTH // 2, 140))
        self.screen.blit(s_surf, s_rect)

        lore_text = VICTORY_LORE if victory else GAME_OVER_LORE
        draw_multiline_center(
            self.screen,
            lore_text,
            small_font,
            (200, 200, 200),
            WIDTH // 2,
            200,
            max_width=WIDTH - 100,
            line_height=24,
        )

        hint = "Pressione ESPAÇO ou ENTER para jogar novamente  |  ESC para sair"
        h_surf = small_font.render(hint, True, (180, 180, 180))
        h_rect = h_surf.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.screen.blit(h_surf, h_rect)

    def debug(self):
        f = pygame.font.SysFont("consolas", 18)

        now = pygame.time.get_ticks()
        if self.start_time is None:
            elapsed_sec = 0
        else:
            elapsed_sec = (now - self.start_time) // 1000
        remaining_sec = max(0, 5 * 60 - elapsed_sec)

        t_obj = "Objetivo: sobreviva 5 min ou mate 100 zumbis"
        s_obj = f.render(t_obj, True, (255, 255, 255))
        self.screen.blit(s_obj, (10, 10))

        t_prog = f"Tempo: {elapsed_sec:3d}s  Restante: {remaining_sec:3d}s  Kills: {self.zombies_killed}/100"
        s_prog = f.render(t_prog, True, (255, 255, 255))
        self.screen.blit(s_prog, (10, 30))

        t_status = (
            f"HP {self.player.hp}/{self.player.max_hp}  "
            f"Ammo {self.player.ammo}/{self.player.max_ammo}  "
            f"G {self.player.grenades}  "
            f"Z {len(self.enemies)}  "
            f"I {len(self.items)}"
        )
        s_status = f.render(t_status, True, (255, 255, 255))
        self.screen.blit(s_status, (10, 50))


if __name__ == "__main__":
    Game().run()
