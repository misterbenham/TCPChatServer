import sqlite3
from datetime import datetime


class Database:
    DB_LOCATION = 'db.sqlite'

    def __init__(self):
        """Initialise db class variables"""
        self.connection = sqlite3.connect(self.DB_LOCATION, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_users_table()
        self.create_friends_table()
        self.create_messages_table()
        self.create_ttt_table()

    def execute(self, new_data):
        """
        Function executes a stored procedure.
        :param new_data: The SQL statement to execute.
        """
        self.cursor.execute(new_data)

    def commit(self):
        """
        Function commits the changes made to the database.
        """
        self.connection.commit()

    def create_users_table(self):
        """
        Function uses SQL 'CREATE' statement to create the user's table with required columns.
        """
        self.execute(f"CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, "
                     f"username TEXT, password TEXT, user_status TEXT)")
        self.commit()

    def create_friends_table(self):
        """
        Function uses SQL 'CREATE' statement to create the friend's table with required columns.
        """
        self.execute(f"CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY, "
                     f"sender TEXT, receiver TEXT, status TEXT)")
        self.commit()

    def create_messages_table(self):
        """
        Function uses SQL 'CREATE' statement to create the message's table with required columns.
        """
        self.execute(f"CREATE TABLE IF NOT EXISTS messages (message_id INTEGER PRIMARY KEY, "
                     f"sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, "
                     f"friend_id INTEGER, FOREIGN KEY (friend_id) REFERENCES friends(id))")
        self.commit()

    def create_ttt_table(self):
        self.execute(f"CREATE TABLE IF NOT EXISTS ttt (game_id INTEGER PRIMARY KEY,"
                     f" sender TEXT, receiver TEXT, status TEXT, timestamp TEXT,"
                     f" friend_id INTEGER, FOREIGN KEY (friend_id) REFERENCES friends(id))")
        self.commit()

    def find_username_in_db(self, username):
        """
        Function uses an SQL 'SELECT' statement to select and return TRUE if it finds the username passed to it.
        :param username: username of client to find in db.
        :return: True if username passed is found in db. False if not found.
        """
        find_user = "SELECT * FROM users WHERE username = ?"
        self.cursor.execute(find_user, [username])
        return self.cursor.fetchall()

    def find_user_pw_in_db(self, username, password):
        """
        Function uses an SQL 'SELECT' statement
        :param username: Username of client to find in db.
        :param password: Clients password to find in db.
        :return: Returns TRUE is username and password that are passed match in the db.
        """
        find_user = "SELECT * FROM users WHERE username = ? AND password = ?"
        self.cursor.execute(find_user, [username, password])
        return self.cursor.fetchall()

    def fetch_all_users_data(self, username):
        """
        Function selects all data from the users table.
        :param username: Client username
        :return: All rows from users table in db.
        """
        self.cursor.execute("SELECT * FROM users")
        rows = self.cursor.fetchall()
        return rows

    def fetch_messages(self, requester, recipient):
        """
        Functions fetches and returns a list of all messages exchanged between client requester and recipient
        in timeline order. The list is a list of tuples- therefore a new list is created and returned, which
        only contains the messages.
        :param requester: Username of client (requester)
        :param recipient: Username of recipient
        :return: List of all messages exchanged between requester and recipient. Returns None if no messages found.
        """
        sender = self.find_user_id(requester)
        receiver = self.find_user_id(recipient)
        fetch_messages = f"SELECT message FROM messages WHERE sender = ? AND receiver = ? " \
                         f"OR sender = ? AND receiver = ? " \
                         f"ORDER BY timestamp DESC LIMIT 10;"
        self.cursor.execute(fetch_messages, [receiver, sender, sender, receiver])
        retval = self.cursor.fetchall()
        previous_messages = []
        for i in retval:
            previous_messages.append(i[0])
        if retval:
            return previous_messages
        else:
            return None

    def find_friendship_id(self, requester, recipient):
        """
        Function uses an SQL 'SELECT' statement to fetch and return the friendship id of the requester and
        recipient in the friends table. A 'UNION' statement makes another statement and merges the results.
        Only one id should be found and returned.
        :param requester: Requester username.
        :param recipient: Recipient username.
        :return: ID of friendship between requester and recipient. Returns none if no friendship_id is found.
        """
        receiver = self.find_user_id(requester)
        sender = self.find_user_id(recipient)
        find_friendship_id = f"SELECT id FROM friends WHERE sender = ? AND receiver = ? " \
                             f"UNION ALL SELECT id FROM friends WHERE sender = ? AND receiver = ?"
        self.cursor.execute(find_friendship_id, [receiver, sender, sender, receiver])
        retval = self.cursor.fetchone()
        if retval:
            return retval[0]
        else:
            return None

    def find_user_id(self, user):
        """
        Function selects and returns the user_id of the user passed in the users table.
        :param user: client username.
        :return: user_id (int)
        """
        find_user_id = f"SELECT user_id FROM users WHERE username = ?"
        self.cursor.execute(find_user_id, [user])
        return self.cursor.fetchone()[0]

    def find_user_name(self, id):
        """
        Function selects and returns a username of the id passed to the user's table in db.
        :param id: id of the username to find.
        :return: Username found from id passed.
        """
        find_user_name = f"SELECT username FROM users WHERE user_id = ?"
        self.cursor.execute(find_user_name, [id])
        return self.cursor.fetchone()[0]

    def find_friendship_status(self, requester, recipient):
        """
        Function finds and returns the status of the two users passed, in the friends table.
        :param requester: username of requester.
        :param recipient: username of recipient.
        :return: Status (str) of the two users friendship.
        """
        receiver = self.find_user_id(requester)
        sender = self.find_user_id(recipient)
        find_status = f"SELECT status FROM friends WHERE sender = ? AND receiver = ?"
        self.cursor.execute(find_status, [sender, receiver])
        retval = self.cursor.fetchone()
        if retval:
            return retval[0]
        else:
            return None

    def insert_friend_relationship(self, requester, recipient):
        """
        Function uses an SQL 'UPDATE' statement to insert the status 'FRIENDS', if the requester and recipient
        status is already 'SENT'.
        :param requester: Requester username.
        :param recipient: Recipient username.
        """
        if self.find_friendship_status(requester, recipient) == "SENT":
            receiver = self.find_user_id(requester)
            sender = self.find_user_id(recipient)
            friends_accepted = f"UPDATE friends SET status = 'FRIENDS' WHERE sender = " \
                               f"? AND receiver = ?"
            self.cursor.execute(friends_accepted, [sender, receiver])
            self.commit()

    def insert_friend_request(self, requester, recipient):
        """
        Function uses an SQL 'INSERT' statement to insert the string 'SENT' in the status column of the requester
        and recipient.
        :param requester: Requester username.
        :param recipient: Recipient username.
        """
        sender = self.find_user_id(requester)
        receiver = self.find_user_id(recipient)
        add_relationship = f"INSERT INTO friends (sender, receiver, status) VALUES (?, ?, ?)"
        self.cursor.execute(add_relationship, (sender, receiver, "SENT"))
        self.commit()

    def insert_message(self, requester, recipient, message):
        """
        Function finds the friendship_id of the requester and recipient from the friends table and then uses that ID
        as a foreign key to insert the message between the users into the messages table. Alongside the message is
        a timestamp that uses a date/time function.
        :param requester: Requester username.
        :param recipient: Recipient username.
        :param message: The string message exchanged between the requester and recipient.
        """
        sender = self.find_user_id(requester)
        receiver = self.find_user_id(recipient)
        friend_id = self.find_friendship_id(requester, recipient)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_message = f"INSERT INTO messages (sender, receiver, message, timestamp, friend_id) " \
                         f"VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(insert_message, (sender, receiver, message, timestamp, friend_id))
        self.commit()

    def insert_ttt_game_request(self, requester, recipient):
        sender = self.find_user_id(requester)
        receiver = self.find_user_id(recipient)
        friend_id = self.find_friendship_id(requester, recipient)
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        insert_game = f"INSERT INTO ttt (sender, receiver, status, timestamp, friend_id) " \
                      f"VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(insert_game, (sender, receiver, 'SENT', timestamp, friend_id))
        self.commit()

    def insert_ttt_game_response(self, requester, recipient, status):
        sender = self.find_user_id(requester)
        receiver = self.find_user_id(recipient)
        update_response = f"UPDATE ttt SET status = ? WHERE sender = ? AND receiver = ?"
        self.cursor.execute(update_response, [status, receiver, sender])
        self.commit()

    def insert_username_and_password(self, username, password):
        """
        Function uses an 'SQL' INSERT statement to insert the username and password passed to it.
        As this function is run upon user registration, the function also inserts the status 'OFFLINE' into
        the users table.
        :param username: Username to insert.
        :param password: Password to insert.
        """
        add_user = f"INSERT INTO users (username, password, user_status) VALUES (?, ?, ?)"
        self.cursor.execute(add_user, (username, password, 'OFFLINE'))
        self.commit()

    def set_status(self, status, user):
        """
        Function updates the user's table user_status, depending on the username and status string passed.
        :param status: Status (str) to insert.
        :param user:  Username of client.
        """
        set_status = f"UPDATE users SET user_status = ? WHERE username = ?"
        self.cursor.execute(set_status, [status, user])
        self.commit()

    def view_friend_requests(self, user):
        """
        Function selects and returns all usernames from the friend's table where the status between passed requester
        and recipient is 'SENT'. An 'inner join' and 'sub-statement' are used in the SQL statement.
        :param user: Username of client.
        :return: List of friend requests received by user.
        """
        find_request_status = f"SELECT username FROM users INNER JOIN friends ON users.user_id=friends.sender WHERE" \
                              f" friends.status='SENT' AND friends.receiver=" \
                              f"(SELECT user_id FROM users" \
                              f" WHERE username = ?)"
        self.cursor.execute(find_request_status, [user])
        friend_requests = self.cursor.fetchall()
        return friend_requests

    def view_ttt_requests(self, user):
        """
        Function selects and returns all usernames from the friend's table where the status between passed requester
        and recipient is 'SENT'. An 'inner join' and 'sub-statement' are used in the SQL statement.
        :param user: Username of client.
        :return: List of friend requests received by user.
        """
        find_request_status = f"SELECT username FROM users INNER JOIN ttt ON users.user_id=ttt.sender WHERE" \
                              f" ttt.status='SENT' AND ttt.receiver=" \
                              f"(SELECT user_id FROM users" \
                              f" WHERE username = ?)"
        self.cursor.execute(find_request_status, [user])
        ttt_requests = self.cursor.fetchall()
        return ttt_requests

    def view_friends_and_status(self, user):
        """
        Function selects and returns all usernames of users in the friend's table where the requester and recipient
        status equal 'FRIENDS (and vice versa).'
        :param user: Client username.
        :return: List of friends usernames.
        """
        find_friends = f"SELECT username, user_status FROM users INNER JOIN friends" \
                       f" ON users.user_id=friends.sender WHERE" \
                       f" friends.status='FRIENDS' AND friends.receiver = " \
                       f"(SELECT user_id FROM users WHERE username = ?) UNION ALL" \
                       f" SELECT username, user_status FROM users INNER JOIN friends ON" \
                       f" users.user_id=friends.receiver WHERE" \
                       f" friends.status='FRIENDS' AND friends.sender = (SELECT user_id FROM users WHERE username = ?)"
        self.cursor.execute(find_friends, [user, user])
        friend_list = self.cursor.fetchall()
        return friend_list
