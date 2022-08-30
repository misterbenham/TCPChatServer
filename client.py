import logging
import socket


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            logging.debug(f"Trying to connect to {self.host} : {self.port}...")
            self.ClientSocket.connect((self.host, self.port))
            logging.info(f"Successfully connected to {self.host} : {self.port}")
        except socket.error as e:
            logging.error(e)


if __name__ == '__main__':
    client = Client('127.0.0.1', 5555)
    client.connect_to_server()
