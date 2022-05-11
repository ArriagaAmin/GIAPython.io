# Utilities
from uuid import UUID
from random import randint
from typing import Tuple, List, Set

# Game
from src.GameObject import SnakeBoddy
from src.collisions import CollisionHandler
from src.__env__ import DELTA_TIME, SEGS_BY_APPLE, SPEED, BOOST_SPEED, \
    MIN_BOOST_LEN, MAX_BOOST_COUNT
from pygame import gfxdraw, Surface, Vector2 as vec2

class Snake(object):
    def __init__(
            self, 
            position: Tuple[int, int], 
            color: Tuple[int, int, int], 
            collisions: CollisionHandler,
            uuid: UUID
        ):
        # Manejador de colisiones
        self.collisions = collisions
        self.uuid = uuid

        # Radio y direccion de la serpiente
        self.radius = 5
        self.heading: float = 0

        # Velocidades
        self.boosting = False
        self.boosting_count = 0
        self.velocity = vec2()

        # Cuerpo
        self.color = color
        self.boddy: List[SnakeBoddy] = []
        for _ in range(51): self.__add_segment(position)

    def __add_segment(self, pos: Tuple[int, int]):
        """
            Agrega un nuevo segmento a la serpiente
        """
        seg = SnakeBoddy(pos, self.radius, self.color, self.uuid)
        self.boddy.append(seg)
        self.collisions.add(seg)

    def __pop_segment(self):
        """
            Elimina el ultimo segmento de la cola de la serpiente
        """
        seg = self.boddy.pop()
        self.collisions.delete(seg)

    def __reset(self):
        """
            Elimina y agrega de nuevo todos los objetos al manejador de 
            colisiones
        """
        for seg in self.boddy:
            self.collisions.delete(seg)
            seg.radius = self.radius 
            self.collisions.add(seg)

    def update(self):
        """
            Actualiza la posicion de la serpiente
        """
        # Obtenemos la velocidad de la serpiente
        if self.boosting and len(self.boddy) >= MIN_BOOST_LEN:
            speed = BOOST_SPEED
            # Verificamos el contador de boosting, si alcanza el maximo, la serpiente
            # decrece
            if self.boosting_count < MAX_BOOST_COUNT:
                self.boosting_count += 1
                new_radius = self.radius
            else:
                self.boosting_count = 0
                self.__pop_segment()
                new_radius = len(self.boddy) // 28 + 4
        else:
            speed = SPEED
            new_radius = self.radius

        # Eliminamos el ultimo segmento de la serpiente
        self.__pop_segment()

        # Si el radio cambio, tenemos que eliminar todos los segmentos del
        # manejador de colisiones y volverlos a agregarlos
        if new_radius != self.radius:
            self.radius = new_radius
            self.__reset()

        # Obtenemos la posicion de la cabeza
        self.velocity.from_polar((speed, self.heading))
        head_pos = (
            self.boddy[0].pos[0] + int(self.velocity[0] * DELTA_TIME),
            self.boddy[0].pos[1] + int(self.velocity[1] * DELTA_TIME)
        )

        # Creamos la cabeza
        head = SnakeBoddy(head_pos, self.radius, self.color, self.uuid)
        self.boddy.insert(0, head)
        self.collisions.add(head)

    def eat(self):
        """
            Alimenta a la serpiente, haciendola crecer.
        """
        # Verificamos si el radio cambia
        new_radius = (len(self.boddy) + SEGS_BY_APPLE) // 28 + 4
        if new_radius != self.radius:
            self.radius = new_radius
            self.__reset()

        # Agregamos varios segmentos a la serpiente
        x, y = self.boddy[-1].pos
        for _ in range(SEGS_BY_APPLE): 
            self.__add_segment((x, y))

    def death_apples(self) -> Set[Tuple[int, int]]:
        """
            Manzanas que se deben generar cuando muere la serpiente
        """
        apples = set()
        for i in range(len(self.boddy)):
            if i % 10 == 0:
                x, y = self.boddy[i].pos
                apples.add((
                    randint(x-self.radius, x+self.radius), 
                    randint(y-self.radius, y+self.radius)
                ))
        return apples

    def draw(self, window: Surface):
        """
            Dibuja a la serpiente.
        """
        # Dibujamos la cabeza
        gfxdraw.filled_circle(
            window,
            int(self.boddy[0].pos[0]),
            int(self.boddy[0].pos[1]),
            self.radius,
            self.color,
        )

        # Dibujamos cada segmento de la cola
        for (i, tail_segment) in enumerate(self.boddy):
            alpha = 1 - i / (len(self.boddy) + 10)
            gfxdraw.filled_circle(
                window,
                int(tail_segment.pos[0]),
                int(tail_segment.pos[1]),
                int(self.radius * 0.95),
                (
                    self.color[0] * alpha,
                    self.color[1] * alpha,
                    self.color[2] * alpha,
                ),
            )
