import socket


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 6479))

    client.send(b"ping\r\n")
    client.send(b"echo\n\ntest\r\n")
    client.send(b"get\n\ntest\r\n")

    while True:
        # length = 100
        # header = length.to_bytes(2, byteorder="big") + b"\r\n"
        # print(header)
        # client.send(header[:4])

        response = client.recv(1024)
        response = response.decode()

        if response.lower() == "closed":
            break

        print(f"Received: {response}")

    client.close()
    print("Connection to server closed")


run_client()
