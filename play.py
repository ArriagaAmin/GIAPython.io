# Utilidades
import pickle
import requests
from sys import argv
from threading import Thread

# Juego
import pygame
from pygame import gfxdraw
from src.game import Game

# Servidor
from flask import Flask, request
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class Client:
    # Iniciamos pygame
    pygame.init()
    window = pygame.display.set_mode(
        (int(Game.CAMERA_X), int(Game.CAMERA_Y))
    )
    background = pygame.Surface((Game.X + Game.CAMERA_X, Game.Y + Game.CAMERA_Y))
    pygame.display.set_caption("GIAPython.io")
    clock = pygame.time.Clock()

    # Enviamos solicitud de incorporacion al servidor
    server = 'http://192.168.1.106:5000'

    @classmethod
    def new_player(cls):
        data = {'port': cls.port}
        cls.id = requests.get(cls.server + '/new_player', data, timeout=1).json()['id']

    @classmethod
    def send_status(cls):
        game_over = False
        while not game_over:
            keys = pygame.key.get_pressed()
            data = {
                'id': cls.id,
                'press_a': keys[pygame.K_a],
                'press_d': keys[pygame.K_d],
                'press_w': keys[pygame.K_w]
            }
            try:
                response = requests.post(cls.server + '/update', data, timeout=0.15)
                game_over = response.json()['status'] == 1
                pygame.event.pump()
            except:
                break


app = Flask(__name__)

@app.route("/draw", methods=["POST"])
def draw():
    # Endpoint para obtener los datos del servidor y dibujar la pantalla
    game = pickle.loads(request.data)

    min_x = Game.CAMERA_X / 2 - 25
    min_y = Game.CAMERA_Y / 2 - 25
    max_x = min_x + Game.X + 30
    max_y = min_y + Game.Y + 30
    Client.background.fill(Game.BG_COLOR)

    for uid in game.snakes:
        game.snakes[uid].draw(Client.background)

    for apple in game.apples:
        apple.draw(Client.background)

    # Dibujamos el fondo y un marco
    gfxdraw.box(
        Client.background,
        (min_x, min_y, Game.X + 40, 20),
        (255, 255, 255)
    )
    gfxdraw.box(
        Client.background,
        (min_x, min_y, 20, Game.Y + 40),
        (255, 255, 255)
    )
    gfxdraw.box(
        Client.background,
        (max_x, min_x, 20, Game.Y + 40),
        (255, 255, 255)
    )
    gfxdraw.box(
        Client.background,
        (min_x, max_y, Game.X + 40, 20),
        (255, 255, 255)
    )

    # Obtenemos la seccion de la superficie donde la serpiente esta en el centro
    x, y = game.snakes[Client.id].head_pos
    Client.window.blit(
        Client.background, 
        (0, 0), 
        (x - Game.CAMERA_X / 2, y - Game.CAMERA_Y / 2, Game.CAMERA_X, Game.CAMERA_Y)
    )
    pygame.display.flip()

    return ''

@app.route("/game_over", methods=["POST"])
def game_over(): 
    # Game over
    pygame.display.quit()
    pygame.quit()
    print('\n\033[1;3;31mGAME OVER\033[0m\n')
    
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return ''

if __name__ == '__main__':
    Client.port = int(argv[1])
    Client.new_player()
    th = Thread(target=Client.send_status)
    th.start()
    app.run(host="0.0.0.0", port=Client.port)

