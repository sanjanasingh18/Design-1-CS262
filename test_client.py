import os
import socket
import math
import time
import uuid
import uuid
import unittest
from run_client import ClientSocket

set_port = 8886
set_host = ''

# https://docs.python.org/2/library/unittest.html from section 25.3.1 

class TestStringMethods(unittest.TestCase):

    def setUp(self):

        self.client_socket = ClientSocket()
        host = set_host
        port = set_port

        self.client_socket.client.connect((host, port))

    def tearDown(self):
        self.client_socket.client.close()

    def test_1(self):
        self.client_socket.client.send('message1'.encode())
        self.assertEqual(self.client_socket.client.recv(1024).decode(), 'reply1')

    def test_2(self):
        self.client_socket.client.send('message2'.encode())
        self.assertEqual(self.client_socket.client.recv(1024).decode(), 'reply2')

if __name__ == '__main__':
    unittest.main()