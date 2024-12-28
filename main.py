import math
import pyxel
import random
import enum
from dataclasses import dataclass

random.seed(0)

FPS = 60
COLOR_TRANSPARENT = 11
DEBUG = 1

pyxel.init(320, 240, fps=FPS)
pyxel.load("main.pyxres")


def blt_topleft(
    x: int,
    y: int,
    img: int | pyxel.Image,
    u: float,
    v: float,
    w: float,
    h: float,
    colkey: int | None = None,
    *,
    rotate: float | None = None,
    scale: float | None = None,
):
    scale = scale or 1
    pyxel.blt(
        x + w / scale,
        y + h / scale,
        img,
        u,
        v,
        w,
        h,
        colkey,
        rotate=rotate,
        scale=scale,
    )


@enum.unique
class Direction(enum.Enum):
    LEFT = -1
    DOWN = 0
    RIGHT = +1


@enum.unique
class PlayerState(enum.Enum):
    MOVING = 0
    JUMPING = 1


@dataclass
class Tooltip:
    visible = False

    def update(self):
        if pyxel.btnp(pyxel.KEY_T):
            self.visible = not self.visible

    def draw(self):
        if not self.visible:
            return

        pyxel.rect(0, 0, 30, 6, 0)
        pyxel.text(0, 0, f"{pyxel.mouse_x} {pyxel.mouse_y}", 7)
        pyxel.circ(pyxel.mouse_x, pyxel.mouse_y, 2, 7)


class TitleScene:
    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if 120 < pyxel.mouse_x < 200 and 192 < pyxel.mouse_y < 218:
                game.start_run()

    def draw(self):
        pyxel.mouse(True)
        pyxel.cls(4)
        pyxel.blt(280, 170, 0, *Sprite.TREE_GREEN.value, COLOR_TRANSPARENT, scale=12)
        pyxel.blt(50, 140, 0, *Sprite.SNOWMAN.value, COLOR_TRANSPARENT, scale=8)
        pyxel.blt(140, 40, 0, 0, 32, 32, 16, COLOR_TRANSPARENT, scale=6)
        pyxel.blt(150, 210, 0, 32, 32, 24, 16, COLOR_TRANSPARENT, scale=4)


class PlayingScene:
    def update(self):
        pass

    def draw(self):
        pyxel.cls(1)
        pyxel.camera(0, player.y - 40)

        draw_snowtrack(100, 30, 600, 7)
        draw_snowtrack(240, 200, 800, 20)

        for tx, ty, sprite in objects:
            blt_topleft(tx, ty, 0, *sprite.value, COLOR_TRANSPARENT, scale=2)

        player.draw()

        pyxel.camera()
        pyxel.text(5, 5, f"{player.y} meters", 7)


@dataclass
class Game:
    @enum.unique
    class State(enum.Enum):
        TITLE = 0
        PLAYING = 1
        PLAYING_CRASH = 2
        PAUSED = 3

    state: State = State.TITLE
    scene = TitleScene()

    def start_run(self):
        self.state = self.State.PLAYING
        self.scene = PlayingScene()

    def toggle_pause(self):
        self.state = (
            self.State.PAUSED
            if self.state == self.State.PLAYING
            else self.State.PLAYING
        )

    def transition_to_crash(self):
        self.state = self.State.PLAYING_CRASH

    def transition_to_playing(self):
        self.state = self.State.PLAYING

    @property
    def is_paused(self):
        return self.state == self.State.PAUSED


@enum.unique
class Sprite(enum.Enum):
    PLAYER_DOWN = 0, 0, 8, 8
    PLAYER_LEFT = 8, 0, 8, 8
    PLAYER_RIGHT = 0, 8, 8, 8
    PLAYER_JUMPING = 8, 8, 8, 8
    PLAYER_CRASHED = 16, 0, 8, 8
    TREE_GREEN = 0, 16, 16, 16
    TREE_HALF = 14, 16, 16, 16
    TREE_WHITE = 32, 16, 16, 16
    TREE_EMPTY = 48, 16, 16, 16
    ROCK_SMALL = 0, 48, 8, 8
    ROCK_WIDE = 0, 56, 16, 8
    SNOWMAN = 0, 64, 16, 16
    SNOWBALL_1 = 16, 64, 8, 8
    SNOWBALL_2 = 24, 64, 8, 8
    SNOWBALL_3 = 16, 72, 8, 8
    SNOWBALL_4 = 24, 72, 8, 8


class BoundingBox(enum.Enum):
    TREE_GREEN = (3, 0, 11, 12)
    TREE_HALF = TREE_GREEN
    TREE_WHITE = TREE_GREEN
    TREE_EMPTY = TREE_GREEN
    ROCK_SMALL = (1, 1, 7, 4)
    ROCK_WIDE = (3, 3, 11, 5)


@dataclass
class Player:
    x: int = 160
    y: int = 30
    direction: Direction = Direction.DOWN
    state: PlayerState = PlayerState.MOVING
    anim_frames_remaining: int = 0

    def update(self, frame_diff: int):
        if game.state == game.State.PLAYING_CRASH:
            return

        self.anim_frames_remaining -= frame_diff

        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.state == PlayerState.MOVING and self.direction == Direction.DOWN:
                self.state = PlayerState.JUMPING
                self.anim_frames_remaining = 50

        if self.anim_frames_remaining <= 0 and self.state == PlayerState.JUMPING:
            self.state = PlayerState.MOVING

        if self.state == PlayerState.MOVING:
            new_direction = None
            if pyxel.btnp(pyxel.KEY_LEFT):
                new_direction = max(Direction.LEFT.value, self.direction.value - 1)
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                new_direction = min(Direction.RIGHT.value, self.direction.value + 1)
            if new_direction is not None:
                self.direction = Direction(new_direction)

        if self.direction == Direction.LEFT:
            self.x = max(self.x - 1, 0)
        elif self.direction == Direction.RIGHT:
            self.x = min(self.x + 1, pyxel.width - 8)

        if self.x == 0 or self.x == pyxel.width - 8:
            self.direction = Direction.DOWN

        if game.state == game.State.PLAYING:
            self.y += 1

    def draw(self):
        if game.state == game.State.PLAYING_CRASH:
            sprite = Sprite.PLAYER_CRASHED
        elif self.state == PlayerState.JUMPING:
            sprite = Sprite.PLAYER_JUMPING
        else:
            sprite = {
                Direction.DOWN: Sprite.PLAYER_DOWN,
                Direction.LEFT: Sprite.PLAYER_LEFT,
                Direction.RIGHT: Sprite.PLAYER_RIGHT,
            }[self.direction]

        width, height = sprite.value[2:]
        blt_topleft(self.x, self.y, 0, *sprite.value, COLOR_TRANSPARENT, scale=2)

    def reset(self):
        self.x = pyxel.ceil(pyxel.width / 2)
        self.y = 0
        self.direction = Direction.DOWN
        self.state = PlayerState.MOVING


objects: list[tuple[int, int, Sprite]] = []
for _ in range(100):
    sprite = random.choice([Sprite.TREE_GREEN, Sprite.TREE_HALF, Sprite.TREE_WHITE])
    objects.append(
        (
            random.randint(0, pyxel.width - 16),
            random.randint(0, pyxel.height * 10),
            sprite,
        )
    )

for _ in range(30):
    objects.append(
        (
            random.randint(0, pyxel.width - 16),
            random.randint(0, pyxel.height * 10),
            random.choice([Sprite.ROCK_SMALL, Sprite.ROCK_WIDE]),
        )
    )

game = Game()
title_scene = TitleScene()
player = Player()
tooltip = Tooltip()


def two_sprites_collide(x1, y1, w1, h1, x2, y2, w2, h2):
    """
    Check if two sprites collide.

    x1,y2     w1
    +---------+----------+
    |                    |
    |       x2,y2        |
    +h1     +-----------------------+
    |       |            |          |
    +-------|------------+          +h2
            |                       |
            +----------+------------+
                       w2
    """
    # TODO understand this
    return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2


def check_collisions():
    global game_state
    for x, y, sprite in objects:
        w, h = sprite.value[2:]
        bx, by, bw, bh = BoundingBox[sprite.name].value
        if two_sprites_collide(
            player.x, player.y, 8 * 2, 8 * 2, x + bx * 2, y + by * 2, bw * 2, bh * 2
        ):
            if (
                sprite is Sprite.ROCK_SMALL or sprite is Sprite.ROCK_WIDE
            ) and player.state == PlayerState.JUMPING:
                continue

            game.transition_to_crash()


last_frame = pyxel.frame_count


def update():
    global last_frame, game_state

    frame_diff, last_frame = pyxel.frame_count - last_frame, pyxel.frame_count

    tooltip.update()

    if game.state == Game.State.TITLE:
        title_scene.update()
        return

    if pyxel.btnp(pyxel.KEY_R):
        game.transition_to_playing()
        player.reset()

    if pyxel.btnp(pyxel.KEY_P):
        game.toggle_pause()

    if game.is_paused:
        return

    player.update(frame_diff)
    check_collisions()

    if player.y > pyxel.height * 10:
        player.y = 0


def draw_snowtrack(x, y, length, frequency):
    for y in range(y, length, frequency):
        amplitude = math.sin(y / 100) * 40
        x0 = math.sin(y) * amplitude
        x1 = math.sin(y + frequency) * amplitude
        pyxel.line(x0 + x, y, x1 + x, y + frequency, 0)


def draw():
    game.scene.draw()
    tooltip.draw()


pyxel.run(update, draw)
