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
#login TODO- if you login and you hvave undelivered messages, want to send those

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

  def getPassword(self):
    return self.password

  def getMessages(self):
    return self.messages

  def emptyMessages(self):
    self.messages = []

  def addMessage(self, message_tuple):
    self.messages.append(message_tuple)

  #helper function to create an account
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

    # check if pwd_input = password
    #while pwd_input != self.password:
    #  pwd_input = input("""
    #  Please enter your password to log in: 
    #  """)
    #print(pwd_input, self.password)
    #if pwd_input == self.password:
      # once you get to pwd_input = password, you have logged in. Send confirmation to server.
      #print("pwd found!!!")
      #message = "True"
      #self.client.sendto(message.encode(), (host, port))


    while data != 'You have logged in. Thank you!':
      
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
    if data == 'You have logged in. Thank you!':
      print("Successfully logged in.")
      self.logged_in = True
      self.username = message





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

      #handle initial information flow- either will login or create a new account
      
      #You need to either log in or create first
      while not self.logged_in:
        #handle initial information flow- either will login or create a new account
        message = input("""
        Welcome!
        Type 'login' to log into your account.
        Type 'create' to create a new account.
        Type 'exit' to disconnect from server/log out.
        Type 'delete' to delete your account.
        """)

        #login function
        if message.lower().strip()[:5] == 'login':
          self.login_client_account(message, host, port)
          break

        #create function
        elif message.lower().strip() == 'create':
          print("create_client")
          self.create_client_username(message, host, port)
      
        #exit function- may want to exit early
        elif message.lower().strip() == 'exit':
          print(f'Connection closed.')
          self.client.close()
          self.logged_in = False
          break
        
        #if it is none of these key words, it will re query until you enter 'login' or 'create'

      # can only enter loop if you are logged in
      if self.logged_in:

        message = input("To send a message, enter the recipient username or 'exit' to leave program or 'delete' to delete your account: ")
        
        #now, allow the client + server to interact until it says to exit
        #message = input('Reply to server: ')
        
        #continue 
        while message.strip() != 'exit':

          #delete account function
          if message.lower().strip() == 'delete':
            print("delete client")
            self.delete_client_account(message, host, port)
            break

          # if they ask to create or delete given that you are currently logged in, throw an error
          elif message.lower().strip() == 'create':
            print("Error: you must log out before creating a new account. Type 'log out' to proceed.")

          # if they ask to create or delete given that you are currently logged in, throw an error
          elif message.lower().strip() == 'login':
            print("Error: you are currently logged in to an account. Type 'log out' to proceed and then log into another account.")

          else:
            # send the message to recipient
            self.client.sendto(('sendmsg' + message).encode(), (host, port))
            data = self.client.recv(1024).decode()

            # if username is found, server will return 'User found. What is your message: '
            if data == "User found. Please enter your message: ":
              message = input(data)

            
            # while loop to keep sending messages to this person until you enter 'stop'
              #while message[4: ] != "stop":

            # then want to send message to person 

            # receive confirmation that it was sent 


            # if username is not found, server will say 'User not found'.

            # re prompt message

            print('Message from server: ' + data)
          
          message = input("To send a message, enter the recipient username or 'exit' to leave program or 'delete' to delete your account: ")

        self.logged_in = False
        print(f'Connection closed.')
        self.client.close()

if __name__ == '__main__':
  socket = ClientSocket()
  socket.client_program()