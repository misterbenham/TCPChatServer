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

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.new_connections = []

    def run(self):
        """
        Creates the listening socket.
        Binds server to host IP and port.
        """
        logging.info(" Creating socket...")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(" Socket created")
        try:
            logging.debug(f" Binding server socket to {self.host} : {self.port}...")
            server_socket.bind((self.host, self.port))
            logging.info(f" Server socket bound to {self.host} : {self.port}")
        except socket.error as e:
            logging.error(e)
        logging.info(f" Server is listening on port {self.port}...")
        server_socket.listen()

        while True:
            # Accept new connection
            try:
                sc, sock_name = server_socket.accept()
                logging.info(f" Accepted a new connection from {sc.getpeername()}")
                new_conn = Connection()
                new_conn.start_connection(sc, sock_name)
                self.new_connections.append(new_conn)
            except socket.error as e:
                logging.error(e)


class Connection:
    """
    Starts the client connection and implements
    send/receive data functionality.
    """
    def __init__(self):
        self.client_socket = socket.socket()
        self.client_address = tuple()

    def start_connection(self, sock: socket, addr: (str, int)):
        self.client_socket = sock
        self.client_address = addr


if __name__ == '__main__':
    server = Server('127.0.0.1', 5555)
    server.run()
