from src import Server, SERVER_IP, PORT

if __name__ == '__main__':
    server = Server(SERVER_IP, PORT)
    server.run()