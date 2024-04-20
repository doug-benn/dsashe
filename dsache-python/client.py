import socket
import time
from random import randbytes


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 6479))

    client.send("Hello World")

    while True:
        response = client.recv(1024)
        response = response.decode()

        if response == "-1":
            break

        time.sleep(1)
        print(f"Received: {response}")

    client.close()
    print("Connection to server closed")


run_client()
