import json
import logging
import socket
import sys
import threading

import utility

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
ENCODE = "utf-8"
BUFFER_SIZE = 2048


class Client:
    """
    The client socket is created and attempts to connect to
    the server on the defined host IP and port.

    :param: host (str): IP address used to connect to server.
    :param: port (int): PORT number used to connect to server.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        """
        Connects client socket to server IP and port. Spins up thread for client_send
        function and runs receive in a loop (listens for new messages from server).
        Starts the method for welcome menu().
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
        """
        Method receives 'message' from the server and loads message json as 'data'.
        Runs separate functions depending on the header of the json data.
        Method run in a while true loop, so it constantly receives new data from server.
        """
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
                elif data["header"] == utility.Responses.TIC_TAC_TOE_REQUEST.value:
                    self.tic_tac_toe_request(data)
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
        Receives messages from client sockets (2048 bytes of data). Decodes using 'UTF-8'.
        """
        return client_socket.recv(BUFFER_SIZE).decode(ENCODE)

    @staticmethod
    def build_message(header, addressee, body, extra_info):
        """
       Static method takes in arguments and assigns them to a dictionary that it returns.

       :param header: Variable to store header enum.
       :param addressee: Variable to store usernames.
       :param body: Variable to store messages.
       :param extra_info: Variable to store an extra info required.
       """
        x = {"header": header,
             "addressee": addressee,
             "body": body,
             "extra_info": extra_info}
        return x

    def client_send(self, msg_to_send):
        """
        Method takes the message dictionary and dumps into json message packet.
        Json message packet is sent to the client.

        :param client_socket: Socket of connected client.
        :param msg_to_send: Parameter for (build_message) dictionary to be sent.
        """
        try:
            msg_packet = json.dumps(msg_to_send)
            self.client_socket.send(msg_packet.encode(ENCODE))
        except socket.error as e:
            logging.error(e)

    def welcome_menu(self):
        """
        Method runs once the main 'run' function starts. Asks the users whether they want to login or register.
        Runs function for login or registration accordingly.
        """
        try:
            user_input = input("What would you like to do? Type 'login' or 'register': ")
            if user_input.lower() == utility.LoginCommands.LOGIN.value:
                self.client_login()
            elif user_input.lower() == utility.LoginCommands.REGISTER.value:
                self.client_register()
        except socket.error as e:
            logging.error(e)

    def client_login(self):
        """
        Asks user for their username and password to be sent to server along with LOGIN header, for login validation.
        """
        uname = input("Enter username: ")
        pw = input("Enter password: ")
        msg_input = self.build_message(utility.LoginCommands.LOGIN.value, uname, pw, None)
        self.client_send(msg_input)
        return uname

    def client_register(self):
        """
        Asks user for new username and password. Ensures both password entries match. Sends username and password
        inputs to server along with REGISTER header.
        """
        uname = input("Enter new username: ")
        pw = input("Enter new password: ")
        pw2 = input("Re-enter password: ")
        if pw != pw2:
            logging.error("Passwords do not match. Please try again...")
        else:
            msg_input = self.build_message(utility.LoginCommands.REGISTER.value, uname, pw, None)
            self.client_send(msg_input)

    def logged_in_menu(self, data):
        """
        Function runs once server has authenticated and logged in client. Menu displays a list of options that the
        client can enter and runs separate functions accordingly.

        :param data: Client username (str).
        """
        try:
            for retry in range(3):
                user_input = input(f"Please select an option from the menu: \n"
                                   f"'broadcast' : Broadcast \n"
                                   f"'dm': Direct Message \n"
                                   f"'af': Add Friend \n"
                                   f"'fr': View Friend Requests \n"
                                   f"'vf': View Friends \n"
                                   f"'ttt' Tic Tac Toe \n"
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
                elif user_input == utility.LoggedInCommands.AUTH_TIC_TAC_TOE.value:
                    recipient = input("Who would you like to play with?:\n")
                    self.send_tic_tac_toe_request(data, recipient)
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
        """
        Function runs when client requests to broadcast multiple messages to all connected clients. The user
        enters a while true loop that constantly allows user input and sends every client message to the server
        with the header "BROADCAST". The user exits the loop if and when they type in 'QUIT'.
        :param data: Client username.
        """
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
        """
        Function runs when client requests to direct message a specific user and enter a private chat room with
        the requested individual. The function sends the header 'AUTHENTICATE_DIRECT_MESSAGE' to the server as
        a pre-check to ensure that the user exists, the two users are friends and other checks take place.
        :param data: client username
        :param recipient: recipient username
        """
        requester = data["addressee"]
        try:
            msg_input = self.build_message(utility.LoggedInCommands.AUTHENTICATE_DIRECT_MESSAGE.value, recipient,
                                           requester, None)
            self.client_send(msg_input)
        except socket.error as e:
            logging.error(e)

    def direct_messages(self, data):
        """
        Function runs once the server has authenticated the request to direct message. A list of previous messages
        (held in data parameter) has already been fetched by the server. The list is reversed to correct timeline order
        and printed. The client then enters a while true loop, enabling them to constantly direct message the recipient
        until the client inputs 'QUIT'. The messages are sent back to the server with the header 'DIRECT_MESSAGE' along
        with the recipient to be distributed.
        :param data: requester username, list of previous messages exchanged between clients.
        """
        requester = data["body"]
        previous_messages = data["extra_info"]
        previous_messages.reverse()
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
        """
        Function runs when the client requests to add a user as a friend. The function send a message to the server
        with the header 'ADD_FRIEND' and the recipients' username to be processed by the server.
        :param data: Client username.
        :param recipient: Recipient username.
        """
        msg_input = self.build_message(utility.LoggedInCommands.ADD_FRIEND.value, data["addressee"],
                                       recipient, None)
        self.client_send(msg_input)

    def send_tic_tac_toe_request(self, data, recipient):
        msg_input = self.build_message(utility.LoggedInCommands.AUTH_TIC_TAC_TOE.value, data["addressee"],
                                       recipient, None)
        self.client_send(msg_input)

    def tic_tac_toe_request(self, data):
        requester = data["extra_info"]
        recipient = data["addressee"]
        print(data["body"])
        try:
            for retry in range(3):
                req_response = input('Press 1 for Yes, 2 for No \n')
                if req_response == '1':
                    msg_input = self.build_message(utility.Responses.TIC_TAC_TOE_CONFIRM.value, recipient,
                                                   requester, None)
                    self.client_send(msg_input)
                elif req_response == '2':
                    msg_input = self.build_message(utility.Responses.TIC_TAC_TOE_DENY.value, recipient,
                                                   requester, None)
                    self.client_send(msg_input)
                else:
                    logging.error("Invalid selection- Please try again...")
            else:
                logging.error("You keep making invalid choices...")
                msg_input = self.build_message(utility.Responses.TIC_TAC_TOE_DENY.value, recipient,
                                               requester, None)
                self.client_send(msg_input)
        except socket.error as e:
            logging.error(e)


if __name__ == '__main__':
    """
    Instantiates the Client class with host (IP) and port numbers.
    Runs the Client run function.
    """
    client = Client('127.0.0.1', 5555)
    client.run()
