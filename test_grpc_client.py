"""
Configuration (BEFORE RUNNING `python3 test_client.py`)
In a separate terminal run `python3 grpc_server.py` and wait for 'Server is active'.

Now, run `python3 test_grpc_client.py` in another terminal.
"""

import os
import socket
import math
import time
import uuid
import uuid
import unittest
from grpc_client import ClientSocket

set_port = 8887
set_host = ''
expected_password = "hi"
msg_content = "abc"

# https://docs.python.org/2/library/unittest.html from section 25.3.1 

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.client_socket = ClientSocket()
        host = set_host
        port = set_port

        self.client_socket.client.connect((host, port))

    def tearDown(self):
        self.client_socket.client.close()

    def test_create_account(self):
        # test create- see if the username + password are properly updated
        print("Testing the CREATE function")
        created_username = self.client_socket.create_client_username("create", set_host, set_port, pwd_client=expected_password)
        self.assertEqual(created_username, self.client_socket.getUsername())
        self.assertEqual(expected_password, self.client_socket.getPassword())

       
    def test_login_account(self):
        print("Testing the LOGIN function")
        # test will only pass if you enter the correct password- try it out!
        # want to exit out of the account to see whether that works
        created_username = self.client_socket.create_client_username("create", set_host, set_port, pwd_client=expected_password)
        print("Username is:", created_username)
        # log out of the account
        self.client_socket.client.send('exit'.encode())

        # log into the account
        username_logged_into = self.client_socket.login_client_account("login", set_host, set_port, username_input=created_username, pwd_input=expected_password)
        self.assertEqual(created_username, username_logged_into)

    def test_delete_account(self):
        print("Testing the DELETE function")
        # assert that after we have created an account, it is deleted (returns True)
        self.client_socket.create_client_username("create", set_host, set_port, pwd_client=expected_password)
        self.assertEqual(self.client_socket.delete_client_account("delete", set_host, set_port), True)
    
    def test_send_messages(self):
        # test sending message to yourself. we were unable to 
        print("Testing the SEND MESSAGE function. ")
        sender_username = self.client_socket.create_client_username("create", set_host, set_port, pwd_client=expected_password)
        # send message to yourself
        confirmation_from_server = self.client_socket.send_message(sender_username, set_host, set_port, msg_content=msg_content)
        # see if the message was delivered as expected
        expected_confirmation = "Delivered message '" + msg_content + " ...' to " + sender_username + " from " + sender_username
        self.assertEqual(confirmation_from_server, expected_confirmation)

    def test_receive_messages(self):
        print("Testing the RECEIVE MESSAGE function.")
        curr_username = self.client_socket.create_client_username("create", set_host, set_port, pwd_client=expected_password)
        # send message to yourself
        self.client_socket.send_message(curr_username, set_host, set_port, msg_content=msg_content)
        # see if the message is received
        confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
        expected_confirmation = "we_love_cs262" + curr_username + "abc"
        self.assertEqual(confirmation_from_server, expected_confirmation)

    # this unit test is INTERACTIVE- requires an active user so we commented this out.
    # def test_send_messages_to_others(self):
    #     print("Testing the SEND MESSAGE function. For the message, please enter 'abc'.")
    #     sender_username = self.client_socket.create_client_username("create", set_host, set_port, pwd_client=expected_password)
    #     other_username = input("Please enter the username of the OTHER client terminal: ")
    #     confirmation_from_server = self.client_socket.send_message(other_username, set_host, set_port)
    #     expected_confirmation = "Delivered message '" + "abc" + " ...' to " + other_username + " from " + sender_username
    #     self.assertEqual(confirmation_from_server, expected_confirmation)

    # this unit test is INTERACTIVE- requires an active user so we commented this out.
    # def test_receive_messages_from_other(self):
    #     print("Testing the RECEIVE MESSAGE function.")
    #     curr_username = self.client_socket.create_client_username("create", set_host, set_port, pwd_client=expected_password)
    #     print("Your username is " + curr_username + ".")
    #     print("Please enter this username in the OTHER client terminal and send 'abc' as your message")
    #     other_username = input("Please enter the username of the OTHER client terminal: ")
    #     confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
    #     expected_confirmation = "we_love_cs262" + other_username + "abc"
    #     self.assertEqual(confirmation_from_server, expected_confirmation)

    def test_view_account_list(self):
        print("Testing the VIEW ACCOUNTS function")

        self.client_socket.create_client_username("create", set_host, set_port, pwd_client=expected_password)
        list_of_accounts = self.client_socket.list_accounts("listaccts", set_host, set_port)
        is_in_account_list = self.client_socket.getUsername() in list_of_accounts
        self.assertEqual(is_in_account_list, True)

        '''Tried to have two users at the same time for testing, did not work :('''
        # sender_username = self.client_socket.create_client_username("create", set_host, set_port)
        # other_object = ClientSocket()
        # other_username = other_object.create_client_username("create", set_host, set_port)
        # confirmation_from_server = self.client_socket.send_message(other_username, set_host, set_port)
        # # here you will be prompted for the message?
        # expected_confirmation = "Delivered message '" + "abc" + " ...' to " + other_username + " from " + sender_username
        # self.assertEqual(confirmation_from_server, expected_confirmation)
        # other_object.client.close()
        

if __name__ == '__main__':
    # set up the server once. This did not work, so you must run the run_server.py file separately.
    # server_instance = Server()
    # server_instance.server.bind((set_host, set_port))
    # server_instance.server.listen()
    # #conn, addr = server_instance.server.accept()
    unittest.main()