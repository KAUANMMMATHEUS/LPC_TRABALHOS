import pygame
import random
import os
import math

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (66, 135, 245)
RED = (219, 68, 55)
GREEN = (15, 157, 88)
YELLOW = (244, 180, 0)
ORGANIZED_COLORS = [RED, RED, (255,140,0), (255,140,0), GREEN, GREEN, YELLOW, YELLOW]
COLOR_POINTS = {YELLOW: 1, GREEN: 3, (255,140,0): 5, RED: 8}

# Paddle
PADDLE_WIDTH = 60
PADDLE_HEIGHT = 15
PADDLE_SPEED = 8

# Ball
BALL_RADIUS = 10
BALL_SPEED = 10

# Brick
BRICK_ROWS = 6
BRICK_COLS = 8
BRICK_WIDTH = SCREEN_WIDTH // BRICK_COLS
BRICK_HEIGHT = 30
BRICK_PADDING = 5
TOP_OFFSET = 60

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Breakout Game with Sound")

# Clock
clock = pygame.time.Clock()

# SOUND SETUP
def load_sound(filename, fallback_beep=False):
    try:
        return pygame.mixer.Sound(filename)
    except:
        if fallback_beep:
            # Create a beep using array
            arr = pygame.sndarray.make_sound(
                (pygame.surfarray.pixels2d(pygame.Surface((1, 1))) * 0 + 127).astype('int16')
            )
            return arr
        return None

# use .wav files, or fallback to beeps
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
BOUNCE_SOUND = load_sound(os.path.join(ASSETS_PATH, "bounce.wav"), fallback_beep=True)
BRICK_SOUND = load_sound(os.path.join(ASSETS_PATH, "brick.wav"), fallback_beep=True)
GAMEOVER_SOUND = load_sound(os.path.join(ASSETS_PATH, "gameover.wav"), fallback_beep=True)
WIN_SOUND = load_sound(os.path.join(ASSETS_PATH, "win.wav"), fallback_beep=True)

def play_sound(sound):
    if sound:
        sound.play()

class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - 40
        self.speed = PADDLE_SPEED
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dir):
        if dir == "LEFT":
            self.x -= self.speed
        elif dir == "RIGHT":
            self.x += self.speed
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)

class Ball:
    def __init__(self):
        self.radius = BALL_RADIUS
        # Start ball just above the paddle, centered
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 40 - int(self.radius * 5)  # a bit higher above the paddle
        self.dx = 0
        self.dy = BALL_SPEED  # move downwards towards the paddle
        self.prev_x = self.x
        self.prev_y = self.y

    def move(self):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x += self.dx
        self.y += self.dy

        # Wall collision
        if self.x <= self.radius:
            self.x = self.radius
            self.dx *= -1
            play_sound(BOUNCE_SOUND)
        elif self.x >= SCREEN_WIDTH - self.radius:
            self.x = SCREEN_WIDTH - self.radius
            self.dx *= -1
            play_sound(BOUNCE_SOUND)
        if self.y <= self.radius:
            self.y = self.radius
            self.dy *= -1
            play_sound(BOUNCE_SOUND)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (self.x, self.y), self.radius)

    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

class Brick:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH - BRICK_PADDING, BRICK_HEIGHT - BRICK_PADDING)
        self.color = color
        self.alive = True

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, WHITE, self.rect, 2)

def create_bricks():
    bricks = []
    for row in range(8):
        color = ORGANIZED_COLORS[row]
        for col in range(BRICK_COLS):
            x = col * BRICK_WIDTH + BRICK_PADDING // 2
            y = row * BRICK_HEIGHT + TOP_OFFSET
            bricks.append(Brick(x, y, color))
    return bricks

def main():
    running = True
    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks()
    score = 0
    lives = 0 
    font = pygame.font.SysFont("Arial", 28)
    game_over = False
    win = False

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move("LEFT")
        if keys[pygame.K_RIGHT]:
            paddle.move("RIGHT")

        if not game_over:
            ball.move()

            # Ball and paddle collision
            if ball.rect().colliderect(paddle.rect):
                # Calculate where the ball hit the paddle
                hit_pos = (ball.x - paddle.x) / paddle.width  # 0 (left) to 1 (right)
                # Angle varies from 150° (left) to 30° (right)
                min_angle = 150
                max_angle = 30
                angle_deg = min_angle + (max_angle - min_angle) * hit_pos
                angle_rad = math.radians(angle_deg)
                speed = math.hypot(ball.dx, ball.dy)
                ball.dx = speed * math.cos(angle_rad)
                ball.dy = -abs(speed * math.sin(angle_rad))
                ball.y = paddle.rect.y - ball.radius
                play_sound(BOUNCE_SOUND)

            # Ball and brick collision
            for brick in bricks:
                if brick.alive and ball.rect().colliderect(brick.rect):
                    brick.alive = False
                    # Score by color
                    brick_points = COLOR_POINTS.get(brick.color, 1)
                    score += brick_points
                    play_sound(BRICK_SOUND)
                    # Increase ball speed every 20 bricks destroyed
                    destroyed_bricks = sum(not b.alive for b in bricks)
                    if destroyed_bricks % 20 == 0 and destroyed_bricks > 0:
                        ball.dx *= 1.1
                        ball.dy *= 1.1
                    # Improved collision response using previous ball position
                    prev_rect = pygame.Rect(ball.prev_x - ball.radius, ball.prev_y - ball.radius, ball.radius*2, ball.radius*2)
                    brick_rect = brick.rect
                    if prev_rect.right <= brick_rect.left:
                        ball.dx = -abs(ball.dx)  # hit left, go left
                    elif prev_rect.left >= brick_rect.right:
                        ball.dx = abs(ball.dx)   # hit right, go right
                    elif prev_rect.bottom <= brick_rect.top:
                        ball.dy = -abs(ball.dy)  # hit top, go up
                    elif prev_rect.top >= brick_rect.bottom:
                        ball.dy = abs(ball.dy)   # hit bottom, go down
                    else:
                        ball.dy *= -1  # fallback: invert vertical
                    break

            # Ball falls below screen
            if ball.y > SCREEN_HEIGHT:
                if lives < 3:
                    lives += 1
                    ball = Ball()
                    paddle = Paddle()
                elif lives == 3:
                    game_over = True
                    win = False
                    play_sound(GAMEOVER_SOUND)

        # Draw all game objects
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)

        # Draw score and life meter
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        life_text = font.render(f"Life Meter: {lives}/3", True, WHITE)
        screen.blit(life_text, (SCREEN_WIDTH - 180, 10))

        # Win or lose
        if all(not brick.alive for brick in bricks):
            win_text = font.render("You Win! Press R to Restart", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2))
            if not game_over:
                play_sound(WIN_SOUND)
            game_over = True
            win = True

        if game_over and not win and lives >= 3:
            lose_text = font.render("Game Over! Press R to Restart", True, RED)
            screen.blit(lose_text, (SCREEN_WIDTH//2 - lose_text.get_width()//2, SCREEN_HEIGHT//2))

        if game_over:
            if keys[pygame.K_r]:
                ball = Ball()
                bricks = create_bricks()
                score = 0
                lives = 0  # Reset lives when restarting
                game_over = False
                win = False

        pygame.display.flip()
        clock.tick(FPS)

        # Win or lose
        if all(not brick.alive for brick in bricks):
            win_text = font.render("You Win! Press R to Restart", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2))
            if not game_over:
                play_sound(WIN_SOUND)
            game_over = True
            win = True

        if game_over:
            if keys[pygame.K_r]:
                ball = Ball()
                bricks = create_bricks()
                score = 0
                game_over = False
                win = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
