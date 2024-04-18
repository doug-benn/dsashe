import socket
import time


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 6479))

    # client.send(b"set\n\ntest_expire\n\ntesting data\n\nPX\n\n10\r\n")

    client.send(b"set\n\nset_get\n\nset and get data\r\n")

    # client.send(b"get\n\nset_get\r\n")

    while True:
        # length = 100
        # header = length.to_bytes(2, byteorder="big") + b"\r\n"
        # print(header)
        # client.send(header[:4])

        response = client.recv(1024)
        response = response.decode()

        if response.lower() == "closed":
            break

        time.sleep(5)
        print(f"Received: {response}")

    client.close()
    print("Connection to server closed")


run_client()
