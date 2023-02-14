import os
import pandas as pd
import socket
import math
import time
import uuid

set_port = 8887
#[uuid: account info ]

#account info is an object
#recipients: queue of undelivered messages, logged in or not 
#login TODO- if you login and you have undelivered messages, want to send those

#this source code from https://docs.python.org/3/howto/sockets.html


class ClientSocket:

  def __init__(self, client=None):
    # we store if the client is currently logged in, their username, password, and 
    # queue of messages that they want to receive
    # all of these objects are stored in a dictionary on the server of username : ClientSocket object

    self.logged_in = False
    self.username = ''
    self.password = ''
    self.messages = []

    if client is None:
      self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
      self.client = client

  # basic get/set

  def getStatus(self):
    return self.logged_in

  def setStatus(self, update_status):
    self.logged_in = update_status

  def getUsername(self):
    return self.username

  def getPassword(self):
    return self.password

  def setPassword(self, password):
    self.password = password

  def getMessages(self):
    return self.messages

  def emptyMessages(self):
    self.messages = []

  def addMessage(self, message_string):
    self.messages.append(message_string)


  # helper function to create an account
  def create_client_username(self, message, host, port):
    self.client.sendto(message.encode(), (host, port))
    data = self.client.recv(1024).decode()
    # update object attributes
    self.username = data
    self.logged_in = True
    print('Your unique username is '  + data)

    # add a password input
    pwd_client = input('Enter password: ')

    # update the password in the client side
    self.password = pwd_client

    self.client.sendto((pwd_client).encode(), (host, port))

    confirmation_from_server = self.client.recv(1024).decode()
    print(confirmation_from_server)


  def parse_live_message(self, message):
    # message format is senderUUID_message
    # UUID is 36 characters total
    # you are not allowed to encode tuples; thus, use string format
    # return is of the format (sender UUID, message)
    return (message[:36], message[36:])


  # helper function to login to a client account
  def login_client_account(self, message, host, port):

    # ensure that the server knows that it is the login function
    self.client.sendto(message.encode(), (host, port))

    print("login client account")
    message = input("""
    Please enter your username to log in: 
    """)
    # send over the username to the server
    self.client.sendto(message.encode(), (host, port))

    # will receive back confirmation that username was sent successfully
    data = self.client.recv(1024).decode()

    pwd_input = input("""
    Please enter your password to log in: 
    """)

    # in the loop, send the password to the server
    self.client.sendto(pwd_input.encode(), (host, port))

    data = self.client.recv(1024).decode()
    print(data, 'output')
    while data[:30] != 'You have logged in. Thank you!':
      
      # allow them to exit
      message = input("""We were unable to find an account associated with that username and password combination.
      Please type either 'create' to create a new account,
      'exit' to close the server connection/log out, 
      or type 'login' to attempt to log in again.
      """)
      # exit- close the connection
      if message.lower().strip() == 'exit':
        print(f'Connection closed.')
        self.logged_in = False
        self.client.close()
        break
      elif message.lower().strip() == 'create':
        self.create_client_username(message, host, port)
        break
      else: 
        # requery the client to see if this was a successful username
        # send over the username to the client
        # prompt the server to look again for login
        # the user will send over their username so we want to prompt the server
        # to anticipate the login input folowed y 
        inform_status = 'login' + message
        self.client.sendto(inform_status.encode(), (host, port))

        # this was prior.
        # will receive back confrmation that you logged in successfully
        # data = self.client.recv(1024).decode()
        message = input("""
        Please enter your username to log in: 
        """)
        # send over the username to the server
        self.client.sendto(message.encode(), (host, port))

        # will receive back confirmation that username was sent successfully
        data = self.client.recv(1024).decode()

        pwd_input = input("""
        Please enter your password to log in: 
        """)

        # in the loop, send the password to the server
        self.client.sendto(pwd_input.encode(), (host, port))

        data = self.client.recv(1024).decode()
    
    # can exit while loop on success (logged in) or on a break 
    if data[:30] == 'You have logged in. Thank you!':
      print("Successfully logged in.")
      self.logged_in = True
      self.username = message

      available_msgs = data[30:].split('sanj<3soph')[1:]
      
      # want to receive all undelivered messages
      for received_msg in available_msgs:
        # get Messages() has 
        sender_username, msg = self.parse_live_message(received_msg)
        print("Message from " + sender_username + ": " + msg)
      

  def delete_client_account(self, message, host, port):

    # send a message that is 'delete' followed by the username to be parsed by the other side
    # we do not have a confirmation to delete as it takes effort to type 'delete' so it is difficult
    # to happen by accident

    message = "delete" + str(self.username)
    self.client.sendto(message.encode(), (host, port))
    
    #server sends back status of whether it worked
    data = self.client.recv(1024).decode()
    if data == 'Account successfully deleted.':
      self.logged_in = False
      print("Successfully deleted account.")
    else:
      print("Unsuccessfully deleted account.")


  def client_program(self):
      # host = socket.
      # host = 'dhcp-10-250-7-238.harvard.edu'
      host = ''
      port = set_port

      # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      # client.connect((host, port))
      self.client.connect((host, port))

      # handle initial information flow- either will login or create a new account
      
      # You need to either log in or create first
      while not self.logged_in:
        # handle initial information flow- either will login or create a new account
        message = input("""
        Welcome!
        Type 'login' to log into your account.
        Type 'create' to create a new account.
        Type 'exit' to disconnect from server/log out.
        """)

        # login function
        if message.lower().strip()[:5] == 'login':
          self.login_client_account(message, host, port)
          break

        # create function
        elif message.lower().strip() == 'create':
          self.create_client_username(message, host, port)
      
        # exit function- may want to exit early
        elif message.lower().strip() == 'exit':
          print(f'Connection closed.')
          self.client.close()
          self.logged_in = False
          break
        
        # if it is none of these key words, it will re query until you enter 'login' or 'create'

      # can only enter loop if you are logged in
      if self.logged_in:

        message = input("""
        To send a message, enter the recipient username, 
        'listaccts' to list all active usernames, 
        'exit' to leave program, or 
        'delete' to delete your account: 
        """)
        
        # continue until client asks to exit
        while message.strip() != 'exit':

          # delete account function
          if message.lower().strip() == 'delete':
            self.delete_client_account(message, host, port)
            break

          # if they ask to create or delete given that you are currently logged in, throw an error
          elif message.lower().strip() == 'create':
            print("Error: you must log out before creating a new account. Type 'log out' to proceed.")

          # if they ask to create or delete given that you are currently logged in, throw an error
          elif message.lower().strip() == 'login':
            print("Error: you are currently logged in to an account. Type 'log out' to proceed and then log into another account.")

          # list all account usernames
          elif message.lower().strip() == 'listaccts':
            self.client.sendto(message.lower().strip().encode(), (host, port))
            data = self.client.recv(1024).decode()
            print('Usernames: ' + data)

          # send message otherwise
          else:
            self.client.sendto(('sendmsg' + self.getUsername() + "_" + message).encode(), (host, port))
            data = self.client.recv(1024).decode()

            # if username is found, server will return 'User found. What is your message: '
            if data == "User found. Please enter your message: ":
              message = input(data)
              self.client.sendto(message.encode(), (host, port))
              # receive confirmation from the server that it was delivered
              data = self.client.recv(1024).decode()

            # COMMENT: message from server was there because before it was client- server interaction
            # now, we do not need to get the server to reprompt the client with something
            # will we ever need 
            print('Message from server: ' + data)
          
          message = input("To send a message, enter the recipient username or 'exit' to leave program or 'delete' to delete your account: ")

        self.logged_in = False
        print(f'Connection closed.')
        self.client.close()


if __name__ == '__main__':
  socket = ClientSocket()
  socket.client_program()