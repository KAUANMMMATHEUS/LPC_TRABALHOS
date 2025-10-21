import pygame
from tank.tank_player import TankPlayer
from core.bullet import Bullet

class TankGame:
    def __init__(self, screen, phase_manager):
        self.screen = screen
        self.phase_manager = phase_manager
        self.phase = self.phase_manager.get_phase()
        self.players = []
        self.bullets = []
        self.score = [0, 0]
        self.font = pygame.font.SysFont("Arial", 28)
        self.next_phase_timer = 0
        self.obstacles = []

    def setup(self):
        # Player 1: left, facing right (angle=90)
        p1_x = 50
        p1_y = (600 - 48) // 2  # Vertically centered for 48x48 tank sprite
        # Player 2: right, facing left (angle=270)
        p2_x = 800 - 50 - 48  # 48 is tank width
        p2_y = (600 - 48) // 2

        self.players = [
            TankPlayer(
                p1_x, p1_y,
                pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE,
                (0,255,0),
                angle = 90
            ),
            TankPlayer(
                p2_x, p2_y,
                pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN,
                (0,0,255),
                angle = 270
            ),
        ]

        self.bullets = []
        self.score = [0, 0]
        self.obstacles = self.generate_obstacles(self.phase)

    def generate_obstacles(self, phase):
        obstacles = []
        # Example: Add obstacles depending on phase
        if phase >= 2:
            obstacles.append(pygame.Rect(375, 250, 50, 100))
        if phase >= 3:
            obstacles.append(pygame.Rect(200, 150, 30, 300))
            obstacles.append(pygame.Rect(570, 150, 30, 300))
        if phase >= 5:
            obstacles.append(pygame.Rect(375, 100, 50, 50))
            obstacles.append(pygame.Rect(375, 450, 50, 50))
            obstacles.append(pygame.Rect(250, 300, 50, 50))
            obstacles.append(pygame.Rect(500, 300, 50, 50))
        return obstacles

    def handle_event(self, event):
        for player in self.players:
            player.handle_event(event, self.bullets)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.phase_manager.request_next_phase()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self):
        for player in self.players:
            player.update()
        for bullet in self.bullets[:]:
            bullet.update()
            # Bullet collision with tanks
            for i, player in enumerate(self.players):
                if bullet.owner != player and bullet.rect.colliderect(player.rect):
                    self.score[self.players.index(bullet.owner)] += 1
                    self.bullets.remove(bullet)
                    bullet.owner.bullet = None
                    player.respawn()
                    break
            # Bullet collision with obstacles
            for obstacle in self.obstacles:
                if bullet.rect.colliderect(obstacle):
                    bullet.owner.bullet = None
                    bullet.alive = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
            if not self.screen.get_rect().colliderect(bullet.rect):
                bullet.owner.bullet = None
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
        # Tank collision with obstacles
        for player in self.players:
            for obstacle in self.obstacles:
                if player.rect.colliderect(obstacle):
                    player.x -= player.speed * pygame.math.Vector2(1,0).rotate(-player.angle).x
                    player.y -= player.speed * pygame.math.Vector2(1,0).rotate(-player.angle).y
                    player.rect.topleft = (player.x, player.y)

    def draw(self):
        self.screen.fill((0, 0, 0))
        # Draw obstacles first
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, (128, 128, 128), obstacle)
        for player in self.players:
            player.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        score_text = self.font.render(
            f"P1: {self.score[0]}  P2: {self.score[1]}  Phase {self.phase} (TAB=Next)", True, (255,255,255))
        self.screen.blit(score_text, (20, 20))
