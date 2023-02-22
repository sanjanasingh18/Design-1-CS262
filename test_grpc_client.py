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
import chat_pb2
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint


set_port = 8888
set_host = ''
expected_password = "hi"
msg_content = "abc"

def encode_varint(value):
  """ Encode an int as a protobuf varint """
  data = []
  _VarintEncoder()(data.append, value, False)
  return b''.join(data)

def send_message(conn, msg):
    """ Send a message, prefixed with its size, to a TPC/IP socket """
    data = msg.SerializeToString()
    size = encode_varint(len(data))
    conn.sendall(size + data)

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
        client_buf = chat_pb2.Data()
        
        # creating the test user client account
        created_username = self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        self.assertEqual(created_username, self.client_socket.getUsername())
        self.assertEqual(expected_password, self.client_socket.getPassword())

    # testing our login account function
    def test_login_account(self):
        print("Testing the LOGIN function")
        # test will only pass if you enter the correct password- try it out!
        # want to exit out of the account to see whether that works
        client_buf = chat_pb2.Data()

        # creating the test user client account
        created_username = self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        print("Username is:", created_username)

        # log out of the account
        client_buf.action = 'exit'
        send_message(self.client_socket.client, client_buf)

        # log into the account
        username_logged_into = self.client_socket.login_client_account(client_buf, username_input=created_username, pwd_input=expected_password)
        self.assertEqual(created_username, username_logged_into)

    # testing logging out/exiting your account
    def test_exit_account(self):
        client_buf = chat_pb2.Data()
        # creating the test user client
        self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        
        # test that log out of the account returns True
        self.assertEqual(self.client_socket.client_exit(), True)
    

    # testing deleting your account
    def test_delete_account(self):
        print("Testing the DELETE function")
        client_buf = chat_pb2.Data()
        # assert that after we have created an account, it is deleted (returns True)
        self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        self.assertEqual(self.client_socket.delete_client_account(client_buf), True)
    
    # test sending a message to yourself
    def test_send_messages_to_myself(self):
        print("Testing the SEND MESSAGE function. ")
        client_buf = chat_pb2.Data()
        # creating a test user sender
        sender_username = self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        
        # send message to yourself
        confirmation_from_server = self.client_socket.send_messages(client_buf, sender_username, msg_content=msg_content)
        
        # see if the message was delivered as expected
        expected_confirmation = "Delivered message '" + msg_content + " ...' to " + sender_username + " from " + sender_username
        self.assertEqual(confirmation_from_server, expected_confirmation)
    
    # testing recieving messages from yourself
    def test_receive_messages_to_myself(self):
        print("Testing the RECEIVE MESSAGE function.")
        client_buf = chat_pb2.Data()
        curr_username = self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        
        # send message to yourself
        self.client_socket.send_messages(client_buf, curr_username, msg_content=msg_content)
       
        # see if the message is received
        confirmation_from_server = self.client_socket.receive_messages(client_buf)
        expected_confirmation = "we_love_cs262" + curr_username + "abc"
        self.assertEqual(confirmation_from_server, expected_confirmation)
    
    # testing sending messages to another account
    def test_send_messages_to_others(self):
        print("Testing the SEND MESSAGE function to another client.")
        client_buf = chat_pb2.Data()
        sender_username = self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        time.sleep(1)

        # make other client
        other_client = ClientSocket()
        other_client.client.connect((set_host, set_port))
        other_username = other_client.create_client_username(client_buf, pwd_client=expected_password)

        # comparing the confirmation from the server with expected confirmation
        confirmation_from_server = self.client_socket.send_messages(client_buf, other_username, msg_content=msg_content)
        expected_confirmation = "Delivered message '" + msg_content + " ...' to " + other_username + " from " + sender_username
        self.assertEqual(confirmation_from_server, expected_confirmation)
        # exit other socket
        self.client_socket.client_exit()

    # testing receiving messages from another account
    def test_receive_messages_from_others(self):
        print("Testing the RECEIVE MESSAGE function to another client.")
        client_buf = chat_pb2.Data()

        # creating a test user recipient
        recipient_username = self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        time.sleep(1)

        # make other client
        other_client = ClientSocket()
        other_client.client.connect((set_host, set_port))
        other_username = other_client.create_client_username(client_buf, pwd_client=expected_password)
        # send message to recipient
        other_client.send_messages(client_buf, recipient_username, msg_content=msg_content)
        time.sleep(1)

        # confirmation you expect to receive 
        confirmation_from_server = self.client_socket.receive_messages(client_buf)
        expected_confirmation = "we_love_cs262" + other_username + "abc"
        self.assertEqual(confirmation_from_server, expected_confirmation)

        # log out of the other_client account
        self.client_socket.client_exit()

    # testing sending messages to an account that does not exist
    def test_send_messages_to_nonexistent_user(self):
        print("Testing the SEND MESSAGE function to a nonexistent client username.")
        client_buf = chat_pb2.Data()

        # creating a test user client
        self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        time.sleep(1)

        # create nonexistent client username
        nonexistent_username = "nonexistent_client_username"

        # comparing the confirmation from the server with expected confirmation
        confirmation_from_server = self.client_socket.send_messages(client_buf, nonexistent_username, msg_content=msg_content)
        expected_confirmation = "User not found."
        self.assertEqual(confirmation_from_server, expected_confirmation)
        # exit other socket
        self.client_socket.client_exit()

    # testing receiving messages with no available messages
    def test_receive_empty_messages(self):
        print("Testing the RECEIVE MESSAGE function with no available messages.")
        client_buf = chat_pb2.Data()
        self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
        time.sleep(1)

        # confirmation you expect to receive from server
        confirmation_from_server = self.client_socket.receive_messages(client_buf)
        expected_confirmation = "No messages available"
        self.assertEqual(confirmation_from_server, expected_confirmation)

        # log out of the other_client account
        self.client_socket.client_exit()

    # testing the view all accounts function
    def test_view_account_list(self):
        print("Testing the VIEW ACCOUNTS function")
        client_buf = chat_pb2.Data()
        
        # creating the test user
        self.client_socket.create_client_username(client_buf, pwd_client=expected_password)
       
        # getting the list of all accounts 
        list_of_accounts = self.client_socket.list_accounts(client_buf)
        
        # checking if the test user exists in the account list
        is_in_account_list = self.client_socket.getUsername() in list_of_accounts
        self.assertEqual(is_in_account_list, True)


if __name__ == '__main__':
    unittest.main()