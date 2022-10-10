import json
import logging
import socket
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
                if data["header"] == utility.LoginCommands.REGISTERED.value:
                    self.client_login()
                    continue
                elif data["header"] == utility.LoginCommands.LOGGED_IN.value:
                    menu_thread = threading.Thread(target=self.logged_in_menu, args=(data, ))
                    menu_thread.start()
                    continue
                elif data["header"] == utility.Responses.BROADCAST_MSG.value:
                    print(data["addressee"], data["body"])
                    continue
                elif data["header"] == utility.Responses.ERROR.value:
                    print(data["body"])
                    continue
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
            if user_input == utility.LoginCommands.LOGIN.value:
                self.client_login()
            elif user_input == utility.LoginCommands.REGISTER.value:
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
                                   f"1: Broadcast \n"
                                   f"2: Direct Message \n"
                                   f"3: Help \n"
                                   f"4: Quit \n")
                if user_input == utility.LoggedInCommands.BROADCAST.value:
                    self.broadcast_messages(data)
                    break
                elif user_input == utility.LoggedInCommands.DIRECT_MESSAGE.value:
                    msg_input = self.build_message(utility.LoggedInCommands.DIRECT_MESSAGE.value, None, None, None)
                    self.client_send(msg_input)
                    break
                elif user_input == utility.LoggedInCommands.HELP.value:
                    msg_input = self.build_message(utility.LoggedInCommands.HELP.value, None, None, None)
                    self.client_send(msg_input)
                    break
                elif user_input == utility.LoggedInCommands.QUIT.value:
                    msg_input = self.build_message(utility.LoggedInCommands.QUIT.value, None, None, None)
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
                # possible recv thread. Kill once broken out of while true.
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


if __name__ == '__main__':
    client = Client('127.0.0.1', 5555)
    client.run()
