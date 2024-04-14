import os
import socket

from threading import Thread, Lock, Timer


class ValueStore:
    def __init__(self):
        self.store = {}
        self.lock = Lock()

    def set_value(self, key, value, expire=None):
        with self.lock:
            self.store[key] = value
            if expire is not None:
                Timer(expire / 1000, self.delete_key, args=(key,)).start()
            return "ok"

    def get_value(self, key):
        with self.lock:
            return self.store.get(key, None)

    def delete_key(self, key):
        with self.lock:
            if key in self.store:
                del self.store[key]
                print(f"Deleting key: {key}")


value_store = ValueStore()


def handle_client(client_conn, client_address):
    try:
        while True:
            data = client_conn.recv(1024)
            print(data)
            if not data:
                break

            decode_message = data.decode().split("\r\n")
            command = decode_message[0].lower()
            print(f"Command: {command}")
            print(f"Message: {decode_message[1:]}")

            match command:
                case "ping":
                    client_conn.sendall(b"+PONG\r\n")

                case "echo":
                    client_conn.sendall(
                        ("$" + str(len(decode_message[1])) + "\r\n" + decode_message[1] + "\r\n").encode()
                    )

                case "set":
                    key = decode_message[1]
                    value = decode_message[2]
                    if "px" in decode_message:
                        time = float(decode_message[4])
                        value_store.set_value(key, value, expire=time)
                    else:
                        value_store.set_value(key, value)
                    client_conn.sendall(b"+OK\r\n")

                case "get":
                    key = decode_message[1]
                    value = value_store.get_value(key)
                    if value is None:
                        client_conn.sendall(b"$-1\r\n")
                    else:
                        client_conn.sendall(("$" + str(len(value)) + "\r\n" + value + "\r\n").encode())

            print(f"Sending to >> {client_address}")
    finally:
        client_conn.shutdown(2)  # 0 = done receiving, 1 = done sending, 2 = both
        client_conn.close()


def listening_connnections(server_socket):
    while True:
        try:
            client_conn, client_address = server_socket.accept()
            print(f"New connection from {client_address[0]}:{client_address[1]}")
            Thread(target=handle_client, args=(client_conn, client_address)).start()
        except Exception as e:
            print(f"Error accepting connections: {e}")


def main():
    server_socket = socket.create_server(("localhost", 6379))
    Thread(target=listening_connnections, args=(server_socket,), daemon=True).start()

    ### This is really annoying and messy
    pid = os.getpid()
    input("Server started and is listening, press any key to abort...")
    os.kill(pid, 9)


if __name__ == "__main__":
    main()
