import os
import pandas as pd
import socket
import math
import time
import uuid
from _thread import *
import threading
from run_client import ClientSocket

set_port = 8888
set_host = ''
# set_host = 'dhcp-10-250-7-238.harvard.edu'

#this source code from https://docs.python.org/3/howto/sockets.html

class Server:
    curr_user = ''

    def __init__(self, sock=None):
        # want to set up a server socket as we did with the sample code
        # want to create a list of accounts for this server and unsent messages

        # format of account_list is [UUID: ClientObject]
        self.account_list = dict()
        
        # mutex lock so only one thread can access account_list at a given time
        # need this to be a recursive mutex as some subfunctions call on lock on top of a locked function
        self.account_list_lock = threading.RLock()

        if sock is None:
            self.server = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server = sock


    def is_username_valid(self, recipient_username):
        # cannot be in account_list (must be a unique username)
        # TODO- lock mutex
        self.account_list_lock.acquire()
        result =  recipient_username in self.account_list
        # TODO- unlock mutex
        self.account_list_lock.release()
        return result


    # if the recipient isn't logged in, add the message to the queue
    def add_message_to_queue(self, sender_username, recipient_username, message):
        # queue format is strings of sender_username + "" + message
        message_string = sender_username + message
        # TODO- lock mutex
        self.account_list_lock.acquire()
        self.account_list.get(recipient_username).addMessage(message_string)
        # TODO- unlock mutex
        self.account_list_lock.release()


    # returns True upon successful delivery. returns False if it fails.
    def deliver_message(self, sender_username, recipient_username, host, port, conn):
        # If username is invalid, throw error message
        if not self.is_username_valid(recipient_username): #== "Recipient username is not valid.":
            recipient_not_found = "User not found."
            print(recipient_not_found)
            conn.sendto(recipient_not_found.encode(), (host, port))
            return False

        # query the client for what the message is
        confirmed_found_recipient = "User found. Please enter your message: "
        print(confirmed_found_recipient)
        conn.sendto(confirmed_found_recipient.encode(), (host, port))

        # server will receive what the message the client wants to send is 
        message = conn.recv(1024).decode()
        
        # regardless of client status (logged in or not), add the message to the recipient queue
        self.add_message_to_queue(sender_username, recipient_username, message)

        # print + deliver confirmation
        confirmation_message_sent = 'Delivered message ' + message + " to " + recipient_username + " from " + sender_username
        print(confirmation_message_sent)
        conn.sendto(confirmation_message_sent.encode(), (host, port))
        return True


    # function we use to create an account/username for a new user
    def create_username(self, host, port, conn):

        # HI- SS I went in here and cleaned up this code bc its horrible 

        # server will generate UUID, print UUID, send info to client, and then add it to the dict
        username = str(uuid.uuid4())
        print("Unique username generated for client is "+ username + ".")
        conn.sendto(username.encode(), (host, port))

        # add (username: clientSocket object where clientSocket includes log-in status,
        # username, password, and queue of undelivered messages
        # it will initialize a new account

        # TODO- lock mutex
        self.account_list_lock.acquire()
        self.account_list[username] = ClientSocket()
        # TODO- unlock mutex
        self.account_list_lock.release()

        # client will send back a password + send over confirmation
        data = conn.recv(1024).decode()
        # update the password in the object that is being stored in the dictionary

        # TODO- lock mutex
        self.account_list_lock.acquire()
        self.account_list.get(username.strip()).setPassword(data)
        # TODO- unlock mutex
        self.account_list_lock.release()

        message = "Your password is confirmed to be " + data
        conn.sendto(message.encode(), (host, port))
        
        return username

    # send messages to the client that are in the deliver queue
    def send_client_messages(self, client_username, host, port, conn, prefix=''):
        # want to receive all undelivered messages
        final_msg = prefix

        # note that we hold the mutex in this entire area- if we let go of mutex + reacquire to
        # empty messages we may obtain new messages in that time and then empty messages
        # that have not yet been read

        # TODO- lock mutex
        self.account_list_lock.acquire()
        msgs = self.account_list.get(client_username).getMessages()

        if msgs:
            str_msgs = ''
            for message in msgs:
                str_msgs += 'we_love_cs262' + message
            final_msg += str_msgs

            # clear all delivered messages as soon as possible to address concurent access
            self.account_list.get(client_username).emptyMessages()
        else:
            final_msg += "No messages available"
        # TODO- unlock mutex
        self.account_list_lock.release()

        conn.sendto(final_msg.encode(), (host, port))


    # function to log in to an account
    def login_account(self, host, port, conn):
        username = conn.recv(1024).decode()
        confirm_received = "Confirming that the username has been received."
        conn.sendto(confirm_received.encode(), (host, port))

        password = conn.recv(1024).decode()
        # ask for login and password and then verify if it works

        # TODO- lock mutex
        self.account_list_lock.acquire()
        # TODOSS- figure out where to UNLOCK mutex

        if (username.strip() in self.account_list):
            # get the password corresponding to this
            if password == self.account_list.get(username.strip()).getPassword():
                #TODO- unlock mutex
                self.account_list_lock.release()

                confirmation = 'You have logged in. Thank you!'
                self.send_client_messages(username.strip(), host, port, conn, confirmation)
                return username.strip()
                
            else:
                #TODO- unlock mutex
                self.account_list_lock.release()
                print("Account not found.")
                message = 'Error'
                conn.sendto(message.encode(), (host, port))

        elif (username.strip()[5:] in self.account_list):
            # get the password corresponding to this
            if password == self.account_list.get(username.strip()[5:]).getPassword():
                #TODO- unlock mutex
                self.account_list_lock.release()
                confirmation = 'You have logged in. Thank you!'
                self.send_client_messages(username.strip(), host, port, conn, confirmation)
                return username.strip()[5:]
            else:
                #TODO- unlock mutex
                self.account_list_lock.release()
                print("Account not found.")
                message = 'Error'
                conn.sendto(message.encode(), (host, port))

        else:
            #TODO- unlock mutex
            self.account_list_lock.release()
            # want to prompt the client to either try again or create account
            print("Account not found.")
            message = 'Error'
            conn.sendto(message.encode(), (host, port))



    def delete_account(self, username, host, port, conn):
        # TODO make protocol buffer so that every time a client send a message we send their UUID and their message
        # You can only delete your account once you are logged in so it handles undelivered messages
        if username in self.account_list:
            # check if there are any messages in the queue to be delivered
            # if so, deliver them
            del self.account_list[username]
            print("Successfully deleted client account", self.account_list)
            message = 'Account successfully deleted.'
            conn.sendto(message.encode(), (host, port))
        else:
            # want to prompt the client to either try again or create account
            message = 'Error deleting account'
            print(message)
            conn.sendto(message.encode(), (host, port))


    # function to list all active (non-deleted) accounts
    # add a return statement so it is easier to Unittest
    def list_accounts(self):

        # TODO- lock mutex 
        self.account_list_lock.acquire()       
        listed_accounts = str(list(self.account_list.keys()))
        # TODO- unlock mutex
        self.account_list_lock.release()

        return listed_accounts

    def server_to_client(self, host, conn, port):
        curr_user = ''
        while True:
            # receive from client
            data = conn.recv(1024).decode()
            
            # check if connection closed- if so, close thread
            if not data:
                # close thread
                return

            print('Message from client: ' + data)

            # check if data equals 'login'- take substring as we send login + username to server
            if data.lower().strip()[:5] == 'login':
                curr_user = self.login_account(host, port, conn)

            elif data.lower().strip()[:6] == 'create':
                curr_user = self.create_username(host, port, conn)

            # check if data equals 'delete'- take substring as we send  delete + username to server
            elif data.lower().strip()[:6] == 'delete':
                # data parsing works correctly
                # print(data, data.lower().strip(), data.lower().strip()[6:])
                self.delete_account(data.lower()[6:], host, port, conn)
                return

            # check if client request to send a message
            elif data.lower().strip()[:7] == 'sendmsg':
                # data parsing works correctly
                # print(data, data.lower().strip()[7:43], data.lower()[44:])
                self.deliver_message(data.lower().strip()[7:43], data.lower()[44:], host, port, conn)


            # check if client request is to list all accounts
            elif data.lower().strip()[:9] == 'listaccts':
                conn.sendto(self.list_accounts().encode(), (host, port))

            elif data[:8] == "msgspls!":
                self.send_client_messages(curr_user, host, port, conn)
                    
    def server_program(self):
        host = set_host
        port = set_port
        self.server.bind((host, port))
        self.server.listen()
        print('Server is active')

        # while SOMETHING, listen!
        while True:
            conn, addr = self.server.accept()

            print(f'{addr} connected to server.')

            # Start a new thread with this client
            #start_new_thread(server_to_client, (host, conn, port, ))
            curr_thread = threading.Thread(target=self.server_to_client, args=(host, conn, port,))
            curr_thread.start()

if __name__ == '__main__':
    a = Server()
    a.server_program()
