"""
Configuration (BEFORE RUNNING `python3 test_client.py`)
In a separate terminal run `python3 run_server.py` and wait for 'Server is active'.

Now, run `python3 test_client.py` in another terminal. 

"""

import os
import socket
import math
import time
import uuid
import uuid
import unittest
from run_client import ClientSocket
from run_server import Server
#from grpc_client import ClientSocket

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

    # testing our create account function
    def test_create_account(self):
        # test create- see if the username + password are properly updated
        print("Testing the CREATE function")
        # creating the test user client account
        created_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        self.assertEqual(created_username, self.client_socket.getUsername())
        self.assertEqual(expected_password, self.client_socket.getPassword())

       
    # testing our login account function
    def test_login_account(self):
        print("Testing the LOGIN function")
        # test will only pass if you enter the correct password- try it out!
        # want to exit out of the account to see whether that works
        # creating the test user client account
        created_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        print("Username is:", created_username)
        # log out of the account
        self.client_socket.client.send('exit'.encode())

        # log into the account
        username_logged_into = self.client_socket.login_client_account("login", set_host, set_port, usrname_input=created_username, pwd_input=expected_password)
        self.assertEqual(created_username, username_logged_into)

    # testing logging into an account with an incorrect password
    def test_incorrect_login_password(self):
        print('Testing the LOGIN function - incorrect password')
        # test will only pass if you enter an incorrect password- try it out!
        # want to exit out of the account to see whether that works
        # creating the test user client account
        created_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        print("Username is:", created_username)
        # log out of the account
        self.client_socket.client.send('exit'.encode())

        # fail the log attempt into the account
        login_status, _ = self.client_socket.send_login_information("login", set_host, set_port, usrname_input=created_username, pwd_input="h")
        self.assertEqual(login_status, False)

    # testing logging into an account with an incorrect username
    def test_incorrect_login_username(self):
        print('Testing the LOGIN function - incorrect username')
        # test will only pass if you enter an incorrect password- try it out!
        # want to exit out of the account to see whether that works
        # creating the test user client account
        created_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        print("Username is:", created_username)
        # log out of the account
        self.client_socket.client.send('exit'.encode())

        # fail the log attempt into the account
        login_status, _ = self.client_socket.send_login_information("login", set_host, set_port, usrname_input="bogus_username", pwd_input=expected_password)
        self.assertEqual(login_status, False)

    # testing exiting/logging out from your account
    def test_exit_account(self):
        print('Testing the EXIT function')
        # assert that after we have created an account, we can successfully log out/exit.
        self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        self.assertEqual(self.client_socket.client_exit(), True)

    # testing deleting your account
    def test_delete_account(self):
        print("Testing the DELETE function")
        # assert that after we have created an account, it is deleted (returns True)
        # creating the test user client account
        self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        self.assertEqual(self.client_socket.delete_client_account(set_host, set_port), True)
    
    # testing sending messages yourself
    def test_send_messages_to_self(self):
        print("Testing the SEND MESSAGE function to yourself. ")
        # create a new user
        sender_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        # send message to yourself
        confirmation_from_server = self.client_socket.send_message(sender_username, set_host, set_port, msg_content=msg_content)
        # see if the message was delivered as expected
        expected_confirmation = "Delivered message '" + msg_content + " ...' to " + sender_username + " from " + sender_username
        self.assertEqual(confirmation_from_server, expected_confirmation)

    # testing recieving messages from yourself
    def test_receive_messages_to_self(self):
        print("Testing the RECEIVE MESSAGE function to yourself.")
        
        # create a new test user
        curr_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        
        # send message to yourself
        self.client_socket.send_message(curr_username, set_host, set_port, msg_content=msg_content)
        
        # see if the message is received from the server
        confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
        expected_confirmation = "we_love_cs262" + curr_username + "abc"
        self.assertEqual(confirmation_from_server, expected_confirmation)

    # testing sending messages to another account
    def test_send_messages_to_others(self):
        print("Testing the SEND MESSAGE function to another client.")
        # creating the test user client account
        sender_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        time.sleep(1)

        # make other client
        other_client = ClientSocket()
        other_client.client.connect((set_host, set_port))
        other_username = other_client.create_client_username(set_host, set_port, pwd_client=expected_password)
       
        # comparing the confirmation from the server with expected confirmation
        confirmation_from_server = self.client_socket.send_message(other_username, set_host, set_port, msg_content=msg_content)
        expected_confirmation = "Delivered message '" + msg_content + " ...' to " + other_username + " from " + sender_username
        self.assertEqual(confirmation_from_server, expected_confirmation)
        # exit other socket
        other_client.client_exit()

    # testing receiving messages from another account
    def test_receive_messages_from_others(self):
        print("Testing the RECEIVE MESSAGE function to another client.")
        # creating the test user client recipient
        recipient_username = self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        time.sleep(1)

        # make other client
        other_client = ClientSocket()
        other_client.client.connect((set_host, set_port))
        other_username = other_client.create_client_username(set_host, set_port, pwd_client=expected_password)
        # send message to recipient
        other_client.send_message(recipient_username, set_host, set_port, msg_content=msg_content)
        time.sleep(1)

        # confirmation you expect to receive from the server
        confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
        expected_confirmation = "we_love_cs262" + other_username + "abc"
        self.assertEqual(confirmation_from_server, expected_confirmation)

        # exit other socket
        other_client.client_exit()

    # testing sending messages to an account that does not exist
    def test_send_messages_to_nonexistent_user(self):
        print("Testing the SEND MESSAGE function to a nonexistent client username.")
        # creating the test user client account to send messages from
        self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        time.sleep(1)

        # create nonexistent client username
        nonexistent_username = "nonexistent_client_username"

        # expected confirmation from the server
        confirmation_from_server = self.client_socket.send_message(nonexistent_username, set_host, set_port, msg_content=msg_content)
        expected_confirmation = "User not found."
        self.assertEqual(confirmation_from_server, expected_confirmation)

    # testing receiving messages with no available messages
    def test_receive_empty_messages(self):
        print("Testing the RECEIVE MESSAGE function with no available messages.")
        # creating the test user client account to get messages for
        self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        time.sleep(1)

        # confirmation you expect to receive 
        confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
        expected_confirmation = "No messages available"
        self.assertEqual(confirmation_from_server, expected_confirmation)

    # testing the view all accounts function
    def test_view_account_list(self):
        print("Testing the VIEW ACCOUNTS function")
        # creating the test user
        self.client_socket.create_client_username(set_host, set_port, pwd_client=expected_password)
        
        # getting the list of all accounts 
        list_of_accounts = self.client_socket.list_accounts("listaccts", set_host, set_port)
        
        # checking if the test user exists in the account list
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