import socket


class CacheClient():
    def __init__(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip="localhost", port=6479):
        self.client.connect((ip, port))

    def close_connection(self):
        self.client.close()

    def send(self, command, data=None):
        if not data:
            send_data = f"{command}\r\n"
        else:
            send_data = f"{command}\n\n{data}\r\n"
        self.client.send(send_data.encode())