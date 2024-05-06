import time
import unittest
import socket
import warnings
from random import randbytes

warnings.simplefilter("ignore", ResourceWarning)


class Test_ServerResponse(unittest.TestCase):
    # Setup client connection
    def setUp(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("localhost", 6479))

    def test_ping(self):
        self.client.sendall(b"ping\r\n")
        self.assertEqual(self.client.recv(6), b"PONG\r\n")

        self.client.sendall(b"ping\r\n")
        self.assertEqual(self.client.recv(1024).decode().strip(), "PONG")

    def test_echo(self):
        self.client.sendall(b"echo\n\nHello\r\n")
        self.assertEqual(self.client.recv(1024), b"Hello\r\n")

        self.client.sendall(b"echo\n\nLonger Echo Test Command\r\n")
        self.assertEqual(self.client.recv(1024), b"Longer Echo Test Command\r\n")

    def test_bad_command(self):
        self.client.sendall(b"bad command\n\nnot_here\r\n")
        self.assertEqual(self.client.recv(1024), b"-1\r\n")

    def test_get(self):
        self.client.sendall(b"get\n\ntest\r\n")
        self.assertEqual(self.client.recv(1024), b"test\n\ntest_value\r\n")

    def test_get_fail(self):
        self.client.sendall(b"get\n\nnot_here\r\n")
        self.assertEqual(self.client.recv(1024), b"-1\r\n")

    def test_set(self):
        self.client.sendall(b"set\n\ntest\n\ntest_value\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")

    def test_set_not_exists(self):
        self.client.sendall(b"set\n\ntest\n\ntest_value\n\nNX\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")

    def test_set_exists(self):
        self.client.sendall(b"set\n\ntest\n\ntest_value\n\nXX\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")

    def test_set_get(self):
        self.client.sendall(b"set\n\nset_get\n\nset and get data\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")

        self.client.sendall(b"get\n\nset_get\r\n")
        self.assertEqual(self.client.recv(1024), b"set_get\n\nset and get data\r\n")

    def test_set_non_expire_px(self):
        self.client.sendall(b"set\n\ntest_non_expire\n\ntesting data\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")
        time.sleep(1)
        self.client.sendall(b"get\n\ntest_non_expire\r\n")
        self.assertEqual(self.client.recv(1024), b"test_non_expire\n\ntesting data\r\n")

    def test_set_expire_px(self):
        self.client.sendall(b"set\n\ntest_expire_ex\n\ntesting data\n\nEX\n\n1\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")
        time.sleep(2)
        self.client.sendall(b"get\n\ntest_expire_ex\r\n")
        self.assertEqual(self.client.recv(1024), b"-1\r\n")

    def test_set_expire_ex(self):
        self.client.sendall(b"set\n\ntest_expire_ex\n\ntesting data\n\nPX\n\n1000\r\n")
        self.assertEqual(self.client.recv(1024), b"OK\r\n")
        time.sleep(2)
        self.client.sendall(b"get\n\ntest_expire_ex\r\n")
        self.assertEqual(self.client.recv(1024), b"-1\r\n")

    def test_random(self):
        with self.assertRaises(ConnectionResetError):
            self.client.sendall(randbytes(1024 * 2))
            self.client.recv(1024)


if __name__ == "__main__":
    unittest.main(warnings="ignore")
