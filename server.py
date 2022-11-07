import hashlib

import bcrypt
import json
import logging
import socket
import threading

import database
import user
import utility

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
ENCODE = "utf-8"
BUFFER_SIZE = 2048


class Server:
    """
    Supports management of server connections.
    Attributes:
        host (str): The IP address of the listening socket.
        port (int): The port number of the listening socket.
    """

    @staticmethod
    def recv_message(client_socket):
        """
        Receives messages from client sockets.
        """
        return client_socket.recv(BUFFER_SIZE).decode(ENCODE)

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.clients = {}
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
        self.db = database.Database()
        self.db.create_users_table()
        self.db.create_friends_table()
        server_socket.listen()
        while True:
            self.accept_connection(server_socket)

    def accept_connection(self, server_socket):
        """
        Accepts new client connections and spins up a thread for each new connection.
        Appends client socket to list of clients[].
        """
        try:
            client_socket, client_address = server_socket.accept()
            logging.info(f" Accepted a new connection from {client_socket.getpeername()}")
            client_thread = threading.Thread(target=self.handle_client_connection,
                                             args=(client_socket,))
            client_thread.start()
        except socket.error as e:
            logging.error(e)

    def handle_client_connection(self, client_socket):
        """
        Function to handle clients connections.
        Receives data and asks client to either login (1) or register (2).
        """
        while True:
            # receive data from client
            try:
                message = self.recv_message(client_socket)
                data = json.loads(message)
                if data["header"] == utility.LoginCommands.LOGIN.value:
                    self.login(client_socket, data)
                    continue
                elif data["header"] == utility.LoginCommands.REGISTER.value:
                    self.register(client_socket, data)
                    continue
                elif data["header"] == utility.LoggedInCommands.BROADCAST.value:
                    if data["body"] == "QUIT":
                        client_socket.close()
                        continue
                    else:
                        print("{} : {}".format(data["addressee"], data["body"]))
                        self.broadcast(client_socket, data)
                        continue
                elif data["header"] == utility.LoggedInCommands.AUTHENTICATE_DIRECT_MESSAGE.value:
                    self.authenticate_direct_message(client_socket, data)
                    continue
                elif data["header"] == utility.LoggedInCommands.DIRECT_MESSAGE.value:
                    self.direct_message(client_socket, data)
                    continue
                elif data["header"] == utility.LoggedInCommands.ADD_FRIEND.value:
                    self.friend_request(client_socket, data)
                    continue
                elif data["header"] == utility.LoggedInCommands.VIEW_FRIEND_REQUESTS.value:
                    self.view_friend_requests(client_socket, data)
                    continue
                elif data["header"] == utility.LoggedInCommands.VIEW_FRIENDS.value:
                    self.view_friends(client_socket, data)
                    continue
                elif data["header"] == utility.LoggedInCommands.SET_STATUS_AWAY.value:
                    self.set_status(client_socket, data)
                    continue
                elif data["header"] == utility.LoggedInCommands.QUIT.value:
                    self.quit(client_socket, data)
                    break
            except socket.error as e:
                client_socket.close()
                logging.error(e)
                break

    def login(self, client_socket, data):
        """
        Asks user to enter username. Searches DB for username. If valid, requests password to login
        and sends user to open_chat_room(). If username is invalid (not in DB), the user must
        try again.
        """
        while True:
            try:
                username = data["addressee"]
                pw = data["body"].encode(ENCODE)
                user_in_db = self.db.find_username_in_db(username)
                if not user_in_db:
                    self.send_message(client_socket, "Username not found. Please enter username: ")
                else:
                    if bcrypt.checkpw(pw, user_in_db[0][2]):
                        self.clients[username] = client_socket
                        self.db.set_status("ONLINE", username)
                        response = self.build_message(utility.LoginCommands.LOGGED_IN.value, username,
                                                      utility.Responses.SUCCESS.value, None)
                        self.server_send(client_socket, response)

                        friends_list = self.db.view_friends(username)
                        print(friends_list)
                        online_notification = self.build_message(utility.Responses.ONLINE_NOTIFICATION.value,
                                                                 username, None, None)
                        for username, client_socket in self.clients.items():
                            if username in friends_list:
                                self.server_send(client_socket, online_notification)
                        break
                    else:
                        self.send_message(client_socket, "Incorrect credentials. Please enter username: ")
            except socket.error as e:
                client_socket.close()
                logging.error(e)
                break

    def register(self, client_socket, data):
        """
        Asks user for new username. Searches DB for username. If already exists, notifies the user that
        they must use another. Asks for password twice. Checks passwords match. Creates user and adds
        them to DB. Sends user to login with new credentials.
        """
        while True:
            try:
                username = data["addressee"]
                if not self.db.fetch_all_users_data(username):
                    response = self.build_message(utility.LoginCommands.REGISTER.value, username,
                                                  "Username already registered, please choose another...", None)
                    self.server_send(client_socket, response)
                    break
                else:
                    pw = data["body"].encode(ENCODE)
                    salt = bcrypt.gensalt()
                    hashed = bcrypt.hashpw(pw, salt)
                    self.db.insert_username_and_password(username, hashed)
                    response = self.build_message(utility.LoginCommands.REGISTERED.value, None,
                                                  utility.Responses.SUCCESS.value, None)
                    self.server_send(client_socket, response)
            except socket.error as e:
                logging.error(e)
                client_socket.close()
                self.clients.pop(client_socket)
            break

    def broadcast(self, client_socket, data):
        """
        Function to broadcast messages to all connected clients,
        except the sender client.
        """
        try:
            data["header"] = None
            username = data["addressee"]
            user_msg = data["body"]
            data["extra_info"] = None
            response = self.build_message(utility.Responses.BROADCAST_MSG.value, username, user_msg, None)
            for username, client_socket in self.clients.items():
                self.server_send(client_socket, response)
        except socket.error as e:
            logging.error(e)
            client_socket.close()
            del self.clients[client_socket]

    def authenticate_direct_message(self, client_socket, data):
        if data["addressee"] not in self.clients:
            response = self.build_message(utility.Responses.ERROR.value, None,
                                          "Username not found", None)
            self.server_send(client_socket, response)
        else:
            response = self.build_message(utility.LoggedInCommands.DIRECT_MESSAGE.value, data["addressee"],
                                          None, None)
            self.server_send(client_socket, response)

    def direct_message(self, client_socket, data):
        data["header"] = None
        username = data["addressee"]
        msg = data["body"]
        response = self.build_message(utility.LoggedInCommands.PRINT_DM.value, username, msg, None)
        client_socket = self.clients[username]
        self.server_send(client_socket, response)

    def friend_request(self, client_socket, data):
        requester = data["addressee"]
        recipient = data["body"]
        if not self.db.fetch_all_users_data(recipient):
            response = self.build_message(utility.Responses.ERROR.value, None, "Username not found...", None)
            self.server_send(client_socket, response)
        elif self.db.find_friendship_status(requester, recipient) == "SENT":
            self.db.insert_friend_relationship(requester, recipient)
            response = self.build_message(utility.Responses.SUCCESS.value, None, "Friend added", None)
            self.server_send(client_socket, response)
        else:
            self.db.insert_friend_request(requester, recipient)
            response = self.build_message(utility.Responses.SUCCESS.value, None,
                                          "Friend request sent", None)
            self.server_send(client_socket, response)

    def view_friend_requests(self, client_socket, data):
        requester = data["addressee"]
        friends_list = self.db.view_friend_requests(requester)
        response = self.build_message(utility.Responses.PRINT_FRIEND_REQUESTS.value, requester,
                                      "\n".join([x[0] for x in friends_list]), None)
        self.server_send(client_socket, response)

    def view_friends(self, client_socket, data):
        requester = data["addressee"]
        friends_list = self.db.view_friends_and_status(requester)
        response = self.build_message(utility.Responses.PRINT_FRIENDS_LIST.value, requester,
                                      "\n".join([x[0] + " : " + x[1] for x in friends_list]), None)
        self.server_send(client_socket, response)

    def set_status(self, client_socket, data):
        username = data["addressee"]
        status = data["body"]
        self.db.set_status(status, username)
        response = self.build_message(utility.Responses.PRINT_STATUS_AWAY.value, username, "Status: AWAY", None)
        self.server_send(client_socket, response)

    @staticmethod
    def build_message(header, addressee, body, extra_info):
        x = {"header": header,
             "addressee": addressee,
             "body": body,
             "extra_info": extra_info}
        return x

    def server_send(self, client_socket, msg_to_send):
        try:
            msg_packet = json.dumps(msg_to_send)
            self.send_message(client_socket, msg_packet)
        except socket.error as e:
            logging.error(e)

    def quit(self, client_socket, data):
        try:
            username = data["addressee"]
            status = "OFFLINE"
            self.db.set_status(status, username)
            response = self.build_message(utility.LoggedInCommands.QUIT.value, None, None, None)
            self.server_send(client_socket, response)
            self.clients.pop(username)
        except socket.error as e:
            logging.error(e)

    @staticmethod
    def send_message(client_socket, msg):
        """
        Sends message (from server) to client socket.
        """
        client_socket.send(msg.encode(ENCODE))


if __name__ == '__main__':
    server = Server('0.0.0.0', 5555)
    server.run()
