import json
import logging
import socket
import sys
import threading
import time

import user
import utility

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
ENCODE = "utf-8"
BUFFER_SIZE = 2048


class Client:
    """
    The client socket is created and attempts to connect to
    the server on the defined host IP and port.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        """
        Connects client socket to server IP and port. Spins up thread for client_send
        function and runs receive in a loop (listens for new messages from server).
        """
        try:
            logging.debug(f" Trying to connect to {self.host} : {self.port}...")
            self.client_socket.connect((self.host, self.port))
            logging.info(f" Successfully connected to {self.host} : {self.port}")
            recv_json_thread = threading.Thread(target=self.recv_json)
            recv_json_thread.start()
            self.welcome_menu()
        except socket.error as e:
            logging.error(e)

    def recv_json(self):
        while True:
            try:
                message = self.recv_message(self.client_socket)
                data = json.loads(message)
                if data["header"] == utility.LoginCommands.REGISTER.value:
                    print(data["body"])
                    self.client_register()
                    continue
                elif data["header"] == utility.LoginCommands.REGISTERED.value:
                    self.client_login()
                    continue
                elif data["header"] == utility.LoginCommands.LOGGED_IN.value:
                    menu_thread = threading.Thread(target=self.logged_in_menu, args=(data, ))
                    menu_thread.start()
                    continue
                elif data["header"] == utility.Responses.BROADCAST_MSG.value:
                    print(f"{data['addressee']} {':'} {data['body']}")
                    continue
                elif data["header"] == utility.LoggedInCommands.DIRECT_MESSAGE.value:
                    self.direct_messages(data)
                    continue
                elif data["header"] == utility.LoggedInCommands.PRINT_DM.value:
                    print(data["addressee"], data["body"])
                    continue
                elif data["header"] == utility.Responses.PRINT_FRIEND_REQUESTS.value:
                    print(data["body"])
                    continue
                elif data["header"] == utility.Responses.PRINT_FRIENDS_LIST.value:
                    print(data["body"])
                    continue
                elif data["header"] == utility.Responses.PRINT_STATUS_AWAY.value:
                    print(data["body"])
                    continue
                elif data["header"] == utility.Responses.ONLINE_NOTIFICATION.value:
                    print(f'{data["addressee"]} { "is ONLINE!"}')
                    continue
                elif data["header"] == utility.Responses.SUCCESS.value:
                    print(data["body"])
                    continue
                elif data["header"] == utility.Responses.ERROR.value:
                    print(data["body"])
                    continue
                elif data["header"] == utility.LoggedInCommands.QUIT.value:
                    sys.exit()
            except socket.error as e:
                logging.error(e)
                self.client_socket.close()
                break

    @staticmethod
    def recv_message(client_socket):
        """
        Receives messages from client sockets.
        """
        return client_socket.recv(BUFFER_SIZE).decode(ENCODE)

    @staticmethod
    def build_message(header, addressee, body, extra_info):
        x = {"header": header,
             "addressee": addressee,
             "body": body,
             "extra_info": extra_info}
        return x

    def client_send(self, msg_to_send):
        try:
            msg_packet = json.dumps(msg_to_send)
            self.client_socket.send(msg_packet.encode(ENCODE))
        except socket.error as e:
            logging.error(e)

    def welcome_menu(self):
        try:
            user_input = input("What would you like to do? Type 'login' or 'register': ")
            if user_input.lower() == utility.LoginCommands.LOGIN.value:
                self.client_login()
            elif user_input.lower() == utility.LoginCommands.REGISTER.value:
                self.client_register()
        except socket.error as e:
            logging.error(e)

    def client_login(self):
        uname = input("Enter username: ")
        pw = input("Enter password: ")
        msg_input = self.build_message(utility.LoginCommands.LOGIN.value, uname, pw, None)
        self.client_send(msg_input)
        return uname

    def client_register(self):
        uname = input("Enter new username: ")
        pw = input("Enter new password: ")
        pw2 = input("Re-enter password: ")
        if pw != pw2:
            logging.error("Passwords do not match. Please try again...")
        else:
            msg_input = self.build_message(utility.LoginCommands.REGISTER.value, uname, pw, None)
            self.client_send(msg_input)

    def logged_in_menu(self, data):
        try:
            for retry in range(3):
                user_input = input(f"Please select an option from the menu: \n"
                                   f"'broadcast' : Broadcast \n"
                                   f"'dm': Direct Message \n"
                                   f"'af': Add Friend \n"
                                   f"'fr': View Friend Requests \n"
                                   f"'vf': View Friends \n"
                                   f"'ssa' : Set Status Away \n"
                                   f"'help': Help \n"
                                   f"'quit' : Quit \n")
                if user_input == utility.LoggedInCommands.BROADCAST.value:
                    self.broadcast_messages(data)
                    break
                elif user_input == utility.LoggedInCommands.AUTHENTICATE_DIRECT_MESSAGE.value:
                    recipient = input("Who would you like to send a DM to?:\n")
                    self.dm_recipient(data, recipient)
                    break
                elif user_input == utility.LoggedInCommands.ADD_FRIEND.value:
                    recipient = input("Type the username of the friend to add:\n")
                    self.add_friend(data, recipient)
                    break
                elif user_input == utility.LoggedInCommands.VIEW_FRIEND_REQUESTS.value:
                    msg_input = self.build_message(utility.LoggedInCommands.VIEW_FRIEND_REQUESTS.value,
                                                   data["addressee"], None, None)
                    self.client_send(msg_input)
                    break
                elif user_input == utility.LoggedInCommands.VIEW_FRIENDS.value:
                    msg_input = self.build_message(utility.LoggedInCommands.VIEW_FRIENDS.value, data["addressee"],
                                                   None, None)
                    self.client_send(msg_input)
                    break
                elif user_input == utility.LoggedInCommands.SET_STATUS_AWAY.value:
                    msg_input = self.build_message(utility.LoggedInCommands.SET_STATUS_AWAY.value, data["addressee"],
                                                   "AWAY", None)
                    self.client_send(msg_input)
                    break
                elif user_input == utility.LoggedInCommands.HELP.value:
                    msg_input = self.build_message(utility.LoggedInCommands.HELP.value, None, None, None)
                    self.client_send(msg_input)
                    break
                elif user_input == utility.LoggedInCommands.QUIT.value:
                    msg_input = self.build_message(utility.LoggedInCommands.QUIT.value, data["addressee"],
                                                   None, "OFFLINE")
                    self.client_send(msg_input)
                    break
                else:
                    logging.error("Invalid selection- Please try again...")
            else:
                logging.error("You keep making invalid choices...")
        except socket.error as e:
            logging.error(e)

    def broadcast_messages(self, data):
        while True:
            try:
                msg_body = input(">")
                msg_input = self.build_message(utility.LoggedInCommands.BROADCAST.value, data["addressee"],
                                               msg_body, None)
                if msg_body == "QUIT":
                    break
                else:
                    self.client_send(msg_input)
                    continue
            except socket.error as e:
                logging.error(e)

    def dm_recipient(self, data, recipient):
        requester = data["addressee"]
        try:
            msg_input = self.build_message(utility.LoggedInCommands.AUTHENTICATE_DIRECT_MESSAGE.value, recipient,
                                           requester, None)
            self.client_send(msg_input)
        except socket.error as e:
            logging.error(e)

    def direct_messages(self, data):
        requester = data["body"]
        previous_messages = data["extra_info"]
        for i in previous_messages:
            print(i)
        while True:
            try:
                msg_body = input(">")
                msg_input = self.build_message(utility.LoggedInCommands.DIRECT_MESSAGE.value, data["addressee"],
                                               msg_body, requester)
                if msg_body == 'QUIT':
                    break
                else:
                    self.client_send(msg_input)
                    continue
            except socket.error as e:
                logging.error(e)

    def add_friend(self, data, recipient):
        msg_input = self.build_message(utility.LoggedInCommands.ADD_FRIEND.value, data["addressee"],
                                       recipient, None)
        self.client_send(msg_input)


if __name__ == '__main__':
    client = Client('127.0.0.1', 5555)
    client.run()
