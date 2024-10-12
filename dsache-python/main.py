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
                Timer(expire, self.delete_key, args=(key,)).start()
            return True

    def get_value(self, key):
        with self.lock:
            return self.store.get(key, None)

    def check_key(self, key):
        with self.lock:
            if key in self.store:
                return True
            else:
                return False

    def delete_key(self, key):
        with self.lock:
            if key in self.store:
                del self.store[key]
                print(f"Deleting key: {key}")


value_store = ValueStore()

# EOS = \r\n
# Next Segment = \n\n


def handle_client(client_conn, client_address):
    client_conn.settimeout(10)
    with client_conn:
        try:
            buffer = b""
            while True:
                while b"\r\n" not in buffer:
                    buffer = buffer.join([buffer, client_conn.recv(1024)])
                    # Check Max Lenght of Buffer
                    if buffer == b"":
                        raise RuntimeError(
                            f"Socket connection broken to {client_address}"
                        )
                    if len(buffer) > 8 and b"\n\n" not in buffer:
                        raise RuntimeError(
                            f"Problem with the data being sent by {client_address}"
                        )

                message, _, buffer = buffer.partition(b"\r\n")

                decode_message = message.decode().split("\n\n")
                print(decode_message)
                command = decode_message[0].lower()

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
                            client_conn.sendall(
                                (key + "\n\n" + value + "\r\n").encode()
                            )

                    case "set" if len(decode_message) >= 2:
                        key = decode_message[1]
                        value = decode_message[2]

                        if len(decode_message) > 3:
                            setting = True
                            # Extra Args
                            extra_args = [arg.lower() for arg in decode_message[3:]]
                            expire_time = None
                            if "ex" in extra_args:  # EX -- Expire time, in seconds
                                expire_time = int(
                                    extra_args[extra_args.index("ex") + 1]
                                )
                            if "px" in extra_args:  # PX -- Expire time, in milliseconds
                                expire_time = (
                                    int(extra_args[extra_args.index("px") + 1]) / 1000
                                )
                            if extra_args in ["nx", "xx"]:
                                print("nx || xx")
                                # NX -- Only set the key if it does not already exist.
                                # XX -- Only set the key if it already exists.
                                if not value_store.check_key(key):
                                    setting = False
                                    print(("NOT SETTINGS THE KEY"))

                            if setting:
                                if value_store.set_value(
                                    key, value, expire=expire_time
                                ):
                                    client_conn.sendall(b"OK\r\n")
                            else:
                                client_conn.sendall(b"Key Exists\r\n")
                        else:
                            if value_store.set_value(key, value):
                                client_conn.sendall(b"OK\r\n")

                    case _:
                        print(f"Parse Error: {command}")
                        client_conn.sendall(b"-1\r\n")

                # print(f"Sending to >> {client_address}")

        except RuntimeError as e:
            print(f"Connection has closed: {e}")
        except socket.timeout as e:
            client_conn.sendall(b"-1\r\n")
            print(f"Connection has timed out: {e}")
        except Exception as e:
            client_conn.sendall(b"-1\r\n")
            print(f"Other Exception: {e}")

        finally:
            client_conn.shutdown(socket.SHUT_RDWR)
            # client_conn.shutdown(2)  # 0 = done receiving, 1 = done sending, 2 = both
            client_conn.close()
            return None


def listening_connnections(server_socket):
    while True:
        try:
            client_conn, client_address = server_socket.accept()
            print(f"New connection from {client_address[0]}:{client_address[1]}")
            Thread(target=handle_client, args=(client_conn, client_address)).start()
        except Exception as e:
            print(f"Failed to accept new connection: {e}")


def main():
    server_socket = socket.create_server(("localhost", 6479))
    Thread(target=listening_connnections, args=(server_socket,), daemon=True).start()

    ### This is really annoying and messy
    pid = os.getpid()
    input("Server started and is listening, press any key to abort...\n\n")

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
