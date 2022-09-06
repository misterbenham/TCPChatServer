import database
import logging
import socket
import threading


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
ENCODE = "utf-8"


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
        self.clients = []
        self.db = database.Database()

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
                self.clients.append(client_socket)
                client_thread = threading.Thread(target=self.handle_client_connection,
                                                 args=(client_socket, ))
                client_thread.start()
            except socket.error as e:
                logging.error(e)

    def handle_client_connection(self, client_socket):
        """
        Function to handle clients connections.
        """
        while True:
            # receive data from client
            try:
                data = client_socket.recv(2048)
                message = data.decode(ENCODE)
                self.broadcast(message, client_socket)
                if message == 'QUIT':
                    index = self.clients.index(client_socket)
                    self.clients.remove(index)
                    client_socket.close()
                    break
                reply = f'Server: {message} : {client_socket.getpeername()}'
                client_socket.sendall(str.encode(reply))
                logging.info({reply})
                # break if connection is closed and remove client from list
                if not data:
                    logging.info(f' [CONNECTION CLOSED] : {client_socket}')
                    self.clients.remove(client_socket)
                    break
                client_socket.sendall(data)
                # send data to the client
            except socket.error as e:
                logging.error(e)
                break
        # connection closed
        client_socket.close()

    def broadcast(self, message, sender):
        """
        Function to broadcast messages to all connected clients,
        except the sender client.
        """
        for client_socket in self.clients:
            if client_socket is not sender:
                client_socket.send(message.encode(ENCODE))


if __name__ == '__main__':
    server = Server('127.0.0.1', 5555)
    server.run()
