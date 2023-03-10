import bcrypt
import json
import logging
import socket
import threading

import database
import ttt_game
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
        clients (dict): a client dictionary that stores client socket address and username.
        db (database): Instance attribute of the database class.
    """

    @staticmethod
    def recv_message(client_socket):
        """
        Receives messages from client sockets.
        Receives 2048 bytes of data and decodes using 'utf-8'.
        """
        return client_socket.recv(BUFFER_SIZE).decode(ENCODE)

    def __init__(self, host: str, port: int):
        self.recipient = None
        self.requester = None
        self.host = host
        self.port = port
        self.clients = {}
        self.db = None

    def run(self):
        """
        Creates the listening socket.
        Binds server to host IP and port.
        Starts server socket listening for client sockets.
        Creates an instance of the database and all tables.
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
        server_socket.listen()
        while True:
            self.accept_connection(server_socket)

    def accept_connection(self, server_socket):
        """
        Accepts new client connections and spins up a thread for each new connection.
        Passes the client_socket as an argument to the thread.
        Appends client socket to dictionary of clients{}.

        :param server_socket: Socket address of server
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
        Threaded function for each new connected client. Receives 'message' from the client sockets as json
        and loads as 'data'. The header of the data is read and separate functions are run accordingly.

        :param client_socket: Socket address of connected client.
        """
        while True:
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
                    self.direct_message(data)
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
                elif data["header"] == utility.LoggedInCommands.AUTH_TIC_TAC_TOE.value:
                    self.authenticate_tic_tac_toe(client_socket, data)
                    continue
                elif data["header"] == utility.LoggedInCommands.VIEW_TIC_TAC_TOE_REQUESTS.value:
                    self.view_ttt_requests(client_socket, data)
                    continue
                elif data["header"] == utility.Responses.TIC_TAC_TOE_CONFIRM.value:
                    requester = data["addressee"]
                    recipient = data["body"]
                    self.db.insert_ttt_game_response(requester, recipient, "CONFIRM")
                    self.start_game(data)
                    continue
                elif data["header"] == utility.Responses.PLAY_TIC_TAC_TOE.value:
                    self.play_tic_tac_toe(data)
                    continue
                elif data["header"] == utility.Responses.TIC_TAC_TOE_ERROR.value:
                    self.play_tic_tac_toe(data)
                    continue
                elif data["header"] == utility.Responses.TIC_TAC_TOE_DENY.value:
                    requester = data["addressee"]
                    recipient = data["body"]
                    self.db.insert_ttt_game_response(requester, recipient, "DENY")
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
        Function run when client requests to login. Checks the db for client username. If not found, responds
        with 'username not found'. If found, checks the username against given password in the db. If not a
        match, responds to client with 'incorrect password'. If correct responds to client with LOGGED_IN header
        allowing client to proceed to menu. Sets users status to 'ONLINE' IN DB. Also searches and fetched friend
        list of client and sends all friends a notification that the connected client is now online. Adds client
        username to the 'clients' dictionary with their client socket.

        :param client_socket: Socket of connected client
        :param data: LOGIN header, client username, given password
        """
        while True:
            try:
                username = data["addressee"]
                pw = data["body"].encode(ENCODE)
                user_in_db = self.db.find_username_in_db(username)
                if not user_in_db:
                    response = self.build_message(utility.LoginCommands.LOGIN.value, None,
                                                  "Username not found. Please enter username: ", None)
                    self.server_send(client_socket, response)
                    break
                else:
                    if bcrypt.checkpw(pw, user_in_db[0][2]):
                        self.clients[username] = client_socket
                        self.db.set_status("ONLINE", username)
                        response = self.build_message(utility.LoginCommands.LOGGED_IN.value, username,
                                                      utility.Responses.SUCCESS.value, None)
                        self.server_send(client_socket, response)

                        friends_list = self.db.view_friends_and_status(username)
                        friends_list_usernames = []
                        for i in friends_list:
                            friends_list_usernames.append(i[0])
                        online_notification = self.build_message(utility.Responses.ONLINE_NOTIFICATION.value,
                                                                 username, None, None)
                        for username, client_socket in self.clients.items():
                            if username in friends_list_usernames:
                                self.server_send(client_socket, online_notification)
                        break
                    else:
                        response = self.build_message(utility.LoginCommands.LOGIN.value, None,
                                                      "Incorrect credentials. Please try again...", None)
                        self.server_send(client_socket, response)
                        break
            except socket.error as e:
                client_socket.close()
                logging.error(e)
                break

    def register(self, client_socket, data):
        """
        Function run when client requests to register with new account. Checks the db against the requested
        username given. If an exact username is found, a response is sent to client stating username is already in use
        and to choose another. Else, the passwrd is hashed using bcrypt (and salted) and username/password are inserted
        into the db. Server responds to client with 'REGISTERED' header, allowing the client to login.

        :param client_socket: Socket of connected client.
        :param data: REGISTER header, requested username (str), requested password (str).
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
                    break
            except socket.error as e:
                logging.error(e)
                client_socket.close()
                self.clients.pop(client_socket)

    def broadcast(self, client_socket, data):
        """
        Function run on request of the client. Responds with message to all clients connected to client dictionary.

        :param client_socket: Socket of connected client.
        :param data: BROADCAST Header, client username (str), client message to broadcast (str).
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
        """
        Searches the given username against the db user table. If found, responds to the client
        allowing them to direct message the recipient. Also fetches all previous messages between client and
        recipient from the db messages table. Messages list is sent as a response to client.
        If not found in db, responds to the client with a message 'username' not found.

        :param client_socket: Connected client socket address
        :param data: header (enum), client username (str), recipient username (str)
        """
        requester = data["body"]
        recipient = data["addressee"]
        if recipient not in self.clients:
            response = self.build_message(utility.Responses.ERROR.value, None,
                                          "Username not found", None)
            self.server_send(client_socket, response)
        else:
            previous_messages = self.db.fetch_messages(requester, recipient)
            response = self.build_message(utility.LoggedInCommands.DIRECT_MESSAGE.value, recipient,
                                          requester, previous_messages)
            self.server_send(client_socket, response)

    def direct_message(self, data):
        """
        Function sends messages from client to recipient and inserts messages into db.

        :param client_socket: Socket of connected client.
        :param data: requester username (str), recipient username (str), message to send (str)
        """
        requester = data["extra_info"]
        username = data["addressee"]
        msg = data["body"]
        response = self.build_message(utility.LoggedInCommands.PRINT_DM.value, username, msg, None)
        self.db.insert_message(requester, username, msg)
        self.server_send(self.clients[username], response)

    def friend_request(self, client_socket, data):
        """
        Function run when user requests to add another user as a friend. Recipient username is checked against the
        db to ensure the user exists. If exists, inserts status 'SENT' to friends table in db. If status is already
        'SENT', updates status to 'FRIENDS' and responds to the client accordingly (either friend request sent or
        friend added).

        :param client_socket: Socket of connected client.
        :param data: Requester username (str), recipient username (str).
        """
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

    def start_game(self, data):
        self.requester = data["addressee"]
        self.recipient = data["body"]
        help_board = ttt_game.get_help_board()
        turn_dict = {self.requester: 'X', self.recipient: 'O'}
        turn = turn_dict[self.requester]
        the_board = ttt_game.return_new_board()
        response = self.build_message(utility.Responses.PLAY_TIC_TAC_TOE.value, self.requester,
                                      self.recipient, [help_board, the_board, turn, turn_dict])
        self.server_send(self.clients[self.recipient], response)

    def play_tic_tac_toe(self, data):
        board, turn, move, turn_dict = [data['extra_info'][0], data['extra_info'][1],
                                        data['extra_info'][2], data['extra_info'][3]]
        help_board = ttt_game.get_help_board()
        updated_board, turn = ttt_game.updateBoard(board, turn, move)
        if isinstance(updated_board, dict):
            self.requester, self.recipient = self.recipient, self.requester
            if data["header"] == utility.Responses.TIC_TAC_TOE_ERROR.value:
                turn = turn_dict[self.requester]
                response = self.build_message(utility.Responses.PLAY_TIC_TAC_TOE.value, self.requester,
                                              self.recipient, [help_board, updated_board, turn, turn_dict])
                self.server_send(self.clients[self.recipient], response)

            else:
                turn = turn_dict[self.requester]
                response = self.build_message(utility.Responses.PLAY_TIC_TAC_TOE.value, self.requester,
                                              self.recipient, [help_board, updated_board, turn, turn_dict])
                self.server_send(self.clients[self.recipient], response)
        elif isinstance(updated_board, str):
            if updated_board == utility.Responses.TIC_TAC_TOE_SPACE_ERROR.value:
                turn = turn_dict[self.recipient]
                response = self.build_message(utility.Responses.TIC_TAC_TOE_ERROR.value, self.requester,
                                              self.recipient, [help_board, board, turn, turn_dict])
                self.server_send(self.clients[self.recipient], response)
            elif updated_board == 'won':
                response = self.build_message(utility.Responses.TIC_TAC_TOE_WINNER.value, self.requester,
                                              self.recipient, [help_board, board, turn,
                                                               f'Game Over! {turn} won!'])
                self.server_send(self.clients[self.recipient], response)
                self.server_send(self.clients[self.requester], response)
            elif updated_board == 'tie':
                response = self.build_message(utility.Responses.TIC_TAC_TOE_TIE.value, self.requester,
                                              self.recipient, [help_board, board, turn,
                                                               f"Game Over! It's a tie!"])
                self.server_send(self.clients[self.recipient], response)
                self.server_send(self.clients[self.requester], response)

    def view_friend_requests(self, client_socket, data):
        """
        Function that runs when user requests to view their friends requests sent to them.
        Runs the database function to retrieve list of requests from db friends table.
        Responds to the client with a list of friend request usernames.

        :param client_socket: Socket of connected client.
        :param data: VIEW_FRIEND_REQUESTS header (enum), requester username (str).
        """
        requester = data["addressee"]
        friends_list = self.db.view_friend_requests(requester)
        response = self.build_message(utility.Responses.PRINT_FRIEND_REQUESTS.value, requester,
                                      "\n".join([x[0] for x in friends_list]), None)
        self.server_send(client_socket, response)

    def view_friends(self, client_socket, data):
        """
        Function that runs when user requests to view their friends list.
        Runs the database function to retrieve list of friend from db friends table.
        Responds to the client with a list of friends usernames.

        :param client_socket: Socket of connected client.
        :param data: Requester username (str).
        """
        requester = data["addressee"]
        friends_list = self.db.view_friends_and_status(requester)
        response = self.build_message(utility.Responses.PRINT_FRIENDS_LIST.value, requester,
                                      "\n".join([x[0] + " : " + x[1] for x in friends_list]), None)
        self.server_send(client_socket, response)

    def authenticate_tic_tac_toe(self, client_socket, data):
        requester = data["addressee"]
        recipient = data["body"]
        if recipient not in self.clients:
            response = self.build_message(utility.Responses.ERROR.value, None,
                                          "Username not found", None)
            self.server_send(client_socket, response)
        else:
            self.db.insert_ttt_game_request(requester, recipient)
            response = self.build_message(utility.Responses.TIC_TAC_TOE_REQUEST.value, requester,
                                          recipient, None)
            self.server_send(self.clients[recipient], response)

    def set_status(self, client_socket, data):
        """
        Function runs when client requests to change their status. Inserts given status into clients 'status' field
        in the db users table. Responds back to the client confirming status update.

        :param client_socket: Socket of connected client.
        :param data: Client username (str), status requested (str).
        """
        username = data["addressee"]
        status = data["body"]
        self.db.set_status(status, username)
        response = self.build_message(utility.Responses.PRINT_STATUS_AWAY.value, username, f"Status: {status}", None)
        self.server_send(client_socket, response)

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

    def server_send(self, client_socket, msg_to_send):
        """
        Method takes the message dictionary and dumps into json message packet.
        Json message packet is sent to the client.

        :param client_socket: Socket of connected client.
        :param msg_to_send: Parameter for (build_message) dictionary to be sent.
        """
        try:
            msg_packet = json.dumps(msg_to_send)
            self.send_message(client_socket, msg_packet)
        except socket.error as e:
            logging.error(e)

    def view_ttt_requests(self, client_socket, data):
        requester = data["addressee"]
        ttt_request_list = self.db.view_ttt_requests(requester)
        response = self.build_message(utility.Responses.PRINT_TTT_REQUESTS.value, requester,
                                      ttt_request_list, None)
        self.server_send(client_socket, response)

    def quit(self, client_socket, data):
        """
        Function run when clients request to quit the application. Changes client status to 'OFFLINE'.
        Removes client from clients dictionary and sends 'QUIT' header back to client.

        :param client_socket: Socket of connected client.
        :param data: Client username (str)
        """
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
        Encodes message beforehand using 'utf-8'.

        :param: client_socket: Socket of connected client.
        :param: msg: The message packet to be sent to client.
        """
        client_socket.send(msg.encode(ENCODE))


if __name__ == '__main__':
    """
    Instantiates the Server class with host (IP) and port numbers.
    Runs the Server run function.
    """
    server = Server('0.0.0.0', 5555)
    server.run()
