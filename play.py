# Utilidades
import pickle
import requests
from sys import argv
from threading import Thread

# Juego
import pygame
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
        (int(Game.X), int(Game.Y))
    )
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
    Client.window.fill(Game.BG_COLOR)

    for uid in game.snakes:
        game.snakes[uid].draw(Client.window)

    for apple in game.apples:
        apple.draw(Client.window)

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

