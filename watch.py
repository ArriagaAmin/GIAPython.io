# Utilidades
import argparse

# Juego
from src import Watcher

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Corre un observador del mapa completo de python.io',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'server_ip',
        type=str,
        help='Server IP.',
        metavar='IP',
    )
    parser.add_argument(
        'server_port',
        type=int,
        help='Server port.',
        metavar='PORT',
    )

    args = parser.parse_args()

    # Iniciamos el observador
    watcher = Watcher(args.server_ip, args.server_port)
    watcher.run()

