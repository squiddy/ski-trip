import math
import pyxel
import enum
from dataclasses import dataclass, field

from helpers import blt_topleft, Tooltip, text_centered, frames_rendered

FPS = 60
COLOR_TRANSPARENT = 11

pyxel.init(320, 240, fps=FPS)
pyxel.load("main.pyxres")
pyxel.rseed(0)


@enum.unique
class Direction(enum.Enum):
    LEFT = -1
    DOWN = 0
    RIGHT = +1


@enum.unique
class PlayerState(enum.Enum):
    MOVING = 0
    JUMPING = 1


class TitleScene:
    @dataclass
    class Snowflake:
        x: int
        y: int
        speed_x: int
        speed_y: int

    def __init__(self):
        self.flakes = []
        for _ in range(10):
            self.flakes.append(
                self.Snowflake(
                    pyxel.rndi(0, pyxel.width),
                    pyxel.rndi(0, pyxel.height),
                    pyxel.rndi(1, 2),
                    pyxel.rndi(1, 2),
                )
            )

    def update(self):
        if pyxel.btnp(pyxel.KEY_S):
            game.start_run()

        for flake in self.flakes:
            flake.x += flake.speed_x
            flake.y += flake.speed_y
            if flake.y > pyxel.height:
                flake.y = -20
            if flake.x > pyxel.width:
                flake.x = -20

    def draw(self):
        pyxel.cls(4)
        pyxel.blt(280, 170, 0, *Sprite.TREE_GREEN.value, COLOR_TRANSPARENT, scale=12)
        pyxel.blt(50, 140, 0, *Sprite.SNOWMAN.value, COLOR_TRANSPARENT, scale=8)
        pyxel.blt(140, 40, 0, *Sprite.LOGO.value, COLOR_TRANSPARENT, scale=6)
        text_centered(pyxel.width / 2, 180, "Press S to start", 0)

        for flake in self.flakes:
            pyxel.blt(
                flake.x,
                flake.y,
                0,
                *Sprite.SNOWFLAKE.value,
                COLOR_TRANSPARENT,
                scale=flake.speed_y,
            )


class PlayingScene:
    def __init__(self) -> None:
        random_choice = lambda l: l[pyxel.rndi(0, len(l)-1)]

        self.player = Player()
        self.objects: list[tuple[int, int, Sprite]] = []
        for _ in range(100):
            sprite = random_choice(
                [Sprite.TREE_GREEN, Sprite.TREE_HALF, Sprite.TREE_WHITE]
            )
            self.objects.append(
                (
                    pyxel.rndi(0, pyxel.width - 16),
                    pyxel.rndi(100, pyxel.height * 10),
                    sprite,
                )
            )

        for _ in range(30):
            self.objects.append(
                (
                    pyxel.rndi(0, pyxel.width - 16),
                    pyxel.rndi(100, pyxel.height * 10),
                    random_choice([Sprite.ROCK_SMALL, Sprite.ROCK_WIDE]),
                )
            )

    def update(self):
        self.player.update()
        if check_collisions(self.player, self.objects):
            game.game_over()

    def draw(self):
        pyxel.cls(1)
        pyxel.camera(0, self.player.y - 40)

        draw_snowtrack(100, 30, 600, 2)
        draw_snowtrack(240, 200, 800, 4)

        for tx, ty, sprite in self.objects:
            blt_topleft(tx, ty, 0, *sprite.value, COLOR_TRANSPARENT, scale=2)

        self.player.draw()

        pyxel.camera()
        pyxel.text(5, 5, f"{int(self.player.y)} meters", 7)


class GameOverScene:
    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            game.start_run()

    def draw(self):
        pyxel.cls(5)

        blt_topleft(
            150, 40, 0, *Sprite.PLAYER_CRASHED.value, COLOR_TRANSPARENT, scale=12
        )
        text_centered(pyxel.width / 2, 140, "Game over", 0)
        text_centered(pyxel.width / 2, 160, "Press R to restart", 1)


class GameWonScene:
    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            game.start_run()

    def draw(self):
        pyxel.cls(9)

        pyxel.rect(0, 215, pyxel.width, 50, 0)
        blt_topleft(
            150, 140, 0, *Sprite.WON.value, COLOR_TRANSPARENT, scale=12
        )
        text_centered(pyxel.width / 2, 20, "Game won", 0)
        text_centered(pyxel.width / 2, 40, "Press R to restart", 1)


@dataclass
class Game:
    @enum.unique
    class State(enum.Enum):
        TITLE = 0
        PLAYING = 1
        GAME_OVER = 2
        GAME_WON = 3

    state: State = State.TITLE
    scene = TitleScene()

    def start_run(self):
        self.state = self.State.PLAYING
        self.scene = PlayingScene()

    def game_over(self):
        self.state = self.State.GAME_OVER
        self.scene = GameOverScene()

    def game_won(self):
        self.state = self.State.GAME_WON
        self.scene = GameWonScene()


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
    LOGO = 0, 32, 32, 16
    SNOWFLAKE = 32, 32, 9, 11
    WON = 24, 0, 16, 16


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
    track: list[tuple[int, int]] = field(default_factory=list)

    def update(self):
        self.anim_frames_remaining -= frames_rendered()

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
            self.y += self.get_speed()

            if len(self.track) > 40:
                self.track.pop(0)
            self.track.append((self.x, self.y))

        if self.y > 1200:
            game.game_won()

    def get_speed(self):
        speed = 1
        if self.direction != Direction.DOWN:
            speed *= 0.8
        return speed

    def draw(self):
        for x, y in self.track:
            pyxel.pset(x + 6, y, 0)

        if self.state == PlayerState.JUMPING:
            sprite = Sprite.PLAYER_JUMPING
        else:
            sprite = {
                Direction.DOWN: Sprite.PLAYER_DOWN,
                Direction.LEFT: Sprite.PLAYER_LEFT,
                Direction.RIGHT: Sprite.PLAYER_RIGHT,
            }[self.direction]

        width, height = sprite.value[2:]
        blt_topleft(self.x, self.y, 0, *sprite.value, COLOR_TRANSPARENT, scale=2)


game = Game()
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


def check_collisions(player: Player, objects) -> bool:
    for x, y, sprite in objects:
        w, h = sprite.value[2:]
        bx, by, bw, bh = BoundingBox[sprite.name].value
        if two_sprites_collide(
            player.x, player.y, 8 * 2, 8 * 2, x + bx * 2, y + by * 2, bw * 2, bh * 2
        ):
            if (
                sprite is Sprite.ROCK_SMALL or sprite is Sprite.ROCK_WIDE
            ) and player.state == PlayerState.JUMPING:
                return False

            return True

    return False


def draw_snowtrack(x: int, y: int, length: int, frequency: int):
    for y in range(y, length, frequency):
        amplitude = pyxel.sin(y / 100) * 400
        x0 = pyxel.sin(y) * amplitude
        x1 = pyxel.sin(y + frequency) * amplitude
        pyxel.line(x0 + x, y, x1 + x, y + frequency, 0)


def update():
    tooltip.update()
    game.scene.update()


def draw():
    game.scene.draw()
    tooltip.draw()


pyxel.run(update, draw)
