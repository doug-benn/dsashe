import time
import unittest
import socket
import warnings

warnings.simplefilter("ignore", ResourceWarning)


class Test_ServerResponse(unittest.TestCase):
    # Setup client connection
    def setUp(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("localhost", 6479))

    def test_ping(self):
        self.client.send(b"ping\r\n")
        self.assertEqual(self.client.recv(1024), b"PONG\r\n")

        self.client.send(b"ping\r\n")
        self.assertEqual(self.client.recv(1024).decode().strip(), "PONG")

    def test_echo(self):
        self.client.send(b"echo\n\nHello\r\n")
        self.assertEqual(self.client.recv(1024), b"Hello\r\n")

        self.client.send(b"echo\n\nLonger Echo Test Command\r\n")
        self.assertEqual(self.client.recv(1024), b"Longer Echo Test Command\r\n")

    def test_get(self):
        self.client.send(b"get\n\ntest\r\n")
        self.assertEqual(self.client.recv(1024), b"test\n\ntest_value\r\n")

    def test_get_fail(self):
        self.client.send(b"get\n\nnot_here\r\n")
        self.assertEqual(self.client.recv(1024), b"-1\r\n")

    def test_set(self):
        self.client.send(b"set\n\ntest\n\nntest_value\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")

    def test_set_get(self):
        self.client.send(b"set\n\nset_get\n\nset and get data\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")

        self.client.send(b"get\n\nset_get\r\n")
        self.assertEqual(self.client.recv(1024), b"set_get\n\nset and get data\r\n")

    def test_set_expire(self):
        self.client.send(b"set\n\ntest_expire\n\ntesting data\n\nEX\n\n1\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")
        time.sleep(1)
        self.client.send(b"get\n\ntest_expire\r\n")
        self.assertEqual(self.client.recv(1024), b"-1\r\n")

    def test_set_non_expire(self):
        self.client.send(b"set\n\ntest_expire\n\ntesting data\n\nPX\n\n10000\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")
        time.sleep(1)
        self.client.send(b"get\n\ntest_expire\r\n")
        self.assertEqual(self.client.recv(1024), b"test_expire\n\ntesting data\r\n")


if __name__ == "__main__":
    unittest.main(warnings="ignore")
