import sqlite3
from datetime import datetime


class Database:
    DB_LOCATION = 'db.sqlite'

    def __init__(self):
        """Initialise db class variables"""
        self.connection = sqlite3.connect(self.DB_LOCATION, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def execute(self, new_data):
        self.cursor.execute(new_data)

    def commit(self):
        self.connection.commit()

    def create_users_table(self):
        self.execute(f"CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, "
                     f"username TEXT, password TEXT, user_status TEXT)")
        self.commit()

    def create_friends_table(self):
        self.execute(f"CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY, "
                     f"sender TEXT, receiver TEXT, status TEXT)")
        self.commit()

    def create_messages_table(self):
        self.execute(f"CREATE TABLE IF NOT EXISTS messages (message_id INTEGER PRIMARY KEY, "
                     f"sender TEXT, receiver TEXT, message TEXT, timestamp TEXT, "
                     f"friend_id INTEGER, FOREIGN KEY (friend_id) REFERENCES friends(id))")
        self.commit()

    def find_username_in_db(self, username):
        find_user = "SELECT * FROM users WHERE username = ?"
        self.cursor.execute(find_user, [username])
        return self.cursor.fetchall()

    def find_user_pw_in_db(self, username, password):
        find_user = "SELECT * FROM users WHERE username = ? AND password = ?"
        self.cursor.execute(find_user, [username, password])
        return self.cursor.fetchall()

    def fetch_all_users_data(self, username):
        self.cursor.execute("SELECT * FROM users")
        rows = self.cursor.fetchall()
        return rows

    def fetch_messages(self, requester, recipient):
        sender = self.find_user_id(requester)
        receiver = self.find_user_id(recipient)
        fetch_messages = f"SELECT message FROM messages WHERE sender = ? AND receiver = ? " \
                         f"OR sender = ? AND receiver = ? " \
                         f"ORDER BY timestamp ASC LIMIT 10"
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
        find_user_id = f"SELECT user_id FROM users WHERE username = ?"
        self.cursor.execute(find_user_id, [user])
        return self.cursor.fetchone()[0]

    def find_user_name(self, id):
        find_user_name = f"SELECT username FROM users WHERE user_id = ?"
        self.cursor.execute(find_user_name, [id])
        return self.cursor.fetchone()[0]

    def find_friendship_status(self, requester, recipient):
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
        if self.find_friendship_status(requester, recipient) == "SENT":
            receiver = self.find_user_id(requester)
            sender = self.find_user_id(recipient)
            friends_accepted = f"UPDATE friends SET status = 'FRIENDS' WHERE sender = " \
                               f"? AND receiver = ?"
            self.cursor.execute(friends_accepted, [sender, receiver])
            self.commit()

    def insert_friend_request(self, requester, recipient):
        sender = self.find_user_id(requester)
        receiver = self.find_user_id(recipient)
        add_relationship = f"INSERT INTO friends (sender, receiver, status) VALUES (?, ?, ?)"
        self.cursor.execute(add_relationship, (sender, receiver, "SENT"))
        self.commit()

    def insert_message(self, requester, recipient, message):
        sender = self.find_user_id(requester)
        receiver = self.find_user_id(recipient)
        friend_id = self.find_friendship_id(requester, recipient)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_message = f"INSERT INTO messages (sender, receiver, message, timestamp, friend_id) " \
                         f"VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(insert_message, (sender, receiver, message, timestamp, friend_id))
        self.commit()

    def insert_username_and_password(self, username, password):
        add_user = f"INSERT INTO users (username, password, user_status) VALUES (?, ?, ?)"
        self.cursor.execute(add_user, (username, password, 'OFFLINE'))
        self.commit()

    def set_status(self, status, user):
        set_status = f"UPDATE users SET user_status = ? WHERE username = ?"
        self.cursor.execute(set_status, [status, user])
        self.commit()

    def view_friend_requests(self, user):
        find_request_status = f"SELECT username FROM users INNER JOIN friends ON users.user_id=friends.sender WHERE" \
                              f" friends.status='SENT' AND friends.receiver=" \
                              f"(SELECT user_id FROM users" \
                              f" WHERE username = ?)"
        self.cursor.execute(find_request_status, [user])
        friend_requests = self.cursor.fetchall()
        return friend_requests

    def view_friends_and_status(self, user):
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

    def view_friends(self, user):
        find_friends = f"SELECT username FROM users INNER JOIN friends" \
                       f" ON users.user_id=friends.sender WHERE" \
                       f" friends.status='FRIENDS' AND friends.receiver = " \
                       f"(SELECT user_id FROM users WHERE username = ?) UNION ALL" \
                       f" SELECT username FROM users INNER JOIN friends ON" \
                       f" users.user_id=friends.receiver WHERE" \
                       f" friends.status='FRIENDS' AND friends.sender = (SELECT user_id FROM users WHERE username = ?)"
        self.cursor.execute(find_friends, [user, user])
        friend_list = self.cursor.fetchall()
        friend_list_usernames = []
        for i in friend_list:
            friend_list_usernames.append(i[0])
        return friend_list_usernames
