import pyxel
from dataclasses import dataclass


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


def text_centered(x: int, y: int, text: str, col: int):
    pyxel.text(x - (len(text) * pyxel.FONT_WIDTH / 2), y, text, col)


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
