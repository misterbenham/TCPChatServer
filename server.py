import logging
import socket

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class Server:
    """
    Supports management of server connections.
    Attributes:
        host (str): The IP address of the listening socket.
        port (int): The port number of the listening socket.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def run(self):
        """
        Creates the listening socket.
        Binds server to host IP and port.
        """
        logging.info("Creating socket...")
        ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info("Socket created")
        try:
            logging.debug(f"Binding server socket to {self.host} : {self.port}...")
            ServerSocket.bind((self.host, self.port))
            logging.info(f"Server socket bound to {self.host} : {self.port}")
        except socket.error as e:
            logging.error(e)
        logging.info(f"Server is listening on port {self.port}...")
        ServerSocket.listen()


if __name__ == '__main__':
    server = Server('127.0.0.1', 5555)
    server.run()
