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
        while True:
            try:
                msg = input("")
                user_msg = f"Sender: " + msg
                self.client_socket.send(user_msg.encode(ENCODE))
            except socket.error as e:
                logging.error(e)


if __name__ == '__main__':
    client = Client('127.0.0.1', 5555)
    client.run()
