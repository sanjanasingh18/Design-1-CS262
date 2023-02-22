"""
Run  `python3 test_server.py`

Instructions: 
Once this file has printed 'Server is active'. 

In two separate terminals, run `python3 run_client.py` and create an account in each terminal.
We will use that to test the server-client interactions.

Instruction: when prompted for a password, enter 'hi'.
Needed to test the login function.

READ CAREFULLY, take your time. 
You can ignore the unclosed socket.socket warning :) 

"""

import os
import socket
import math
import time
import uuid
import unittest
from run_server import Server

# https://docs.python.org/2/library/unittest.html from section 25.3.1 
# Adapted from section 25.3.4

set_port = 8887
set_host = ''

class SimpleServerTestCase(unittest.TestCase):
    #create only one instance to avoid multiple instantiations
    def setUp(self):
        self.server_instance = Server()

        #set up host, port, create connection
        host = ''
        port = 8887
        self.server_instance.server.bind((host, port))
        print('Server is active.')

        # accept incoming connections
        self.server_instance.server.listen()
        conn, addr = self.server_instance.server.accept()

    def tearDown(self):
        #conn.close()
        print('shut downwnn')
    
    def test_create_account(self):
       # test create- see if the username + password are properly updated
        print("Testing the CREATE function")
        created_username = self.server_instance.create_username(set_host, set_port, conn)
    #     created_username = self.client_socket.create_client_username("create", set_host, set_port)
    #     self.assertEqual(created_username, self.client_socket.getUsername())
    #     self.assertEqual(expected_password, self.client_socket.getPassword())

       
    # def test_login_account(self):
    #     print("Testing the LOGIN function")
    #     # test will only pass if you enter the correct password- try it out!
    #     # want to exit out of the account to see whether that works
    #     created_username = self.client_socket.create_client_username("create", set_host, set_port)
    #     print("Username is:", created_username)
    #     # log out of the account
    #     self.client_socket.client.send('exit'.encode())

    #     # log into the account
    #     username_logged_into = self.client_socket.login_client_account("login", set_host, set_port)
    #     # enter the username, password = 'hi'
    #     # if the password is wrong, it will not log in.
    #     self.assertEqual(created_username, username_logged_into)

    # def test_delete_account(self):
    #     print("Testing the DELETE function")
    #     # assert that after we have created an account, it is deleted (returns True)
    #     self.client_socket.create_client_username("create", set_host, set_port)
    #     self.assertEqual(self.client_socket.delete_client_account("delete", set_host, set_port), True)
    
    # def test_send_messages(self):
    #     print("Testing the SEND MESSAGE function. For the message, please enter 'abc'.")
    #     sender_username = self.client_socket.create_client_username("create", set_host, set_port)
    #     other_username = input("Please enter the username of the OTHER client terminal: ")
    #     confirmation_from_server = self.client_socket.send_message(other_username, set_host, set_port)
    #     expected_confirmation = "Delivered message '" + "abc" + " ...' to " + other_username + " from " + sender_username
    #     self.assertEqual(confirmation_from_server, expected_confirmation)

    # def test_receive_messages(self):
    #     print("Testing the RECEIVE MESSAGE function.")
    #     curr_username = self.client_socket.create_client_username("create", set_host, set_port)
    #     print("Your username is " + curr_username + ".")
    #     print("Please enter this username in the OTHER client terminal and send 'abc' as your message")
    #     other_username = input("Please enter the username of the OTHER client terminal: ")
    #     confirmation_from_server = self.client_socket.receive_messages(set_host, set_port)
    #     expected_confirmation = "we_love_cs262" + other_username + "abc"
    #     self.assertEqual(confirmation_from_server, expected_confirmation)

    # def test_view_account_list(self):
    #     print("Testing the VIEW ACCOUNTS function")

    #     self.client_socket.create_client_username("create", set_host, set_port)
    #     list_of_accounts = self.client_socket.list_accounts("listaccts", set_host, set_port)
    #     is_in_account_list = self.client_socket.getUsername() in list_of_accounts
    #     self.assertEqual(is_in_account_list, True)

    # def list_empty_account_test(self):
    #     #make the test where you can see that the length 
    #     #once you let users choose their username, this will be easier to test
    #     # TODO- update once we have username input
    #     self.assertEqual('[]', self.server_instance.list_accounts()[1],
    #                      'incorrect accounts available')

if __name__ == '__main__':
    unittest.main()
