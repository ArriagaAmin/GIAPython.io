import json
from typing import Tuple

# Cargamos las variables de entorno
with open('.env.json', 'r') as f:
    ENV = json.load(f)
    
X          : int = ENV['WORLD_X']
Y          : int = ENV['WORLD_Y']
CAMERA_X   : int = ENV['CAMERA_X']
CAMERA_Y   : int = ENV['CAMERA_Y']
RATE       : int = ENV['RATE']
DELTA_TIME : float = ENV['DELTA_TIME']
BG_COLOR   : Tuple[int, int, int] = tuple(ENV['BG_COLOR'])

MAX_BOOST_COUNT : int = ENV['MAX_BOOST_COUNT']
MIN_BOOST_LEN   : int = ENV['MIN_BOOST_LEN']
SPEED           : float = ENV['SPEED']
TURN_SPEED      : float = ENV['TURN_SPEED']
BOOST_SPEED     : float = ENV['BOOST_SPEED']

APPLE_RADIUS     : int = ENV['APPLE_RADIUS']
MAX_APPLES       : int = ENV['MAX_APPLES']
APPLE_TIME_SPAWM : int = ENV['APPLE_TIME_SPAWN']
INITIAL_APPLES   : int = ENV['INITIAL_APPLES']
SEGS_BY_APPLE    : int = ENV['SEGS_BY_APPLE']
APPLE_COLOR      : Tuple[int, int, int] = tuple(ENV['APPLE_COLOR'])

TILE_LEN : int = ENV['TILE_LEN']

SERVER_IP : str = ENV['SERVER_IP']
PORT      : int = ENV['SERVER_PORT']
CAPTION   : str = ENV['CAPTION']

