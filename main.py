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


def decode_integer(elems):
    elem = elems.pop(0)
    return int(elem[1:])


def decode_array(elems):
    elem = elems.pop(0)
    num_elements = int(elem[1:])
    result = []
    for i in range(num_elements):
        result.append(parse_message(elems))
    return result


def decode_bulk_str(elems):
    elem = elems.pop(0)
    num_chars = int(elem[1:])
    content = elems.pop(0)
    assert len(content) == num_chars
    return str(content)


def parse_message(msg):
    msg_type = msg[0][0]

    match msg_type:
        case "*":  # Array Message
            decoded_msg = decode_array(msg)
        case "$":  # Bulk String
            decoded_msg = decode_bulk_str(msg)
        case _:
            print("Error Message type unsupported")

    return decoded_msg


def handle_client(client_conn, client_address):
    try:
        while True:
            data = client_conn.recv(1024)
            print(data)
            if not data:
                break

            decode_message = parse_message(data.decode().split("\r\n"))
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
        client_conn.close()


def main():
    # Setup and start server
    server_socket = socket.create_server(("localhost", 6379)).listen(5)
    print("Server started and listening")

    all_threads = []

    try:
        while True:
            client_conn, client_address = server_socket.accept()
            print(f"New connection from {client_address[0]}:{client_address[1]}")
            client_thread = Thread(target=handle_client, args=(client_conn, client_address), daemon=True).start()
            all_threads.append(client_thread)

    except KeyboardInterrupt:
        print("Stopped by Ctrl+C")
    finally:
        if server_socket:
            server_socket.close()
        for thread in all_threads:
            thread.join()


if __name__ == "__main__":
    main()
