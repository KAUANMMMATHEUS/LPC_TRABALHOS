import pygame
import math

# Window and frame rate settings
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 1024
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (66, 135, 245)

# Ship (triangle) properties
TRI_WIDTH = 60
TRI_HEIGHT = 40
TRI_SPEED = 8

# BRAKE flag: 0 = always move forward, 1 = move only when W is pressed
BRAKE = 0

# Initialize pygame and window
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Triangle Movement")
clock = pygame.time.Clock()

# Ship class represents the main blue triangle
class Ship:
	def __init__(self):
		# Size and position
		self.width = TRI_WIDTH
		self.height = TRI_HEIGHT
		self.x = (SCREEN_WIDTH - self.width) // 2
		self.y = (SCREEN_HEIGHT - self.height) // 2
		self.speed = TRI_SPEED
		self.angle = 0  # Angle in degrees

	# Move the ship forward in the direction it is pointing
	def move_forward(self):
		rad = math.radians(self.angle)
		dx = self.speed * math.sin(rad)
		dy = -self.speed * math.cos(rad)
		self.x += dx
		self.y += dy
		# Keep the ship within the window boundaries
		self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
		self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

	# Rotate the ship by a given angle (in degrees)
	def rotate(self, delta):
		self.angle = (self.angle + delta) % 360

	# Draw the ship and the small red triangle at the tip
	def draw(self, surface):
		# Center of the triangle
		cx = self.x + self.width // 2
		cy = self.y + self.height // 2
		# Triangle points before rotation
		top = (self.x + self.width // 2, self.y)
		left = (self.x, self.y + self.height)
		right = (self.x + self.width, self.y + self.height)
		points = [left, right, top]
		# Function to rotate a point around the center
		def rotate_point(px, py):
			rad = math.radians(self.angle)
			dx = px - cx
			dy = py - cy
			qx = cx + dx * math.cos(rad) - dy * math.sin(rad)
			qy = cy + dx * math.sin(rad) + dy * math.cos(rad)
			return (int(qx), int(qy))
		# Apply rotation to all points
		rotated_points = [rotate_point(px, py) for (px, py) in points]
		# Draw the main blue triangle
		pygame.draw.polygon(surface, BLUE, rotated_points)
		# Draw the small red triangle at the tip
		tip = rotated_points[2]
		base_left = rotated_points[0]
		base_right = rotated_points[1]
		vx = base_right[0] - base_left[0]
		vy = base_right[1] - base_left[1]
		base_len = math.hypot(vx, vy)
		mini_height = 18
		mini_base = 16
		if base_len == 0:
			mini_left = mini_right = tip
		else:
			# Perpendicular unit vector to the base (points "backwards" from the tip)
			perp_vx = -(vy / base_len)
			perp_vy = vx / base_len
			# Center of the small triangle's base
			mini_base_cx = tip[0] + perp_vx * mini_height
			mini_base_cy = tip[1] + perp_vy * mini_height
			# Unit vector along the base
			unit_vx = vx / base_len
			unit_vy = vy / base_len
			# Left and right points of the small triangle's base
			mini_left = (
				int(mini_base_cx - unit_vx * (mini_base / 2)),
				int(mini_base_cy - unit_vy * (mini_base / 2))
			)
			mini_right = (
				int(mini_base_cx + unit_vx * (mini_base / 2)),
				int(mini_base_cy + unit_vy * (mini_base / 2))
			)
		mini_points = [mini_left, mini_right, tip]
		pygame.draw.polygon(surface, (255, 0, 0), mini_points)

# Main game loop
def main():
	running = True
	ship = Ship()
	global BRAKE
	w_pressed_last = False
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		keys = pygame.key.get_pressed()
		# Toggle BRAKE on W key press (edge detection)
		if keys[pygame.K_w]:
			if not w_pressed_last:
				BRAKE = 1 - BRAKE
			w_pressed_last = True
		else:
			w_pressed_last = False
		if keys[pygame.K_a]:
			ship.rotate(-5)
		if keys[pygame.K_d]:
			ship.rotate(5)
		if BRAKE == 0:
			ship.move_forward()
		elif BRAKE == 1:
			pass  # Only moves if toggled to 0
		screen.fill(BLACK)
		ship.draw(screen)
		pygame.display.flip()
		clock.tick(FPS)
	pygame.quit()

if __name__ == "__main__":
	main()