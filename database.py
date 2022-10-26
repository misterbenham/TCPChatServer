import sqlite3


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
                     f"username TEXT, password TEXT)")
        self.commit()

    def create_friends_table(self):
        self.execute(f"CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY, "
                     f"sender TEXT, receiver TEXT, status TEXT)")
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

    def find_user_id(self, user):
        find_user_id = f"SELECT user_id FROM users WHERE username = '{user}'"
        self.cursor.execute(find_user_id)
        return self.cursor.fetchone()[0]

    def find_user_name(self, id):
        find_user_name = f"SELECT username FROM users WHERE user_id = '{id}'"
        self.cursor.execute(find_user_name)
        return self.cursor.fetchone()[0]

    def find_friendship_status(self, requester, recipient):
        receiver = self.find_user_id(requester)
        sender = self.find_user_id(recipient)
        find_status = f"SELECT status FROM friends WHERE sender = {sender} AND receiver = {receiver}"
        self.cursor.execute(find_status)
        retval = self.cursor.fetchone()[0]
        print (retval)
        return retval

    def insert_friend_relationship(self, requester, recipient):
        if self.find_friendship_status(requester, recipient) == "SENT":
            receiver = self.find_user_id(requester)
            sender = self.find_user_id(recipient)
            friends_accepted = f"UPDATE friends SET status = 'FRIENDS' WHERE sender = " \
                               f"{sender} AND receiver = {receiver}"
            self.cursor.execute(friends_accepted)
            self.commit()

    def update_to_friends(self, requester, recipient):
        sender = self.find_user_id(requester)
        receiver = self.find_user_id(recipient)
        add_relationship = f"INSERT INTO friends (sender, receiver, status) VALUES (?, ?, ?)"
        self.cursor.execute(add_relationship, (sender, receiver, "SENT"))
        self.commit()

    def insert_username_and_password(self, username, password):
        add_user = f"INSERT INTO users (username, password) VALUES (?, ?)"
        self.cursor.execute(add_user, (username, password))
        self.commit()

    def view_friend_requests(self, user):
        id = self.find_user_id(user)
        find_request_status = f"SELECT sender FROM friends WHERE receiver = '{id}' AND status = 'SENT'"
        self.cursor.execute(find_request_status)
        user_ids = self.cursor.fetchall()
        friend_requests = [self.find_user_name(x[0]) for x in user_ids]
        return friend_requests

    def view_friends(self, user):
        id = self.find_user_id(user)
        find_friends = f"SELECT sender FROM friends WHERE receiver = '{id}' AND status = 'FRIENDS' " \
                       f"UNION ALL SELECT receiver FROM friends WHERE sender = '{id}' AND status = 'FRIENDS'"
        self.cursor.execute(find_friends)
        friend_ids = self.cursor.fetchall()
        friends = [self.find_user_name(x[0]) for x in friend_ids]
        return friends
