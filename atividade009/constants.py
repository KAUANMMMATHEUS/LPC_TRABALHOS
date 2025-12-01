# settings.py
from pathlib import Path

WIDTH = 800
HEIGHT = 600
FPS = 60

PLAYER_SPEED = 250
BULLET_SPEED = 500
PISTOL_COOLDOWN = 250

WORLD_WIDTH = 3200
WORLD_HEIGHT = 2400

PLAYER_BASE_SIZE = (18, 20)
ZOMBIE_BASE_SIZE = (18, 20)
BULLET_BASE_SIZE = (24, 24)
SPRITE_SCALE = 4

PLAYER_SIZE = (PLAYER_BASE_SIZE[0] * SPRITE_SCALE, PLAYER_BASE_SIZE[1] * SPRITE_SCALE)
ZOMBIE_SIZE = (ZOMBIE_BASE_SIZE[0] * SPRITE_SCALE, ZOMBIE_BASE_SIZE[1] * SPRITE_SCALE)
BULLET_SIZE = (BULLET_BASE_SIZE[0] * SPRITE_SCALE, BULLET_BASE_SIZE[1] * SPRITE_SCALE)

ASSETS_DIR = Path("atividade009/assets")

ZOMBIE_SPEED = 30
SPAWN_INTERVAL = 3000

PLAYER_MAX_HP = 30
PLAYER_ARMOR_MAX_HP = 50
ZOMBIE_MAX_HP = 3

BULLET_HIT_RADIUS = 30
ZOMBIE_TOUCH_RADIUS = 35

EXPLOSION_FRAMES = ["explosion_0.png", "explosion_1.png", "explosion_2.png"]
EXPLOSION_SIZE = (96 * 3, 96 * 3)
EXPLOSION_DURATION = 450
EXPLOSION_RADIUS = 100 * 3

START_LORE = (
    "Depois do surto em Vila Morta, você ficou preso no último quarteirão ainda de pé. "
    "A munição é pouca, a noite é longa e ninguém virá ajudar. Sobreviver virou estatística."
)
GAME_OVER_LORE = (
    "Seu corpo cai entre as carcaças dos mortos-vivos. "
    "Com o último sobrevivente abatido, Vila Morta desaparece do mapa como mais um boato abafado pelo governo."
)
VICTORY_LORE = (
    "Você sobreviveu à noite em Vila Morta. "
    "Os rádios silenciam, mas os boatos sobre um enxame ainda maior a caminho deixam claro: "
    "isso não foi o fim, foi só o ensaio."
)

# --- Gamepad / controller defaults (added for joystick support) ---
# deadzone for analog sticks
GAMEPAD_AXIS_DEADZONE = 0.2
# Common face button indices (covers Xbox and PlayStation common layouts)
GP_BUTTON_SHOOT_SET = {0, 1, 2, 3}
# Common shoulder / secondary buttons for alternate actions
GP_BUTTON_MEDKIT_SET = {4, 5, 6, 7}
# Common start/options buttons for menu/shop
GP_BUTTON_SHOP_SET = {8, 9, 10, 11}
