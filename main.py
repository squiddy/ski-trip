import pyxel
import random
import enum

random.seed(0)

FPS = 60

pyxel.init(160, 120, fps=FPS)
pyxel.load("main.pyxres")


@enum.unique
class Direction(enum.Enum):
    DOWN = 0
    LEFT = -1
    RIGHT = +1


@enum.unique
class PlayerState(enum.Enum):
    MOVING = 0
    JUMPING = 1


COLOR_TRANSPARENT = 11


@enum.unique
class Sprite(enum.Enum):
    PLAYER_DOWN = 0, 0, 8, 8
    PLAYER_LEFT = 8, 0, 8, 8
    PLAYER_RIGHT = 0, 8, 8, 8
    PLAYER_JUMPING = 8, 8, 8, 8
    TREE_GREEN = 0, 16, 16, 16
    TREE_HALF = 14, 16, 16, 16
    TREE_WHITE = 32, 16, 16, 16
    TREE_EMPTY = 48, 16, 16, 16
    ROCK = 0, 48, 8, 8
    SNOWMAN = 0, 64, 16, 16


last_frame = pyxel.frame_count
x, y, dir, state = 80, 10, Direction.DOWN, PlayerState.MOVING
player_frames_remaining = 0

trees: list[tuple[int, int, Sprite]] = []
for _ in range(100):
    sprite = random.choice([Sprite.TREE_GREEN, Sprite.TREE_HALF, Sprite.TREE_WHITE])
    trees.append(
        (
            random.randint(0, pyxel.width - 16),
            random.randint(0, pyxel.height * 10),
            sprite,
        )
    )

rocks: list[tuple[int, int, Sprite]] = []
for _ in range(30):
    rocks.append(
        (
            random.randint(0, pyxel.width - 16),
            random.randint(0, pyxel.height * 10),
            Sprite.ROCK,
        )
    )


def update():
    global dir, x, y, last_frame, state, player_frames_remaining

    frame_diff, last_frame = pyxel.frame_count - last_frame, pyxel.frame_count
    player_frames_remaining -= frame_diff

    if pyxel.btnp(pyxel.KEY_SPACE):
        if state == PlayerState.MOVING:
            state = PlayerState.JUMPING
            player_frames_remaining = 50

    if player_frames_remaining <= 0 and state == PlayerState.JUMPING:
        state = PlayerState.MOVING

    if state == PlayerState.MOVING:
        new_dir = None
        if pyxel.btnp(pyxel.KEY_LEFT):
            new_dir = max(Direction.LEFT.value, dir.value - 1)
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            new_dir = min(Direction.RIGHT.value, dir.value + 1)
        if new_dir:
            dir = Direction(new_dir)

    if dir == Direction.LEFT:
        x = max(x - 1, 0)
    elif dir == Direction.RIGHT:
        x = min(x + 1, pyxel.width - 8)

    pyxel.camera(0, y)
    y += 1
    if y > pyxel.height * 10:
        y = 0


def draw():
    pyxel.cls(1)

    if state == PlayerState.JUMPING:
        sprite = Sprite.PLAYER_JUMPING
    else:
        sprite = {
            Direction.DOWN: Sprite.PLAYER_DOWN,
            Direction.LEFT: Sprite.PLAYER_LEFT,
            Direction.RIGHT: Sprite.PLAYER_RIGHT,
        }[dir]
    pyxel.blt(x, y + 10, 0, *sprite.value, COLOR_TRANSPARENT)

    for tx, ty, sprite in trees:
        pyxel.blt(tx, ty, 0, *sprite.value, COLOR_TRANSPARENT)
    for rx, ry, sprite in rocks:
        pyxel.blt(rx, ry, 0, *sprite.value, COLOR_TRANSPARENT)

    pyxel.blt(10, y, 0, *Sprite.SNOWMAN.value, COLOR_TRANSPARENT)
    pyxel.camera()
    pyxel.text(10, 110, f"{state}", 7)


pyxel.run(update, draw)
