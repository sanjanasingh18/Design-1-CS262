"""Main testing script for the composite outcome experiment. Purpose is to determine whether using composite outcomes improves DL performance for prognosis

Usage:
  run_mixed.py <image_dir> <model_path> <data_frame> <output_file> [--TTA] [--mixedLayers=MIXEDLAYERS] [--conv=CONV] [--cont=CONT] [--cat=CAT] [--modelarch=MODELARCH] [--type=TYPE] [--target=TARGET] [--split=SPLIT] [--layers=LAYERS]
  run_mixed.py (-h | --help)
Examples:
  run_mixed.py /path/to/images /path/to/model /path/to/write/output.csv
Options:
  -h --help                     Show this screen.
  --modelarch=MODELARCH         CNN model architecture to train [default: inceptionv4]
  --type=TYPE                   Type of output [default: Discrete]
  --target=TARGET               If optional df is specified, then need to include the target variable [default: None]
  --split=SPLIT                 If split, then split on the Dataset column keeping only the Te values [default: False]
  --cont=CONT                   List of continuous variables to include in the tabular learner [default: None]
  --cat=CAT                     List of categorical variables to include in the tabular learner [default: None]
  --layers=LAYERS               Tabular layers [default: 32,32]
  --mixedLayers=MIXEDLAYERS     Mixed layers at the end of the network [default: 64,32,32,2]
  --conv=CONV                   Number of features produced by the CNN [default: 32]
  --TTA
"""

import os
import pandas as pd
import socket
import math
import time
import uuid


#this source code from https://docs.python.org/3/howto/sockets.html


class ClientSocket:
  # add an is_logged_in object for the account
  is_logged_in = False

  def __init__(self, client=None):
    if client is None:
      self.client = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
    else:
      self.client = client

  #helper function to create an account
  def create_client_username(self, message, host, port):
    self.client.sendto(message.encode(), (host, port))
    data = self.client.recv(1024).decode()

    print(data)

  #helper function to login to a client account
  def login_client_account(self, message, host, port):

    #ensure that the server knows that it is the login function
    self.client.sendto(message.encode(), (host, port))

    print("login client account")
    message = input("""
    Please enter your username to log in: 
    """)
    #send over the username to the client
    self.client.sendto(message.encode(), (host, port))

    #will receive back confrmation that you logged in successfully
    data = self.client.recv(1024).decode()

    while data != 'Account has been identified. Thank you!':
      
      #allow them to exit

      #print("Unsuccessfully logged in")
      message = input("""We were unable to find an account associated with that username.
      Please type either 'create' to create a new account,
      'exit' to close the server connection, 
      or re-enter your username.
      """)
      #exit- close the connection
      if message.lower().strip() == 'exit':
        print(f'Connection closed.')
        self.client.close()
        break
      elif message.lower().strip() == 'create':
        self.create_client_username(message, host, port)
        break
      else: 
        #requery the client to see if this was a successful username
        #send over the username to the client
        self.client.sendto(message.encode(), (host, port))
        
        #will receive back confrmation that you logged in successfully
        data = self.client.recv(1024).decode()

        #print("Successfully logged in")
        #if data == 'Account has been identified. Thank you!':
        #  #successfully logged in
        #  print("Successfully logged in.")
      
        #else: #means there was an error
        #
        #  print("Unsuccessfully logged in")



  def delete_client_account(self, host, port):
    message = 'delete'
    self.client.sendto(message.encode(), (host, port))
    data = self.client.recv(1024).decode()

    if data == 'Account successfully deleted.':
      is_logged_in = False
      print("Successfully deleted account and logged out.")
    else:
      print("Unsuccessfully deleted account.")

  def client_program(self):
      # host = socket.
      host = 'dhcp-10-250-7-238.harvard.edu'
      port = 8884

      # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      # client.connect((host, port))
      self.client.connect((host, port))

      #handle initial information flow- either will login or create a new account
      
      #You need to either log in or create first
      have_logged_in = False
      while not have_logged_in:
        #handle initial information flow- either will login or create a new account
        message = input("""
        Welcome!
        Type 'login' to log into your account.
        Type 'create' to create a new account.
        Type 'exit' to disconnect from server.
        """)

        #login function
        if message.lower().strip() == 'login':
          self.login_client_account(message, host, port)
          have_logged_in = True

        #create function
        elif message.lower().strip() == 'create':
          print("create_client")
          self.create_client_username(message, host, port)
          have_logged_in = True
        
        #exit function- may want to exit early
        elif message.lower().strip() == 'exit':
          print(f'Connection closed.')
          self.client.close()
          break
        
        #if it is none of these key words, it will re query until you enter 'login' or 'create'

      #you can only access this loop if you have logged in- if you aren't logged in then you exited
      if have_logged_in:
        #now, allow the client + server to interact until it says to exit
        message = input('Reply to server: ')
        
        #continue 
        while message.strip() != 'exit':
          #delete account function
          if message.lower().strip() == 'delete my account':
            self.delete_client_account(host, port)

          self.client.sendto(message.encode(), (host, port))
          data = self.client.recv(1024).decode()

          print('Message from server: ' + data)
          message = input('Reply to server: ')

        print(f'Connection closed.')
        self.client.close()


if __name__ == '__main__':
  socket = ClientSocket()
  socket.client_program()