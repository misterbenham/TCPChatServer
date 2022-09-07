class User:

    def __init__(self, client_connection):
        self.client_connection = client_connection
        self.username = None

    def username(self, username):
        self.username = username

