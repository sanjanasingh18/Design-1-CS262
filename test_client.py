"""
Configuration: in a separate terminal, run run_client.py and create an account.
We will use that to test the send + receive messages protocol.

Instruction: when prompted for a password, enter 'hi'.
Needed to test the login function.

READ CAREFULLY, take your time. 

"""

import os
import socket
import math
import time
import uuid
import uuid
import unittest
from run_client import ClientSocket
#from grpc_client import ClientSocket

set_port = 8886
set_host = ''
expected_password = "hi"

# https://docs.python.org/2/library/unittest.html from section 25.3.1 

class TestStringMethods(unittest.TestCase):
    #setup_done = False
    def setUp(self):
        #if TestStringMethods.setup_done:
        #    return
        #TestStringMethods.setup_done = True
        self.client_socket = ClientSocket()
        host = set_host
        port = set_port

        self.client_socket.client.connect((host, port))

    #@classmethod
    #def setupClass(self):

    def tearDown(self):
        self.client_socket.client.close()

    def test_create_account(self):
        # test create- see if the username + password are properly updated
        print("Testing the CREATE function")
        created_username = self.client_socket.create_client_username("create", set_host, set_port)
        self.assertEqual(created_username, self.client_socket.getUsername())
        self.assertEqual(expected_password, self.client_socket.getPassword())
        
    def test_login_account(self):
        print("Testing the LOGIN function")
        # test will only pass if you enter the correct password- try it out!
        # want to exit out of the account to see whether that works
        created_username = self.client_socket.create_client_username("create", set_host, set_port)
        print("Username is :", created_username)
        # log out of the account
        self.client_socket.client.send('exit'.encode())
        # log into the account
        username_logged_into = self.client_socket.login_client_account("login", set_host, set_port)
        # enter the username, password = 'hi'
        # if the password is wrong, it will not log in.
        self.assertEqual(created_username, username_logged_into)

    def test_delete_account(self):
        print("Testing the DELETE function")
        # assert that after we have created an account, it is deleted (returns True)
        created_username = self.client_socket.create_client_username("create", set_host, set_port)
        self.assertEqual(self.client_socket.delete_client_account("delete", set_host, set_port), True)
    
    def test_send_messages(self):
        print("Testing the SEND MESSAGE function")
        print('oops')


    def test_view_account_list(self):
        print("Testing the VIEW ACCOUNTS function")
        #self.assertEqual(self.client_socket.create_client_username("create", set_host, set_port), self.client_socket.getUsername())
        """self.client_socket.client.send('create'.encode())
        
        # create will send back the username
        username_from_server = self.client_socket.client.recv(1024).decode()

        # enter a password
        pwd_draft = "pwd"
        # finish information flow
        self.client_socket.client.send(pwd_draft.encode())
        self.client_socket.client.recv(1024).decode()

        # check if the username is updated for the client!
        self.assertEqual(username_from_server, self.client_socket.getUsername())"""


        #self.assertEqual("hi", self.client_socket.getPassword())

        #self.client_socket.client.send('create'.encode())
        #self.client_socket.create_client_username("create", set_host, set_port)
        #self.client_socket.client.send('create'.encode())

        #username_from_server = self.client_socket.client.recv(1024).decode()
        # enter a password
        #pwd_draft = "pwd"
        #self.client_socket.client.send(pwd_draft.encode())
        #expected_pwd_message = "Your password is confirmed to be " + pwd_draft
        #self.assertEqual(self.client_socket.client.recv(1024).decode(), expected_pwd_message)

    #def test_2(self):
        #self.client_socket.client.send('message2'.encode())
        #self.assertEqual(self.client_socket.client.recv(1024).decode(), 'reply2')

if __name__ == '__main__':
    unittest.main()