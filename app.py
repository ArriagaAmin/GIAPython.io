# Utilidades
from random import randint
from threading import Thread

# Juego
from src.game import Game
from src.snake import Snake 
from pygame import Vector2 as vec2

# Servidor
from flask import Flask, request
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class PythonIO:
    """
        Clase que sirve como wrapper del juego, permitiendo modificar la partida desde
        la app de Flask
    """
    # Creamos el juego y hacemos que se mantenga actualizado en un hilo distinto
    game = Game()
    th = Thread(target=game.run)
    th.start()
    # Tenemos un id de cada jugador
    id = 0

    @classmethod
    def new_snake(cls, client: str) -> str:
        """
            Agrega a un nuevo jugador.

            Parametros:
            -----------
                * client: str
                    Endpoint del jugador

            Return:
            -------
                * str
                    ID del jugador
        """
        # Obtenemos una posicion aleatoria
        new_position = vec2(
            randint(0, int(cls.game.X / 2)),
            randint(0, int(cls.game.Y))
        )
        # Creamos una nueva serpiente
        new_snake = Snake(
            new_position,
            (randint(0, 255), randint(0, 255), randint(0, 255))
        )
        # Agregamos al jugador
        cls.game.players[str(cls.id)] = new_snake
        cls.game.clients[str(cls.id)] = client

        # Retornamos el ID
        cls.id += 1
        return str(cls.id-1)

    @classmethod
    def update_snake(cls, id: str, a: bool, d: bool, w: bool):
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
        cls.game.players[id].boosting = w
        cls.game.players[id].heading += (
            (d - a) * cls.game.players[id].TURN_SPEED
            * cls.game.delta_time
        )

app = Flask(__name__)

@app.route("/new_player", methods=["GET"])
def new_player():
    # Obtenemos el endpoint del nuevo jugador
    client = request.remote_addr
    port = request.values.get('port')
    endpoint = f'http://{client}:{port}'

    # Agregamos al jugador
    id = PythonIO.new_snake(endpoint)
    data = {'id': id}
    return data

@app.route("/update", methods=["POST"])
def update():
    # Endpoint para actualizar una serpiente
    id = request.values.get('id')
    a = request.values.get('press_a') == 'True'
    d = request.values.get('press_d') == 'True'
    w = request.values.get('press_w') == 'True'

    if id in PythonIO.game.players:
        PythonIO.update_snake(id, a, d, w)
        game_over = int(id not in PythonIO.game.players)
    else:
        game_over = 1

    return {'status': game_over}

if __name__ == "__main__":
    app.run(host="0.0.0.0")