import math
import os
import platform
import random
import turtle


# Play a sound file with operating system identification
def play_sound_file(sound_file, is_sound):
    if is_sound:
        if os.path.exists(sound_file):
            if platform.system() == "Darwin" or platform.system() == "Linux":
                os.system(f"afplay {sound_file} &")
            elif platform.system() == "Windows":
                import winsound
                winsound.PlaySound(sound_file, winsound.SND_ASYNC)
        else:
            hud.clear()
            hud.write(f"Sound file doesn't exist: {sound_file}", align="center", font=("Arial", 24, "normal"))
            screen.exitonclick()


# Move paddle up for player 1
def paddle_1_up():
    y = paddle_1.ycor()
    if y < PADDLE_SCREEN_LIMIT:
        y += PADDLE_MOVE_OFFSET
    paddle_1.sety(min(y, PADDLE_SCREEN_LIMIT))


# Move paddle down for player 1
def paddle_1_down():
    y = paddle_1.ycor()
    if y > -PADDLE_SCREEN_LIMIT:
        y -= PADDLE_MOVE_OFFSET
    paddle_1.sety(max(y, -PADDLE_SCREEN_LIMIT))


# Move paddle up for player 2
def paddle_2_up():
    y = paddle_2.ycor()
    if y < PADDLE_SCREEN_LIMIT:
        y += PADDLE_MOVE_OFFSET
    paddle_2.sety(min(y, PADDLE_SCREEN_LIMIT))


# Move paddle down for player 1
def paddle_2_down():
    y = paddle_2.ycor()
    if y > -PADDLE_SCREEN_LIMIT:
        y -= PADDLE_MOVE_OFFSET
    paddle_2.sety(max(y, -PADDLE_SCREEN_LIMIT))


# Toggle for sound play
def sound_toggle():
    global is_sound_play
    is_sound_play = not is_sound_play
    return None


# Change ball direction with a random angle
def ball_change_direction(direction):
    speed = math.hypot(ball.dx, ball.dy) * BALL_ACCELERATION_RATE
    angle = random.uniform(-math.pi / 4, math.pi / 4)
    ball.dx = direction * abs(speed * math.cos(angle))
    ball.dy = speed * math.sin(angle)


# Game main function
def game():
    global score_1, score_2, is_sound_play

    # Update ball position
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # Test top wall collision
    if ball.ycor() > 290:
        ball.sety(290)
        ball.dy *= -1
        play_sound_file(BOUNCE_SOUND_FILE, is_sound_play)

    # Test bottom wall collision
    if ball.ycor() < -290:
        ball.sety(-290)
        ball.dy *= -1
        play_sound_file(BOUNCE_SOUND_FILE, is_sound_play)

    # Player 1 score
    if ball.xcor() > 390:
        score_1 += 1
        if score_1 == 10:
            hud.clear()
            hud.write(f"Player 1 WON!!! {score_1} : {score_2}", align="center", font=("Arial", 24, "normal"))
            screen.exitonclick()
        hud.clear()
        hud.write(f"{score_1} : {score_2}", align="center", font=("Arial", 24, "normal"))
        play_sound_file(SCORE_SOUND_FILE, is_sound_play)
        ball.goto(0, 0)
        ball.dx = BALL_INITIAL_SPEED
        ball.dy = BALL_INITIAL_SPEED

    # Player 2 score
    if ball.xcor() < -390:
        score_2 += 1
        if score_2 == 10:
            hud.clear()
            hud.write(f"Player 2 WON!!! {score_1} : {score_2}", align="center", font=("Arial", 24, "normal"))
            screen.exitonclick()
        hud.clear()
        hud.write(f"{score_1} : {score_2}", align="center", font=("Arial", 24, "normal"))
        play_sound_file(SCORE_SOUND_FILE, is_sound_play)
        ball.goto(0, 0)
        ball.dx = BALL_INITIAL_SPEED
        ball.dy = BALL_INITIAL_SPEED

    # Test if ball colides with paddle 1
    if (-350 < ball.xcor() < -330) and (paddle_1.ycor() - 50 < ball.ycor() < paddle_1.ycor() + 50):
        ball.setx(-330)
        play_sound_file(BOUNCE_SOUND_FILE, is_sound_play)
        ball_change_direction(direction=1)

    # Test if ball colides with paddle 2
    if (330 < ball.xcor() < 350) and (paddle_2.ycor() - 50 < ball.ycor() < paddle_2.ycor() + 50):
        ball.setx(330)
        play_sound_file(BOUNCE_SOUND_FILE, is_sound_play)
        ball_change_direction(direction=-1)

    # Update screen with an approximate rate of 60 FPS
    screen.update()
    screen.ontimer(game, 16)  # Aproximadamente 60 FPS

### Game main source code
# Constants used in application
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_MOVE_OFFSET = 30
PADDLE_SCREEN_LIMIT = 250
BALL_INITIAL_SPEED = 5
BALL_ACCELERATION_RATE = 1.12
SCORE_SOUND_FILE = "score.wav"
BOUNCE_SOUND_FILE = "bounce.wav"

# Initialize screen elements
screen = turtle.Screen()
screen.title("Pong With Turtle Lib")
screen.bgcolor("black")
screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
screen.tracer(0)

# Initialize paddle for player 1
paddle_1 = turtle.Turtle()
paddle_1.speed(0)
paddle_1.shape("square")
paddle_1.color("white")
paddle_1.shapesize(stretch_wid=5, stretch_len=1)
paddle_1.penup()
paddle_1.goto(-350, 0)

# Initialize paddle for player 2
paddle_2 = turtle.Turtle()
paddle_2.speed(0)
paddle_2.shape("square")
paddle_2.color("white")
paddle_2.shapesize(stretch_wid=5, stretch_len=1)
paddle_2.penup()
paddle_2.goto(350, 0)

# Initialize ball
ball = turtle.Turtle()
ball.speed(0)
ball.shape("circle")
ball.color("white")
ball.penup()
ball.goto(0, 0)
ball.dx = BALL_INITIAL_SPEED
ball.dy = BALL_INITIAL_SPEED

# Variables for the score
score_1 = 0
score_2 = 0

# Variable to control sound play
is_sound_play = True

# Hud
hud = turtle.Turtle()
hud.speed(0)
hud.shape("square")
hud.color("white")
hud.penup()
hud.hideturtle()
hud.goto(0, 260)
hud.write("0 : 0", align="center", font=("Arial", 24, "normal"))

# Keyboard control functions
screen.listen()
screen.onkeypress(paddle_1_up, "w")
screen.onkeypress(paddle_1_down, "s")
screen.onkeypress(paddle_2_up, "Up")
screen.onkeypress(paddle_2_down, "Down")
screen.onkeypress(sound_toggle, "t")

# Start game and put screen in loop
game()
screen.mainloop()
