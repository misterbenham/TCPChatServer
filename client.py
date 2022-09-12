import logging
import socket
import threading
import time

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
ENCODE = "utf-8"


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
            send_thread = threading.Thread(target=self.client_send)
            send_thread.start()
            while True:
                try:
                    msg = self.client_socket.recv(2048).decode(ENCODE)
                    print(msg)
                except socket.error as e:
                    logging.error(e)
                    self.client_socket.close()
                    break
        except socket.error as e:
            logging.error(e)

    def client_send(self):
        """
        Message input allowing clients to enter and send messages through server to recipient.
        """
        while True:
            try:
                msg = input()
                self.client_socket.send(msg.encode(ENCODE))
            except socket.error as e:
                logging.error(e)


if __name__ == '__main__':
    client = Client('127.0.0.1', 5555)
    client.run()
