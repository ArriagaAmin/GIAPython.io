from uuid import UUID
from random import randint
from time import time, sleep
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set

from src.snake import Snake
from src.collisions import CollisionHandler
from src.GameObject import Apple, SnakeBoddy
from src.__env__ import X, Y, CAMERA_X, CAMERA_Y, MAX_APPLES, \
    APPLE_TIME_SPAWM, INITIAL_APPLES, RATE


class Rate(object):
    """
        Convenience class for sleeping in a loop at a specified rate

        Reference:
            https://github.com/strawlab/ros_comm/blob/master/clients/rospy/src/rospy/timer.py
    """
    def __init__(self, hz: int):
        """
            Constructor.
            @param hz: hz rate to determine sleeping
            @type  hz: int
        """
        self.last_time = time()
        self.sleep_dur = 1 / hz

    def sleep(self):
        """
            Attempt sleep at the specified rate. sleep() takes into
            account the time elapsed since the last successful
            sleep().
            
            @raise ROSInterruptException: if ROS time is set backwards or if
            ROS shutdown occurs before sleep completes
        """
        curr_time = time()
        # detect time jumping backwards
        if self.last_time > curr_time:
            self.last_time = curr_time

        # calculate sleep interval
        elapsed = curr_time - self.last_time
        sleep(max(0, self.sleep_dur - elapsed))
        self.last_time += self.sleep_dur

        # detect time jumping forwards, as well as loops that are
        # inherently too slow
        if curr_time - self.last_time > self.sleep_dur * 2:
            self.last_time = curr_time

@dataclass
class GameData(object):
    """
        Almacena los datos del juego necesarios para poder dibujar la escena.
    """
    circles: List[Tuple[
        Tuple[int, int],    # Centro
        int,                # Radio
        Tuple[int, int, int]# Color
    ]] = field(default_factory=list)
    snakes_id: Dict[str, Tuple[int, int]] = field(default_factory=dict)

class Game(object):
    def __init__(self):
        # Llevamos un contador del tiempo actual
        self.apple_clock = time()

        # Datos del juego
        self.players: Dict[UUID, Snake] = {}
        self.clients: Dict[str, str] = {}
        self.apples: Dict[UUID, Apple] = {}
        self.dead: Set[UUID] = set()

        # Inicializamos el manejador de colisiones
        self.collisions = CollisionHandler()

        # Creamos varias manzanas
        for _ in range(INITIAL_APPLES): 
            self.add_random_apple()

    def add_apple(self, x: int, y: int):
        """
            Agrega una nueva manzana al juego.
        """
        apple = Apple((x, y))
        self.collisions.add(apple)
        self.apples[apple.id] = apple

    def remove_apple(self, apple: Apple):
        """
            Elimina una manzana del juego
        """
        self.collisions.delete(apple)
        self.apples.pop(apple.id)

    def add_random_apple(self):
        """
            Agrega una nueva manzana en la pantalla con una posicion aleatoria.
        """
        x = randint(CAMERA_X / 2, CAMERA_X / 2 + X)
        y = randint(CAMERA_Y / 2, CAMERA_Y / 2 + Y)
        self.add_apple(x, y)

    def is_loser(self, head: SnakeBoddy, uuid: UUID):
        """
            Verifica si un usuario queda descalificado.
        """
        # La serpiente muere si se sale del mapa.
        x, y = head.pos
        if x < CAMERA_X / 2 or x > CAMERA_X / 2 + X or \
            y < CAMERA_Y / 2 or y > CAMERA_Y / 2 + Y:
            return True

        # La serpiente muere si choca contra otra serpiente
        snake_collision : List[SnakeBoddy] = self.collisions.collision_with(head, 'Snake')
        for obj in snake_collision:
            if obj.snake_id in self.dead:
                self.collisions.delete(obj)
            elif str(obj.snake_id) != str(uuid):
                return True

        return False

    def update(self):
        """
            Actualiza un frame del juego.
        """
        # Actualizamos cada jugador
        for uuid in self.players: self.players[uuid].update()

        # Verificamos que jugadores perdieron y cuales se comieron alguna manzana
        losers = set()
        for uuid in self.players:
            head = self.players[uuid].boddy[0]

            # Verificamos si el jugador perdio
            if self.is_loser(head, uuid):
                self.dead.add(uuid)
                losers.add(uuid)
                continue

            # Verificamos que manzanas se comio
            eaten = self.collisions.collision_with(head, 'Apple')

            # Eliminamos las manzanas comidas
            for apple in eaten:
                self.remove_apple(apple)
                self.players[uuid].eat()
        
        for uuid in losers:
            # Agregamos las manzanas generadas por la muerte de la serpiente
            for apple in self.players[uuid].death_apples():
                self.add_apple(*apple)

            # Eliminamos todos los segmentos de la serpiente del manejador de
            # colisiones
            for segment in self.players[uuid].boddy:
                self.collisions.delete(segment)

            self.players.pop(uuid)
            self.clients.pop(uuid)

        # Verificamos si se debe spawmear una nueva manzana
        diff_time = time() - self.apple_clock
        if diff_time > APPLE_TIME_SPAWM and len(self.apples) < MAX_APPLES:
            self.apple_clock = time()
            self.add_random_apple()

    def get_data(self) -> GameData:
        """
            Obtiene los datos para dibujar el mapa del juego
        """
        gd = GameData()

        for apple_id in self.apples:
            apple = self.apples[apple_id]
            gd.circles.append((apple.pos, apple.radius, apple.color))

        for snake_id in self.players:
            gd.snakes_id[snake_id] = self.players[snake_id].boddy[0].pos
            for segment in self.players[snake_id].boddy:
                gd.circles.append((segment.pos, segment.radius, segment.color))

        return gd

    def run(self):
        """
            Mantiene el juego actualizandose indefinidamente
        """
        rate = Rate(RATE)
        count = 0
        begin_time = time()

        while True: 
            try: self.update()
            except: continue
            rate.sleep()

            if count == RATE * 60:
                vel = RATE * 60 / (time() - begin_time)
                print(f'Executing approximately {vel} steps per second.')
                count = 0
                begin_time = time()
            else:
                count += 1
