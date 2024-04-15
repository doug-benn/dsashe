import socket
import time


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 6379))

    while True:
        length = 100
        header = length.to_bytes(2, byteorder="big") + b"\r\n"
        print(header)

        client.send(header[:4])

        response = client.recv(1024)
        response = response.decode()

        if response.lower() == "closed":
            break

        print(f"Received: {response}")
        time.sleep(10)

    client.close()
    print("Connection to server closed")


run_client()
