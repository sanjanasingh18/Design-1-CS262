import os
import pandas as pd
import socket
import math
import time
import uuid

clientsocket has a clientinfo object

good fit for a dictionary

dictionary would be on server

#[uuid: account info ]

#account info is an object
#recipients: queue of undelivered messages, logged in or not 
#login TODO- if you login and you hvave undelivered messages, want to send those

#this source code from https://docs.python.org/3/howto/sockets.html

class ClientInfo:

  def __init__(self):
    # In ClientSocket, objects are username: [ClientInfo]
    self.login_status = False
    self.messages = []

  def getStatus(self):
    return self.login_status

  def setStatus(self, update_status):
    self.login_status = update_status
  
  def getMessages(self):
    return self.messages

  def emptyMessages(self):
    self.messages = []

  def addMessage(self, message):
    self.messages.append(message)


class ClientSocket:

  def __init__(self, client=None):
    # add an is_logged_in object for the account
    self.logged_in = False

    self.username = ''

    if client is None:
      self.client = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
    else:
      self.client = client

  #helper function to create an account
  def create_client_username(self, message, host, port):
    self.client.sendto(message.encode(), (host, port))
    data = self.client.recv(1024).decode()
    # update object attributes
    self.username = data
    print('updated username: ', self.username)
    self.logged_in = True
    print('Your unique username is '  + data)

  #helper function to login to a client account
  def login_client_account(self, message, host, port):

    #ensure that the server knows that it is the login function
    self.client.sendto(message.encode(), (host, port))

    print("login client account")
    message = input("""
    Please enter your username to log in: 
    """)
    possible_username = message
    #send over the username to the client
    self.client.sendto(message.encode(), (host, port))

    #will receive back confrmation that you logged in successfully
    data = self.client.recv(1024).decode()

    while data != 'Account has been identified. Thank you!':
      
      #allow them to exit
      message = input("""We were unable to find an account associated with that username.
      Please type either 'create' to create a new account,
      'exit' to close the server connection/log out, 
      or re-enter your username.
      """)
      #exit- close the connection
      if message.lower().strip() == 'exit':
        print(f'Connection closed.')
        self.logged_in = False
        self.client.close()
        break
      elif message.lower().strip() == 'create':
        self.create_client_username(message, host, port)
        break
      else: 
        #requery the client to see if this was a successful username
        #send over the username to the client
        #prompt the server to look again for login
        inform_status = 'login' + message
        self.client.sendto(inform_status.encode(), (host, port))

        #will receive back confrmation that you logged in successfully
        data = self.client.recv(1024).decode()
    
    # can exit while loop on success (logged in) or on a break 
    if data == 'Account has been identified. Thank you!':
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
      port = 8887

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

        message = input("Enter recipient username or 'exit' to leave program or 'delete' to delete your acount: ")
        
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
              while message[4: ]
            # then want to send message to person 

            # receive confirmation that it was sent 


            # if username is not found, server will say 'User not found'.

            # re prompt message

            print('Message from server: ' + data)
          
          message = input("Enter recipient username or 'exit' to leave program or 'delete' to delete your acount: ")

        self.logged_in = False
        print(f'Connection closed.')
        self.client.close()

if __name__ == '__main__':
  socket = ClientSocket()
  socket.client_program()