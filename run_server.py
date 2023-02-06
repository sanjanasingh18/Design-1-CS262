import os
import pandas as pd
import socket
import math
import time
import uuid

#this source code from https://docs.python.org/3/howto/sockets.html

class Server:
    def __init__(self, sock=None):
        #want to set up a server socket as we did with the sample code
        #want to create a list of accounts for this server and unsent messages

        #format of account_list is [UUID: queue of messages not yet sent]
        self.account_list = dict()
        
        if sock is None:
            self.server = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server = sock

    #function we use to create an account/username for a new user
    def create_username(self, host, port, conn):
        # server will generate UUID, print UUID, send info to client, and then add it to the dict
        username = uuid.uuid4()
        print("Unique username generated for client is "+ str(username) + ". Waiting on message from client.")
        message = 'Your unique username is ' + str(username)
        conn.sendto(message.encode(), (host, port))

        # add (username: empty list) to dictionary
        # empty list will eventually hold the queue of messages
        self.account_list[str(username)] = []

    #function to log in to an account
    def login_account(self, host, port, conn, data):
        #message = 'Please enter your username (UUID)'
        #conn.sendto(message.encode(), (host, port))
        #check if this username exists- check if it is in the account_list, 
        data = conn.recv(1024).decode()
        if data.strip() in self.account_list:
            print('has key!')
            message = 'Account has been identified. Thank you!'
            conn.sendto(message.encode(), (host, port))
        else:
            # want to prompt the client to either try again or create account
            print("key not found.")
            message = 'Error'
            conn.sendto(message.encode(), (host, port))

    def server_program(self):
        #changed to the 
        #server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #used socket.gethostname() to get the host name to connect between
        #computers
        host = 'dhcp-10-250-7-238.harvard.edu'
        print(host)
        port = 8884
        self.server.bind((host, port))

        self.server.listen()
        conn, addr = self.server.accept()

        print(f'{addr} connected to server.')

        message = 'temporary non-null input'
        #want to see when we have to disconnect- revise this while loop 
        #and break statement
        while True:
            #receive from client
            data = conn.recv(1024).decode()
            
            #check if connection closed
            if not data:
                break

            print('Message from client: ' + data)

            #check if data equals 'login'
            if data.lower().strip() == 'login':
                print('server login')
                self.login_account(host, port, conn, data)
            elif data.lower().strip() == 'create':
                self.create_username(host, port, conn)
            else:
                message = input('Reply to client: ')
                conn.sendto(message.encode(), (host, port))
        
        #TODO- do not want to automatically disconnect once
        #you have a client
        #while server doesn't say to EXIT
        print('Client has disconnected. Closing server.')
        conn.close()
    
    def deliver_message():
        #is the account logged in?
        #if so, deliver immediately
        print('delivered')
        #if not, add to queue 

    def list_accounts(self):
        print(account_list.keys())

if __name__ == '__main__':
    a = Server()
    a.server_program()
