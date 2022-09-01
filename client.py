import logging
import socket


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class Client:
    """
    The client socket is created and attempts to connect to
    the server on the defined host IP and port.
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):

        try:
            logging.debug(f" Trying to connect to {self.host} : {self.port}...")
            self.client_socket.connect((self.host, self.port))
            logging.info(f" Successfully connected to {self.host} : {self.port}")
            # Testing code below
            while True:
                msg = input("Enter a message: ")
                self.client_socket.sendall(str.encode(msg))
        except socket.error as e:
            logging.error(e)


if __name__ == '__main__':
    client = Client('127.0.0.1', 5555)
    client.connect_to_server()
