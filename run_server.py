import os
import pandas as pd
import socket
import math
import time
import uuid

#this source code from https://docs.python.org/3/howto/sockets.html

class Server:
    curr_user = ''

    def __init__(self, sock=None):
        #want to set up a server socket as we did with the sample code
        #want to create a list of accounts for this server and unsent messages

        #format of account_list is [UUID: queue of messages not yet sent]
        self.account_list = dict() #['abc'] 
        
        if sock is None:
            self.server = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server = sock

    def is_username_valid(username_candidate):
        # check if username has key words
        # cannot start with the words delete, create, login 

        # cannot be in account_list (must be a unique username)

    #function we use to create an account/username for a new user
    def create_username(self, host, port, conn):
        # server will generate UUID, print UUID, send info to client, and then add it to the dict
        username = uuid.uuid4()
        print("Unique username generated for client is "+ str(username) + ". Waiting on message from client.")
        message = str(username)
        conn.sendto(message.encode(), (host, port))

        # add (username: empty list) to dictionary
        # empty list will eventually hold the queue of messages
        self.account_list[message] = []
        curr_user = message

    #function to log in to an account
    def login_account(self, host, port, conn):
        #check if this username exists- check if it is in the account_list,         
        data = conn.recv(1024).decode()
        #workaround with the login bug
        if (data.strip() in self.account_list) or (data.strip()[5:] in self.account_list):
            print('has key!', self.account_list)
            message = 'Account has been identified. Thank you!'
            conn.sendto(message.encode(), (host, port))
        else:
            # want to prompt the client to either try again or create account
            print("key not found.")
            message = 'Error'
            conn.sendto(message.encode(), (host, port))

    def delete_account(self, username, host, port, conn):
        #TODO make protocol buffer so that every time a client send a message we send their UUID and their message
        if username in self.account_list:
            del self.account_list[username]
            print("Successfully deleted client account", self.account_list)
            message = 'Account successfully deleted.'
            conn.sendto(message.encode(), (host, port))
        else:
            # want to prompt the client to either try again or create account
            print("key not found: see current account list", self.account_list)
            message = 'Error deleting account'
            conn.sendto(message.encode(), (host, port))

    
    def deliver_message(self):
        #is the account logged in?
        #if so, deliver immediately
        print('delivered')
        #if not, add to queue 

    #function to list all active (non-deleted) accounts
    #add a return statement so it is easier to Unittest
    def list_accounts(self):
        print(self.account_list.keys())
        return self.account_list.keys()


    def server_program(self):
        #changed to the 
        #server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #used socket.gethostname() to get the host name to connect between
        #computers
        # host = 'dhcp-10-250-7-238.harvard.edu'
        host = ''
        print(host)
        port = 8887
        self.server.bind((host, port))

        #while SOMETHING, listen!
        while True:
            lst_acc_cmd = 'list accounts'
            self.server.listen()
            conn, addr = self.server.accept()

            print(f'{addr} connected to server.')

            # want to see when we have to disconnect- revise this while loop 
            # and break statement
            while True:
                # receive from client
                data = conn.recv(1024).decode()
                
                # check if connection closed
                if not data:
                    break

                print('Message from client: ' + data)

                # check if data equals 'login'- take substring as we send login + username to server
                if data.lower().strip()[:5] == 'login':
                    print('server login')
                    self.login_account(host, port, conn)
                elif data.lower().strip()[:6] == 'create':
                    self.create_username(host, port, conn)
                # check if data equals 'delete'- take substring as we send  delete + username to server
                elif data.lower().strip()[:6] == 'delete':
                    print(data, data.lower().strip(), data.lower().strip()[6:])
                    self.delete_account(data.lower()[6:], host, port, conn)
                else:
                    # allows the server to list all the accounts, once all accounts are listed, prompts 
                    # server to list all accounts again or type a message to send to client
                    message = input("Reply to client or type 'list accounts' to list all accounts: ")
                    while message.lower().strip() == lst_acc_cmd:
                        print('Account UUIDs: ' + str(list(self.account_list.keys())))
                        message = input("Reply to client or type 'list accounts' to list all accounts: ")
                    conn.sendto(message.encode(), (host, port))
            
            # need to continuously scan for 'exit' to exit the server. TODO- fix this
            message = input("Type 'exit' to close the server, 'list accounts' to list all accounts, or press enter to continue: ")
            # prompts the user for input until the server inputs exit to close or just presses
            # enter to continue
            while (message.lower().strip() != 'exit') and (message.lower().strip() != ''):
                # prints all the UUIDs stored if the server asks to list all the accounts while a client
                # is not connected.
                if message.lower().strip() == lst_acc_cmd:
                    print('Account UUIDs: ' + str(list(self.account_list.keys())))
                message = input("Type 'exit' to close the server, 'list accounts' to list all accounts, or press enter to continue: ")
            if message.lower().strip() == 'exit':
                print('You have successfully closed the server.')
                conn.close()
                break
            
        #TODO- do not want to automatically disconnect once
        #you have a client
        #while server doesn't say to EXIT

if __name__ == '__main__':
    a = Server()
    a.server_program()
