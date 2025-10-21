import pygame
from warplane.warplane_player import WarplanePlayer
from core.bullet import Bullet

class WarplaneGame:
    def __init__(self, screen, phase_manager):
        self.screen = screen
        self.phase_manager = phase_manager
        self.players = []
        self.bullets = []
        self.score = [0, 0]
        self.font = pygame.font.SysFont("Arial", 28)
        self.phase = self.phase_manager.get_phase()
        self.next_phase_timer = 0

    def setup(self):
        self.players = [
            WarplanePlayer(100, 300, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE, (255,0,0)),
            WarplanePlayer(700, 300, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN, (255,255,255)),
        ]
        self.bullets = []
        self.score = [0, 0]

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
            # Bullet collision with planes
            for i, player in enumerate(self.players):
                if bullet.owner != player and bullet.rect.colliderect(player.rect):
                    self.score[self.players.index(bullet.owner)] += 1
                    self.bullets.remove(bullet)
                    player.respawn()
                    break
            if not self.screen.get_rect().colliderect(bullet.rect):
                self.bullets.remove(bullet)

    def draw(self):
        self.screen.fill((16, 16, 32))
        for player in self.players:
            player.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        score_text = self.font.render(f"P1: {self.score[0]}  P2: {self.score[1]}  Phase {self.phase} (TAB=Next)", True, (255,255,255))
        self.screen.blit(score_text, (20, 20))
