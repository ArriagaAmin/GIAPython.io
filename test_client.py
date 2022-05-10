from src.server_client import *

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
PORT = 12345  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        msg = input('> ')
        send_msg(s, bytearray(msg, 'utf-8'))