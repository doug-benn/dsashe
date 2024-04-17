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
value_store.set_value("test", "test_value")

# EOS = \r\n
# Next Segment = \n\n


def handle_client(client_conn, client_address):
    try:
        buffer = b""
        while True:
            while b"\r\n" not in buffer:
                buffer = buffer.join([buffer, client_conn.recv(1024)])
                # Check Max Lenght of Buffer
                if buffer == b"":
                    raise RuntimeError("Socket connection broken")

            message, sep, buffer = buffer.partition(b"\r\n")

            decode_message = message.decode().split("\n\n")
            print(decode_message)
            command = decode_message[0].lower()
            print(f"Command: {command}")

            match command:
                case "ping":
                    print("Sending Ping")
                    client_conn.sendall(b"PONG\r\n")

                case "echo":
                    client_conn.sendall((decode_message[1] + "\r\n").encode())

                case "get" if len(decode_message) == 2:
                    # Parse remaining headers
                    key = decode_message[1]
                    value = value_store.get_value(key)
                    if value is None:
                        client_conn.sendall(b"-1\r\n")
                    else:
                        client_conn.sendall((key + "\n\n" + value + "\r\n").encode())

                case "set" if len(decode_message) >= 2:
                    key = decode_message[1]
                    value = decode_message[2]
                    if len(decode_message) > 2:
                        # Extra Args
                        extra_args = [arg.lower() for arg in decode_message[3:]]
                        print(extra_args)
                        if "px" in extra_args:  # PX milliseconds -- Expire time, in milliseconds
                            time = int(extra_args[extra_args.index("px") + 1])
                            value_store.set_value(key, value, expire=time)
                    else:
                        value_store.set_value(key, value)

                    client_conn.sendall(b"OK\r\n")

                case _:
                    print(f"Parse Error: {command}")
                    client_conn.sendall(b"-1\r\n")

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
    server_socket = socket.create_server(("localhost", 6479))
    # server_socket.settimeout(20)
    Thread(target=listening_connnections, args=(server_socket,), daemon=True).start()

    ### This is really annoying and messy
    pid = os.getpid()
    input("Server started and is listening, press any key to abort...")
    os.kill(pid, 9)


if __name__ == "__main__":
    main()

    # data = client_conn.recv(1024)
    # print(data)
    # if not data:
    #     print("Closing socket")
    #     break

    # expiry = int.from_bytes(buffer[0:4], byteorder="big")
    # print(expiry)
