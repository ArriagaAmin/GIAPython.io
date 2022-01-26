import json
from typing import *
from src.apple import Apple
from pygame import gfxdraw, Surface, Vector2 as vec2

# Cargamos las variables de entorno
with open('.env.json', 'r') as f:
    ENV = json.load(f)

class Snake:
    SPEED           : float = ENV['SPEED']
    TURN_SPEED      : float = ENV['TURN_SPEED']
    BOOST_SPEED     : float = ENV['BOOST_SPEED']
    MAX_BOOST_COUNT : int = ENV['MAX_BOOST_COUNT']
    MIN_BOOST_LEN   : int = ENV['MIN_BOOST_LEN']

    def __init__(self, position: vec2, color: Tuple[int, int, int]):
        # Posicion, direccion y radio de la cabeza (y por lo tanto de todo su cuerpo)
        self.head_pos = position
        self.head_radius: int = 5
        self.heading: float = 0

        # Velocidades
        self.boosting = False
        self.boosting_count = 0
        self.velocity = vec2()

        # Cuerpo
        self.tail: List[vec2] = [vec2() for _ in range(50)]
        self.color = color

    def update(self):
        """
            Actualiza la posicion de la serpiente
        """
        # Hacemos que cada segmento de la cola "sigua" al segmento en frente de el.
        tail_length = len(self.tail)
        for i in range(1, tail_length):
            self.tail[tail_length - i].update(self.tail[tail_length - (i + 1)])
        self.tail[0].update(self.head_pos)

        # Actualizamos la posicion de la cabeza segun su velocidad
        if self.boosting and len(self.tail) >= self.MIN_BOOST_LEN:
            speed = self.BOOST_SPEED
            # Verificamos el contador de boosting, si alcanza el maximo, la serpiente
            # decrece
            if self.boosting_count < self.MAX_BOOST_COUNT:
                self.boosting_count += 1
            else:
                self.boosting_count = 0
                self.tail.pop()
                self.head_radius = len(self.tail) // 28 + 4
        else:
            speed = self.SPEED
        self.velocity.from_polar((speed, self.heading))
        self.head_pos += self.velocity * ENV['DELTA_TIME']

    def eat(self):
        """
            Alimenta a la serpiente, haciendola crecer.
        """
        x, y = self.tail[-1]
        for _ in range(7): self.tail.append(vec2([x, y]))
        self.head_radius = len(self.tail) // 28 + 4

    def death_apples(self) -> Set[Apple]:
        """
            Manzanas que se deben generar cuando muere la serpiente
        """
        apples = set()
        for i in range(len(self.tail)):
            if i % 10 == 0:
                x, y = self.tail[i]
                apples.add(Apple((x, y)))
        return apples

    def draw(self, window: Surface):
        """
            Dibuja a la serpiente.
        """
        # Dibujamos la cabeza
        gfxdraw.filled_circle(
            window,
            int(self.head_pos.x),
            int(self.head_pos.y),
            self.head_radius,
            self.color,
        )

        # Dibujamos cada segmento de la cola
        for (i, tail_segment) in enumerate(self.tail):
            alpha = 1 - i / len(self.tail)
            gfxdraw.filled_circle(
                window,
                int(tail_segment.x),
                int(tail_segment.y),
                int(self.head_radius * 0.85),
                (
                    self.color[0] * alpha,
                    self.color[1] * alpha,
                    self.color[2] * alpha,
                ),
            )
