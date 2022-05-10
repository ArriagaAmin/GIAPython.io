from __future__ import annotations

# Utilities
from math import floor
from uuid import uuid4, UUID
from typing import Set, Tuple
from abc import abstractmethod

# Game
from pygame import gfxdraw, Surface
from src.__env__ import APPLE_RADIUS, APPLE_COLOR, TILE_LEN

class GameObject(object):
    """
        Representacion de un objeto del juego. Todos son circulos.
    """
    NAME: str

    @abstractmethod
    def __init__(self):
        self.id: UUID
        self.pos: Tuple[int, int]
        self.radius: int
        self.color: Tuple[int, int, int]


    def tiles(self) -> Set[Tuple[int, int]]:
        """
            Obtenemos un conjunto de casillas ocupados por el objeto.
        """
        min_x = floor((self.pos[0] - self.radius) / TILE_LEN)
        min_y = floor((self.pos[1] - self.radius) / TILE_LEN)
        max_x = floor((self.pos[0] + self.radius) / TILE_LEN)
        max_y = floor((self.pos[1] + self.radius) / TILE_LEN)

        tiles = set()
        for i in range(min_x-1, max_x + 2):
            for j in range(min_y-1, max_y + 2):
                tiles.add((i, j))

        return tiles

    def draw(self, window: Surface):
        """
            Dibuja al circulo.
        """
        gfxdraw.filled_circle(
            window,
            int(self.pos[0]),
            int(self.pos[1]),
            self.radius,
            self.color,
        )

    def collision(self, other: GameObject) -> bool:
        """
            Verifica si colisiona con otro objeto
        """
        dist = (self.pos[0] - other.pos[0])**2 + (self.pos[1] - other.pos[1])**2
        return dist <= (self.radius + other.radius) ** 2


class Apple(GameObject):
    """
        Representacion de una manzana en el juego.
    """
    NAME : str = 'Apple'

    def __init__(self, pos: Tuple[int, int]):
        self.id = uuid4()
        self.pos = pos
        self.radius = APPLE_RADIUS
        self.color = APPLE_COLOR

class SnakeBoddy(GameObject):
    """
        Representacion de una parte del cuerpo de una serpiente en el cuerpo.
    """
    NAME : str = 'Snake'

    def __init__(
            self, 
            pos: Tuple[int, int], 
            radius: int, 
            color: Tuple[int, int, int],
            snake_id: UUID
        ):
        self.id = uuid4()
        self.pos = pos
        self.radius = radius
        self.color = color
        self.snake_id = snake_id

