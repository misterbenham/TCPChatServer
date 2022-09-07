import sqlite3


class Database:
    DB_LOCATION = 'db.sqlite'

    def __init__(self):
        """Initialise db class variables"""
        self.connection = sqlite3.connect(self.DB_LOCATION, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def execute(self, new_data):
        self.cursor.execute(new_data)
        