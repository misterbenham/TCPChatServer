import logging
import socket
import threading


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
                client_socket, client_address = server_socket.accept()
                logging.info(f" Accepted a new connection from {client_socket.getpeername()}")
                self.new_connections.append((client_socket, client_address))
                new_client_thread = threading.Thread(target=self.handle_client_connection(client_socket, client_address))
                new_client_thread.start()
            except socket.error as e:
                logging.error(e)

    def handle_client_connection(self, client_socket, client_address):
        while True:
            # receive data from client
            data = client_socket.recv(2048)
            message = data.decode('utf-8')
            if message == 'QUIT':
                logging.info(f'{client_socket.getpeername()} has left the chat.')
                break
            reply = f'Server: {message}'
            client_socket.sendall(str.encode(reply))
            logging.info({reply})
            # break if connection is closed and remove client from list
            if not data:
                logging.info(f' [CONNECTION CLOSED] : {client_socket}')
                self.new_connections.remove((client_socket, client_address))
                break
            client_socket.sendall(data)
            # send data to the client
            # connection closed
        client_socket.close()


if __name__ == '__main__':
    server = Server('127.0.0.1', 5555)
    server.run()
