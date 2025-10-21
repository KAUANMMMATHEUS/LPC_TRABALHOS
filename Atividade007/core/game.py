import pygame
from core.phase_manager import PhaseManager
from tank.tank_game import TankGame
from warplane.warplane_game import WarplaneGame

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Combat (Atari 1977) Remake")
        self.clock = pygame.time.Clock()
        self.phase_manager = PhaseManager()
        self.current_mode = None
        self.running = True

    def run(self):
        while self.running:
            phase = self.phase_manager.get_phase()
            if phase < 18:
                self.current_mode = TankGame(self.screen, self.phase_manager)
            else:
                self.current_mode = WarplaneGame(self.screen, self.phase_manager)
            self.current_mode.setup()
            while not self.phase_manager.next_phase_requested:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return
                    self.current_mode.handle_event(event)
                self.current_mode.update()
                self.current_mode.draw()
                pygame.display.flip()
                self.clock.tick(60)
            self.phase_manager.advance_phase()
