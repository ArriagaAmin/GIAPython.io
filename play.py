# Utilidades
import argparse
from random import randint

# Juego
from src import Client


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Corre un ciente de python.io',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-n', '--no-interface',
        action='store_const',
        const=False, 
        default=True,
        help='No se muestra una interfaz.'
    )
    parser.add_argument(
        '-c', '--color',
        type=int,
        nargs=3,
        help='Permite establecer un color a la serpiente.',
        metavar='CHANNEL'
    )
    parser.add_argument(
        '-i', '--image',
        type=str,
        default='images/screenshot.png',
        help='Archivo donde se guardara la iamgen de cada frame.',
        metavar='FILENAME'
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

    # Iniciamos el cliente
    if args.color == None: color = (randint(0, 255), randint(0, 255), randint(0, 255))
    else: color = tuple(args.color)
    client = Client(
        args.server_ip, 
        args.server_port, 
        args.no_interface, 
        color,
        args.image
    )

    client.run()

