import os
import socket
import math
import time
import uuid
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint
# from https://krpc.github.io/krpc/communication-protocols/tcpip.html

set_port = 8888
set_host = ''
# set_host = 'dhcp-10-250-7-238.harvard.edu'
#[uuid: account info ]

def encode_varint(value):
  """ Encode an int as a protobuf varint """
  data = []
  _VarintEncoder()(data.append, value, False)
  return b''.join(data)


def decode_varint(data):
    """ Decode a protobuf varint to an int """
    return _DecodeVarint(data, 0)[0]


def send_message(conn, msg):
    """ Send a message, prefixed with its size, to a TPC/IP socket """
    data = msg.SerializeToString()
    size = encode_varint(len(data))
    conn.sendall(size + data)


def recv_message(conn, msg_type):
    """ Receive a message, prefixed with its size, from a TCP/IP socket """
    # Receive the size of the message data
    data = b''
    while True:
        try:
            data += conn.recv(1)
            size = decode_varint(data)
            break
        except IndexError:
            pass
    # Receive the message data
    data = conn.recv(size)
    # Decode the message
    msg = msg_type()
    msg.ParseFromString(data)
    return msg

class ClientSocket:

  def __init__(self, client=None):
    # We store if the client is currently logged in (to see if they have permission to
    # send/receive messages), their username, password, and 
    # queue of messages that they have received.

    # All of these objects are stored in a dictionary on the server of [username : ClientSocket object]

    self.logged_in = False
    self.username = ''
    self.password = ''
    self.messages = []

    if client is None:
      self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
      self.client = client

  # basic get/set functions to allow for the server to update these values

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
    self.client_buf.action = 'create'

    self.client.sendto(message.encode(), (host, port))
    data = self.client.recv(1024).decode()
    # update object attributes
    self.client_buf.username = data
    # self.username = data
    self.logged_in = True
    print('Your unique username is '  + data)

    # add a password input
    pwd_client = input('Enter password: ')

    # update the password in the client side
    self.client_buf.password = pwd_client
    # self.password = pwd_client

    self.client.sendto((pwd_client).encode(), (host, port))

    confirmation_from_server = self.client.recv(1024).decode()
    print(confirmation_from_server)

  
  # helper function to parse messages as everything is sent as strings
  def parse_live_message(self, message):
    # message format is senderUUID+message
    # UUID is 36 characters total (fixed length)
    # return is of the format (sender UUID, message)
    return (message[:36], message[36:])

  # function to print all available messages
  def deliver_available_msgs(self, available_msgs):
    # want to receive all undelivered messages
    for received_msg in available_msgs:
      # get Messages() has 
      sender_username, msg = self.parse_live_message(received_msg)
      print("Message from " + sender_username + ": " + msg)


  # Function to login to a client account
  def login_client_account(self, message, host, port):

    # ensure that the server knows that it is the login function
    # message says 'login'
    self.client.sendto(message.encode(), (host, port))

    # client will enter a username
    usrname_input = input("""
    Please enter your username to log in: 
    """)

    # send over the username to the server
    self.client.sendto(usrname_input.encode(), (host, port))

    # will receive back confirmation that username was sent successfully
    data = self.client.recv(1024).decode()

    # client will enter a password
    pwd_input = input("""
    Please enter your password to log in: 
    """)

    # in the loop, send the password to the server
    self.client.sendto(pwd_input.encode(), (host, port))

    # server will send back feedback on whether this was a valid login or not
    data = self.client.recv(1024).decode()

    # stay in for loop until you 
    while data[:30] != 'You have logged in. Thank you!':
      
      # allow them to create an account, exit, or try to log in again
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

      # create new account- reroute to that function
      elif message.lower().strip() == 'create':
        self.create_client_username(message, host, port)
        break


      else: 
        # requery the client to restart login process
        inform_status = 'login'
        self.client.sendto(inform_status.encode(), (host, port))

        usrname_input = input("""
        Please enter your username to log in: 
        """)
        # send over the username to the server
        self.client.sendto(usrname_input.encode(), (host, port))

        # will receive back confirmation that username was sent successfully
        data = self.client.recv(1024).decode()

        pwd_input = input("""
        Please enter your password to log in: 
        """)

        # in the loop, send the password to the server
        self.client.sendto(pwd_input.encode(), (host, port))

        # server will send back feedback on whether this was a valid login or not
        data = self.client.recv(1024).decode()
    
    # can exit while loop on success (logged in) or if the loop breaks (with create/exit)
    if data[:30] == 'You have logged in. Thank you!':
      # only if logged in, update the variables
      print("Successfully logged in.")
      self.logged_in = True
      self.username = usrname_input

      if data[30:] != 'No messages available':
          available_msgs = data[30:].split('we_love_cs262')[1:]
          self.deliver_available_msgs(available_msgs)

  # function to delete the client account
  def delete_client_account(self, message, host, port):

    # send a message that is 'delete' followed by the username to be parsed by the other side
    # we do not have a confirmation to delete as it takes effort to type 'delete' so it is difficult
    # to happen by accident

    message = "delete" + str(self.username)
    self.client.sendto(message.encode(), (host, port))
    
    # erver sends back status of whether account was successfully deleted
    data = self.client.recv(1024).decode()
    if data == 'Account successfully deleted.':
      self.logged_in = False
      print("Successfully deleted account.")
    else:
      print("Unsuccessfully deleted account.")


  # this is the main client program that we run- it calls on all subfunctions
  def client_program(self):
      host = set_host
      port = set_port

      self.client.connect((host, port))

      # handle initial information flow- either will login or create a new account
      # You need to either log in or create an account first

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
        
        # if it is none of these key words, it will re query until you enter 'login' or 'create' or 'exit'

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
            # check remaining msgs
            message = 'msgspls!'
            self.client.sendto(message.encode(), (host, port))
            data = self.client.recv(1024).decode()
            if data != 'No messages available':
              available_msgs = data.split('we_love_cs262')[1:]
              self.deliver_available_msgs(available_msgs)
            self.delete_client_account('delete', host, port)
            break

          # if they ask to create or delete given that you are currently logged in, throw an error
          elif message.lower().strip() == 'create':
            print("Error: you must log out before creating a new account. Type 'exit' to log out.")

          # if they ask to create or delete given that you are currently logged in, throw an error
          elif message.lower().strip() == 'login':
            print("Error: you are currently logged in to an account. Type 'exit' to log out and then log into another account.")

          # list all account usernames
          elif message.lower().strip() == 'listaccts':
            self.client.sendto(message.lower().strip().encode(), (host, port))
            data = self.client.recv(1024).decode()
            #feedback = self.client.recv(1024).decode()
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

              
            # print output of the server- either that it was successfully sent or that the user was not found.
            print('Message from server: ' + data)

          # get all messages that have been delivered to this client
          message = 'msgspls!'

          # inform server that you want to get new messages
          self.client.sendto(message.encode(), (host, port))

          # server will send back messages
          data = self.client.recv(1024).decode()
          if data != 'No messages available':
            # deliver available messages if there are any
            available_msgs = data.split('we_love_cs262')[1:]
            self.deliver_available_msgs(available_msgs)

          # re query for new client actions
          message = input("""
          To send a message, enter the recipient username, 
          'listaccts' to list all active usernames, 
          'exit' to leave program, or 
          'delete' to delete your account: 
          """)

        # will only exit while loops on 'exit' or 'delete'
        # read undelivered messages for exit
        if message.strip() == 'exit':
          # retrieve messages before exiting
          get_remaining_msgs = 'msgspls!'
          self.client.sendto(get_remaining_msgs.encode(), (host, port))
          data = self.client.recv(1024).decode()
          if data != 'No messages available':
            available_msgs = data.split('we_love_cs262')[1:]
            self.deliver_available_msgs(available_msgs)

        self.logged_in = False
        print(f'Connection closed.')
        self.client.close()

# program creates a ClientSocket object and runs client_program which
# handles input and directs it to the appropriate function
if __name__ == '__main__':
  socket = ClientSocket()
  socket.client_program()