import os
import pandas as pd
import socket
import math
import time
import uuid
from run_client import ClientSocket

set_port = 8887
#this source code from https://docs.python.org/3/howto/sockets.html

class Server:
    curr_user = ''

    def __init__(self, sock=None):
        #want to set up a server socket as we did with the sample code
        #want to create a list of accounts for this server and unsent messages

        #format of account_list is [UUID: ClientObject]
        self.account_list = dict()
        
        if sock is None:
            self.server = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server = sock

    def is_username_valid(self, recipient_username):
        # cannot be in account_list (must be a unique username)
        return recipient_username in self.account_list

    
    # function to get a user's login status from the account_list
    def get_user_status(self, username):
        # check if the username is valid
        if self.is_username_valid(username):
            # get the object then access the user status usign getStatus()
            return self.account_list.get(username).getStatus()
        
        # if the username is invalid, return error
        return "Recipient username is not valid."


    # if the recipient isn't logged in, add the message to the queue
    def add_message_to_queue(self, sender_username, recipient_username, message):
        # queue format is tuples of (sender_username, message)
        self.account_list.get(recipient_username).addMessage(self, (sender_username, message))


    # returns True upon successful delivery. returns False if it fails.
    def deliver_message(self, sender_username, recipient_username, message, host, port, conn):
        # is the recipient account logged in?
        user_status = self.get_user_status(recipient_username)
        if user_status:
            # if so, deliver immediately
            message_to_recipient = sender_username + "_" + message

            # what if both accounts are logged in??? who is this sending it to 
            # TODO - answer this question ^
            conn.sendto(message_to_recipient.encode(), (host, port))
            
            print('Delivered message ' + message + " to " + recipient_username + " from " + sender_username)

        # Checks if it is sent to a valid user
        elif user_status == "Recipient username is not valid.":
            return False

        # if not logged in, add to recipient queue
        else:
            # add to queue for recipient
            self.add_message_to_queue(sender_username, recipient_username, message)
            return True


    # function we use to create an account/username for a new user
    def create_username(self, host, port, conn):
        # server will generate UUID, print UUID, send info to client, and then add it to the dict
        username = uuid.uuid4()
        print("Unique username generated for client is "+ str(username) + ".")
        message = str(username)
        conn.sendto(message.encode(), (host, port))

        # add (username: clientSocket object where clientSocket includes log-in status,
        # username, password, and queue of undelivered messages
        # it will initialize a new account
        self.account_list[message] = ClientSocket()

        # client will send back a password + send over confirmation
        data = conn.recv(1024).decode()
        message = "Your password is confirmed to be " + data
        conn.sendto(message.encode(), (host, port))

    #function to log in to an account
    def login_account(self, host, port, conn):
        username = conn.recv(1024).decode()

        confirm_received = "Confirming that the username has been received."
        conn.sendto(confirm_received.encode(), (host, port))

        password = conn.recv(1024).decode()
        # ask for login and password and then verify if it works
        if (username.strip() in self.account_list):
            # get the password corresponding to this
            print("Username found")

            # TODO issue- get password keeps coming out blank. help!!!
            
            print(self.account_list.get(username.strip()).getPassword(), "pwd")
            if password == self.account_list.get(username.strip()).getPassword():
                message = 'You have logged in. Thank you!'
                print(message)
                conn.sendto(message.encode(), (host, port))
            else:
                print("PWD NOT FOUND- this is a temp print statment for debugging")
                print("Account not found.")
                message = 'Error'
                conn.sendto(message.encode(), (host, port))

        elif (username.strip()[5:] in self.account_list):
            # get the password corresponding to this
            print("Username 5 found")

            # TODO issue- get password keeps coming out blank. help!!!

            print(self.account_list.get(username.strip()).getPassword(), "pwd")
            if password == self.account_list.get(username.strip()[5:]).getPassword():
                message = 'You have logged in. Thank you!'
                print(message)
                conn.sendto(message.encode(), (host, port))
            else:
                print("PWD NOT FOUND- this is a temp print statment for debugging")
                print("Account not found.")
                message = 'Error'
                conn.sendto(message.encode(), (host, port))

        else:
            # want to prompt the client to either try again or create account
            print("username not found- this is a temp print statment for debugging")
            print("Account not found.")
            message = 'Error'
            conn.sendto(message.encode(), (host, port))

        """    
        # check if this username exists- check if it is in the account_list,         
        data = conn.recv(1024).decode()
        # workaround with the login bug

        
        if (data.strip() in self.account_list) or (data.strip()[5:] in self.account_list):
            print('has key!', self.account_list)
            message = 'Account has been identified. Thank you!'
            conn.sendto(message.encode(), (host, port))
            
            print('sent msg to client')
            # wait to confirmation that password worked
            password_valid = conn.recv(1024).decode()

            # need to check the server's record of the client password here
            clie
            print(password_valid)
            if password_valid == "True":
                message = 'You have logged in. Thank you!'
                print(message)
                conn.sendto(message.encode(), (host, port))
            
            else: 
                # want to prompt the client to either try again or create account
                print("Account not found.")
                message = 'Error'
                conn.sendto(message.encode(), (host, port))
        else:
            # want to prompt the client to either try again or create account
            print("Account not found.")
            message = 'Error'
            conn.sendto(message.encode(), (host, port))
        """

    def delete_account(self, username, host, port, conn):
        # TODO make protocol buffer so that every time a client send a message we send their UUID and their message
        # You can only delete your account once you are logged in so it handles undelivered messages
        if username in self.account_list:
            del self.account_list[username]
            print("Successfully deleted client account", self.account_list)
            message = 'Account successfully deleted.'
            conn.sendto(message.encode(), (host, port))
        else:
            # want to prompt the client to either try again or create account
            # NOTE this print statement is just internal... client will not see the account list
            #print("Key not found: see current account list", self.account_list)
            message = 'Error deleting account'
            conn.sendto(message.encode(), (host, port))


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
        port = set_port
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
            

if __name__ == '__main__':
    a = Server()
    a.server_program()
