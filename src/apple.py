from typing import *
from dataclasses import dataclass
from pygame import gfxdraw, Surface

@dataclass(unsafe_hash=True)
class Apple:
    """
        Representacion de una manzana en el juego.
    """
    pos: Tuple[int, int]
    radius: int = 5
    color: Tuple[int, int, int] = (255, 0, 0)

    def draw(self, window: Surface):
        """
            Dibuja la manzana como un circulo.
        """
        gfxdraw.filled_circle(
            window,
            int(self.pos[0]),
            int(self.pos[1]),
            self.radius,
            self.color,
        )