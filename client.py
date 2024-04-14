import socket
import time


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 6379))

    while True:
        msg = "ping"
        client.send(msg.encode()[:1024])

        response = client.recv(1024)
        response = response.decode()

        if response.lower() == "closed":
            break

        print(f"Received: {response}")
        time.sleep(10)

    client.close()
    print("Connection to server closed")


run_client()
