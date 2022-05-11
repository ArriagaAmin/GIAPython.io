# Reference:
#   https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data

# Utilities
import math
import socket
import struct
import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
from uuid import uuid4
from typing import Tuple 
from threading import Thread
from random import randint, random

# Game
import pygame
from pygame import gfxdraw
from src.snake import Snake
from src.game import Game, GameData, Rate
from src.__env__ import DELTA_TIME, X, CAMERA_X, Y, CAMERA_Y, CAPTION, \
    BG_COLOR, TURN_SPEED, RATE


def __recvall(sock: socket.socket, n: int) -> bytearray:
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def send_msg(sock: socket.socket, msg: bytes):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock: socket.socket) -> bytearray:
    # Read message length and unpack it into an integer
    raw_msglen = __recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return __recvall(sock, msglen)


class Server(object):
    """
        Servidor que mantiene al juego actualizado
    """
    def __init__(self, ip: str, port: int):
        self.ip = ip 
        self.port = port 

        # Creamos el juego y hacemos que se mantenga actualizado en un hilo distinto
        self.game = Game()
        th = Thread(target=self.game.run)
        th.start()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip, port))

    def __new_snake(self, addr: str, color: Tuple[int, int, int]) -> str:
        """
            Agrega a un nuevo jugador.
        """
        uuid = uuid4()

        # Obtenemos una posicion aleatoria
        new_position = (
            randint(CAMERA_X // 2 + 100, CAMERA_X // 2 + X - 100),
            randint(CAMERA_Y // 2 + 100, CAMERA_Y // 2 + Y - 100)
        )
        # Creamos una nueva serpiente
        new_snake = Snake(new_position, color, self.game.collisions, uuid)
        new_snake.heading = randint(0, 360)
        # Agregamos al jugador
        self.game.players[str(uuid)] = new_snake
        self.game.clients[str(uuid)] = addr

        # Retornamos el ID
        return str(uuid)

    def __update_snake(self, id: str, a: bool, d: bool, w: bool):
        """
            Actualiza el estado de una serpiente de acuerdo a las teclas que estan siendo
            apretadas por el jugador.

            Parametros:
            -----------
                * id: str
                    ID del jugador
                * a: bool
                    Indica si se esta presionando la tecla a.
                * d: bool
                    Indica si se esta presionando la tecla d.
                * w: bool
                    Indica si se esta presionando la tecla w.
        """
        self.game.players[id].boosting = w
        self.game.players[id].heading += ((d - a) * TURN_SPEED * DELTA_TIME)

    def __process_client(self, conn: socket.socket, addr: str):
        """
            Mantiene una conexion constante con un cliente especifico
        """
        while True:
            msg = recv_msg(conn)

            # Verificamos si se envio un mensaje None.
            if msg == None: continue

            # Verificamos que tipod e request se esta realizando
            data = pickle.loads(msg)
            request = data['request']

            # Crear una nueva serpiente (jugador)
            if request == 'New player':
                color = data['color']
                new_id = self.__new_snake(addr, color)
                response = pickle.dumps(new_id)
                send_msg(conn, response)

            # Moverse
            elif request == 'Update':
                id = data['id']
                press_a = data['press_a']
                press_d = data['press_d']
                press_w = data['press_w']

                player_exists = id in self.game.players

                if player_exists:
                    self.__update_snake(id, press_a, press_d, press_w)

            # Obtener datos del juego
            elif request == 'World':
                # Intente usar threading.Lock pero por alguna razon no funciono
                # Asi que aqui esta mi cutre solucion
                while True:
                    try:
                        response = pickle.dumps(
                            self.game.get_data() , 
                            protocol=2
                        )
                        break 
                    except:
                        pass 
                send_msg(conn, response)

            # Cerrar la conexion
            elif request == 'Shutdown':
                conn.shutdown(0)
                conn.close()
                break

    def run(self):
        """
            Se mantiene escuchando a la espera de nuevos jugadores
        """
        print(f'Running server in socket: \033[1m{self.ip}:{self.port}\033[0m')
        self.socket.listen()
        while True:
            conn, addr = self.socket.accept()
            th = Thread(target=self.__process_client, args=(conn, addr))
            th.start()

class Client(object):
    """
        Cliente que representa a un jugador
    """
    def __init__(
            self, 
            server_ip: str, 
            server_port: int, 
            graphic: bool, 
            color: Tuple[int, int, int],
            image_filename: str
        ):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_ip, server_port))
        self.interface_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interface_socket.connect((self.server_ip, self.server_port))
        self.graphic = graphic 
        self.color = color
        self.image_filename = image_filename
        self.game_over = 0

        # Iniciamos pygame
        pygame.init()

        self.clock = pygame.time.Clock()

    def __draw(self, world: GameData):
        """
            Dibuja la interfaz del juego
        """
        min_x = CAMERA_X / 2 - 25
        min_y = CAMERA_Y / 2 - 25
        max_x = min_x + X + 30
        max_y = min_y + Y + 30
        self.background.fill(BG_COLOR)

        for circle in world.circles:
            gfxdraw.filled_circle(
                self.background,
                int(circle[0][0]),
                int(circle[0][1]),
                circle[1],
                circle[2],
            )

        # Dibujamos el fondo y un marco
        gfxdraw.box(
            self.background,
            (min_x, min_y, X + 40, 20),
            (255, 255, 255)
        )
        gfxdraw.box(
            self.background,
            (min_x, min_y, 20, Y + 40),
            (255, 255, 255)
        )
        gfxdraw.box(
            self.background,
            (max_x, min_y, 20, Y + 40),
            (255, 255, 255)
        )
        gfxdraw.box(
            self.background,
            (min_x, max_y, X + 40, 20),
            (255, 255, 255)
        )

        # Obtenemos la seccion de la superficie donde la serpiente esta en el centro
        x, y = world.snakes_id[self.id]
        self.window.blit(
            self.background, 
            (0, 0), 
            (x - CAMERA_X / 2, y - CAMERA_Y / 2, CAMERA_X, CAMERA_Y)
        )
        
        # Convertimos la imagen en un archivo
        imgdata = pygame.surfarray.array3d(self.window)
        imgdata = np.swapaxes(imgdata, 0, 1)
        img = Image.fromarray(imgdata, 'RGB')
        img.save(self.image_filename)

        if self.graphic:
            pygame.display.flip()

    def __run_interface(self):
        """
            Mantiene actualizada la interfaz del juego
        """
        # Obtenemos los datos del mundo
        send_msg(self.interface_socket, pickle.dumps({'request': 'World'}))
        world : GameData = pickle.loads(recv_msg(self.interface_socket))

        while not self.game_over:
            self.__draw(world)
            send_msg(self.interface_socket, pickle.dumps({'request': 'World'}))
            world : GameData = pickle.loads(recv_msg(self.interface_socket))
            self.game_over = self.id not in world.snakes_id

        # Game over
        if self.graphic:
            pygame.display.quit()
            pygame.quit()

    def run(self):
        """
            Se mantiene conectado al servidor para actualizar el juego
        """
        while True:
            # Enviamos la solicitud para un nuevo jugador
            data = {'request': 'New player', 'color': self.color}
            send_msg(self.socket, pickle.dumps(data))

            # Obtenemos el id de nuestro jugador
            self.id = pickle.loads(recv_msg(self.socket))

            self.game_over = 0

            self.background = pygame.Surface((X + CAMERA_X, Y + CAMERA_Y))
            if self.graphic:
                self.window = pygame.display.set_mode((CAMERA_X, CAMERA_Y))
                pygame.display.set_caption(CAPTION)
            else:
                self.window = pygame.Surface((CAMERA_X, CAMERA_Y))
                
            # Creamos un hilo para la interfaz
            th = Thread(target=self.__run_interface)
            th.start()

            rate = Rate(2 * RATE)
            while not self.game_over:
                # Obtenemos las teclas presionadas
                # Aqui es donde iria la accion de la IA
                keys = pygame.key.get_pressed()
                press_a, press_d, press_w = (
                    keys[pygame.K_a], 
                    keys[pygame.K_d], 
                    keys[pygame.K_w]
                )

                # Actualizamos nuestra serpiente
                data = {
                    'request': 'Update',
                    'id': self.id,
                    'press_a': press_a,
                    'press_d': press_d,
                    'press_w': press_w
                }
                send_msg(self.socket, pickle.dumps(data))

                pygame.event.pump()
                rate.sleep()

            print('\n\033[1;3;31mGAME OVER\033[0m\n')

            response = input('Quiere jugar de nuevo? [Y/n] ')
            if response == 'n' or response == 'N': break

        send_msg(self.socket, pickle.dumps({'request': 'Shutdown'}))

class Watcher(object):
    """
        Cliente para observar todo el mapa de juego
    """
    def __init__(self, server_ip: str, server_port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_ip, server_port))
        self.first = True

        # Iniciamos pygame
        pygame.init()

        self.clock = pygame.time.Clock()

    def __draw(self, *args):
        """
            Dibuja la interfaz del juego
        """
        send_msg(self.socket, pickle.dumps({'request': 'World'}))
        world : GameData = pickle.loads(recv_msg(self.socket))

        min_x = CAMERA_X / 2 - 25
        min_y = CAMERA_Y / 2 - 25
        max_x = min_x + X + 30
        max_y = min_y + Y + 30
        self.background.fill(BG_COLOR)

        for circle in world.circles:
            gfxdraw.filled_circle(
                self.background,
                int(circle[0][0]),
                int(circle[0][1]),
                circle[1],
                circle[2],
            )

        # Dibujamos el fondo y un marco
        gfxdraw.box(
            self.background,
            (min_x, min_y, X + 40, 20),
            (255, 255, 255)
        )
        gfxdraw.box(
            self.background,
            (min_x, min_y, 20, Y + 40),
            (255, 255, 255)
        )
        gfxdraw.box(
            self.background,
            (max_x, min_y, 20, Y + 40),
            (255, 255, 255)
        )
        gfxdraw.box(
            self.background,
            (min_x, max_y, X + 40, 20),
            (255, 255, 255)
        )
        
        # Convertimos la imagen en un archivo
        imgdata = pygame.surfarray.array3d(self.background)
        imgdata = np.swapaxes(imgdata, 0, 1)
        
        if self.first:
            self.image = plt.imshow(imgdata, animated=True)
            self.first = False
        else:
            self.image.set_array(imgdata)

        return self.image,

    def run(self):
        """
            Mantiene actualizado el mapa
        """
        self.background = pygame.Surface((X + CAMERA_X, Y + CAMERA_Y))

        fig = plt.figure()
        ani = animation.FuncAnimation(fig, self.__draw, interval=10, blit=True)
        plt.show()






