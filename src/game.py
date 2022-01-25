import pickle
import requests
from typing import *
from time import time
from random import randint
from dataclasses import dataclass, field
from pygame import Vector2 as vec2

from src.snake import Snake
from src.apple import Apple

@dataclass
class GameData:
    """
        Almacena los datos del juego necesarios para poder dibujar la escena.
    """
    snakes: Dict[str, Snake] = field(default_factory=dict)
    apples: Set[Apple] = field(default_factory=set)

class Game:
    # Dimensiones y color de la pantalla
    X = 1350
    Y = 700
    BG_COLOR = (0, 0, 0)
    # Numero maximo de manzanas
    MAX_APPLES = 100
    APPLE_TIME_SPAWM = 2

    def __init__(self):
        # Llevamos un contador del tiempo actual
        self.clock = time()
        self.apple_clock = time()

        # Datos del juego
        self.players: Dict[str, Snake] = {}
        self.clients: Dict[str, str] = {}
        self.apples: Set[Apple] = set()

        # Creamos varias manzanas
        for _ in range(10): self.add_random_apple()

    def add_apple(self, x: int, y: int):
        """
            Agrega una nueva manzana al juego.
        """
        self.apples.add(Apple((x, y)))

    def add_random_apple(self):
        """
            Agrega una nueva manzana en la pantalla con una posicion aleatoria.
        """
        x = randint(10, self.X-10)
        y = randint(10, self.Y-10)
        self.add_apple(x, y)

    def is_loser(self, uid):
        """
            Verifica si un usuario queda descalificado.
        """
        x, y = self.players[uid].head_pos
        return x < 0 or x > self.X or y < 0 or y > self.Y

    def update(self, delta_time: float):
        """
            Actualiza un frame del juego.
        """
        # Actualizamos cada jugador
        for uid in self.players: self.players[uid].update(delta_time)

        # Verificamos que jugadores perdieron y cuales se comieron alguna manzana
        losers= set()
        for uid in self.players:
            # Verificamos si el jugador perdio
            if self.is_loser(uid):
                losers.add(uid)
                continue
            
            x, y = self.players[uid].head_pos
            r_2 = self.players[uid].head_radius ** 2

            # Verificamos que manzanas se comio
            eaten = set()
            for apple in self.apples:
                if apple in eaten: continue

                # Solo tenemos que usar la formula de la circunferencia para saber si
                # una manzana esta dentro de la cabeza de una serpiente
                x_a, y_a = apple.pos
                if (x_a - x) ** 2 + (y_a - y) ** 2 < r_2:
                    self.players[uid].eat()
                    eaten.add(apple)

            # Eliminamos las manzanas que se comieron
            for apple in eaten:
                self.apples.discard(apple)
        
        # Verificamos si se debe spanear una nueva manzana
        diff_time = time() - self.apple_clock
        if diff_time > self.APPLE_TIME_SPAWM and len(self.apples) < self.MAX_APPLES:
            self.apple_clock = time()
            self.add_random_apple()

        # Eliminamos los jugadores que perdieron
        for uid in losers:
            # Agregamos las manzanas generadas por la muerte de la serpiente
            self.apples = self.apples.union(self.players[uid].death_apples())

            # Enviamos un game_over al jugador
            try: requests.post(self.clients[uid] + '/game_over', timeout=0.15)
            except: pass
            self.players.pop(uid)
            self.clients.pop(uid)


        # Enviamos el estado del juego a cada jugador
        data = pickle.dumps(GameData(self.players, self.apples), protocol=2)

        try:
            for c in self.clients:
                try: requests.post(self.clients[c] + '/draw', data, timeout=0.15)
                except: pass
        except: pass

    def run(self):
        """
            Mantiene el juego actualizandose indefinidamente
        """
        while True:
            new_time = time()
            self.delta_time = new_time - self.clock
            self.clock = new_time
            self.update(self.delta_time)
