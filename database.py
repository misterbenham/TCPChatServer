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
        self.execute(f"CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
        self.commit()

    def is_valid_username(self, username):
        find_user = "SELECT * FROM users WHERE username = ?"
        self.cursor.execute(find_user, [username])
        return self.cursor.fetchall()

    def is_valid_password(self, username, password):
        find_user = "SELECT * FROM users WHERE username = ? AND password = ?"
        self.cursor.execute(find_user, [username, password])
        return self.cursor.fetchall()


