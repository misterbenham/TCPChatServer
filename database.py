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

    def insert_username_and_password(self, username, password):
        add_user = "INSERT INTO users (username, password) VALUES (?,?)"
        self.cursor.execute(add_user, (username, password))
        self.commit()
