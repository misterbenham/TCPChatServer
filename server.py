import logging
import socket
import threading

import database
import user


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
        self.db = None

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
        self.db = database.Database()
        self.db.create_users_table()
        while True:
            self.accept_connection(server_socket)

    def accept_connection(self, server_socket):
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
        self.send_message(client_socket, "Welcome to the chat server! Press 1 to login or 2 to register: ")
        while True:
            # receive data from client
            try:
                data = client_socket.recv(2048)
                message = data.decode(ENCODE)
                if message == "1":
                    self.login(client_socket)
                if message == "2":
                    if self.register(client_socket):
                        self.login(client_socket)
            except socket.error as e:
                logging.error(e)
                break
        # connection closed
        client_socket.close()

    def open_chat_room(self, client_socket):
        while True:
            data = client_socket.recv(2048)
            message = data.decode(ENCODE)
            self.broadcast(message, client_socket)
            logging.info(f" {client_socket.getpeername()}" + ": " + message)
            if message == 'QUIT':
                index = self.clients.index(client_socket)
                self.clients.remove(index)
                client_socket.close()
                break
            if not data:
                logging.info(f' [CONNECTION CLOSED] : {client_socket}')
                self.clients.remove(client_socket)
                break

    def login(self, client_socket):
        self.send_message(client_socket, "Enter username: ")
        while True:
            data = client_socket.recv(2048)
            username = data.decode(ENCODE)
            if self.db.find_username_in_db(username):
                self.send_message(client_socket, "Enter password: ")
                data = client_socket.recv(2048)
                pw = data.decode(ENCODE)
                if self.db.find_user_pw_in_db(username, pw):
                    self.send_message(client_socket, f"Credentials match. Welcome {username}!")
                    self.open_chat_room(client_socket)
                    break
                else:
                    self.send_message(client_socket, "Incorrect credentials. Please enter username: ")
            else:
                self.send_message(client_socket, "Username not found. Please enter username: ")

    def register(self, client_socket):
        self.send_message(client_socket, "Enter new username: ")
        while True:
            data = client_socket.recv(2048)
            username = data.decode(ENCODE)
            if not self.db.fetch_all_users_data(username):
                self.send_message(client_socket, "Username already registered, please choose another: ")
            else:
                while True:
                    self.send_message(client_socket, "Enter password: ")
                    data = client_socket.recv(2048)
                    pw = data.decode(ENCODE)
                    self.send_message(client_socket, "Re-enter password: ")
                    data = client_socket.recv(2048)
                    pw2 = data.decode(ENCODE)
                    if pw == pw2:
                        self.db.insert_username_and_password(username, pw)
                        self.send_message(client_socket, "Registration successful! Please login below...")
                        return True
                    else:
                        self.send_message(client_socket, "Passwords do not match. Please try again...")

    def send_message(self, client_socket, msg):
        client_socket.send(msg.encode(ENCODE))

    def broadcast(self, message, sender):
        """
        Function to broadcast messages to all connected clients,
        except the sender client.
        """
        user_msg = f"{sender.getpeername()}: " + message
        for client_socket in self.clients:
            if client_socket is not sender:
                client_socket.send(user_msg.encode(ENCODE))


if __name__ == '__main__':
    server = Server('127.0.0.1', 5555)
    server.run()
