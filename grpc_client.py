import os
import socket
import math
import time
import uuid
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint
# from https://krpc.github.io/krpc/communication-protocols/tcpip.html
import chat_pb2

set_port = 8888
set_host = ''
# host = 'dhcp-10-250-7-238.harvard.edu'
#[uuid: account info ]

#account info is an object
#recipients: queue of undelivered messages, logged in or not 
#login TODO- if you login and you have undelivered messages, want to send those

#this source code from https://docs.python.org/3/howto/sockets.html


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
    # we store if the client is currently logged in, their username, password, and 
    # queue of messages that they want to receive
    # all of these objects are stored in sa dictionary on the server of username : ClientSocket object

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
  def create_client_username(self, client_buf):
    client_buf.action = 'create'
    print('client_buf', client_buf)

    send_message(self.client, client_buf)
    #self.client.sendto(message.encode(), (host, port))

    data = recv_message(self.client, chat_pb2.Data)
    #data = self.client.recv(1024).decode()
    # update object attributes
    self.username = data.client_username
    client_buf.client_username = data.client_username
    # self.username = data
    self.logged_in = True
    print('Your unique username is '  + data.client_username)

    # add a password input
    pwd_client = input('Enter password: ')

    # update the password in the client side
    client_buf.client_password = pwd_client
    self.password = pwd_client

    send_message(self.client, client_buf)
    #self.client.sendto((pwd_client).encode(), (host, port))

    confirmation_from_server = recv_message(self.client, chat_pb2.Data).message
    #confirmation_from_server = self.client.recv(1024).decode()
    print(confirmation_from_server)


  def parse_live_message(self, message):
    # message format is senderUUID_message
    # UUID is 36 characters total
    # you are not allowed to encode tuples; thus, use string format
    # return is of the format (sender UUID, message)
    return (message[:36], message[36:])

      
  def deliver_available_msgs(self, available_msgs):
    # want to receive all undelivered messages
    for received_msg in available_msgs:
      # get Messages() has 
      sender_username, msg = self.parse_live_message(received_msg)
      print("Message from " + sender_username + ": " + msg)


  # helper function to login to a client account
  def login_client_account(self, client_buf):

    client_buf.action = 'login'

    # ensure that the server knows that it is the login function
    send_message(self.client, client_buf)

    username_input = input("""
    Please enter your username to log in: 
    """)
    client_buf.client_username = username_input
    # send over the username to the server
    send_message(self.client, client_buf)

    # will receive back confirmation that username was sent successfully
    data = recv_message(self.client, chat_pb2.Data)

    pwd_input = input("""
    Please enter your password to log in: 
    """)
    client_buf.client_password = pwd_input

    # in the loop, send the password to the server
    send_message(self.client, client_buf)

    data = recv_message(self.client, chat_pb2.Data)

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
        self.create_client_username(client_buf)
        break

      else: 
        # requery the client to see if this was a successful username
        # send over the username to the client
        # prompt the server to look again for login
        # the user will send over their username so we want to prompt the server
        # to anticipate the login input folowed y 
        client_buf.action = 'login'
        send_message(self.client, client_buf)

        # this was prior.
        # will receive back confrmation that you logged in successfully
        # data = self.client.recv(1024).decode()
        username_input = input("""
        Please enter your username to log in: 
        """)

        client_buf.client_username = username_input

        # send over the username to the server
        send_message(self.client, client_buf)

        # will receive back confirmation that username was sent successfully
        data = recv_message(self.client, chat_pb2.Data)

        pwd_input = input("""
        Please enter your password to log in: 
        """)
        
        client_buf.client_password = pwd_input

        # in the loop, send the password to the server
        send_message(self.client, client_buf)

        data = recv_message(self.client, chat_pb2.Data)
    
    # can exit while loop on success (logged in) or on a break 
    if data[:30] == 'You have logged in. Thank you!':
      print("Successfully logged in.")
      self.logged_in = True
      # self.username = username_input
      client_buf.client_username = username_input

      client_msgs = client_buf.available_messages[30:]

      if client_msgs != 'No messages available':
          available_msgs = client_msgs.split('we_love_cs262')[1:]
          self.deliver_available_msgs(available_msgs)

      # if data[30:] != 'No messages available':
      #     available_msgs = data[30:].split('we_love_cs262')[1:]
      #     self.deliver_available_msgs(available_msgs)


  def delete_client_account(self, message, host, port):

    # send a message that is 'delete' followed by the username to be parsed by the other side
    # we do not have a confirmation to delete as it takes effort to type 'delete' so it is difficult
    # to happen by accident

    client_buf.action = 'delete'
    client_buf.client_username = str(self.username)

    # message = "delete" + str(self.username)
    self.client.sendto(message.encode(), (host, port))
    
    #server sends back status of whether it worked
    data = self.client.recv(1024).decode()
    if data == 'Account successfully deleted.':
      self.logged_in = False
      print("Successfully deleted account.")
    else:
      print("Unsuccessfully deleted account.")


  def client_program(self):
      host = set_host
      port = set_port

      self.client.connect((host, port))

      # define a client_buf object to send messages

      client_buf = chat_pb2.Data()

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
          self.login_client_account(client_buf)
          break

        # create function
        elif message.lower().strip() == 'create':
          self.create_client_username(client_buf)
      
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
            # check remaining msgs
            # TODO: update to use protocol buffer 
            message = 'msgspls!'
            self.client.sendto(message.encode(), (host, port))
            data = self.client.recv(1024).decode()

            client_msgs = client_buf.available_messages

            if client_msgs != 'No messages available':
                available_msgs = client_msgs.split('we_love_cs262')[1:]
                self.deliver_available_msgs(available_msgs)

            # if data != 'No messages available':
            #   available_msgs = data.split('we_love_cs262')[1:]
            #   self.deliver_available_msgs(available_msgs)

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

              
            # COMMENT: message from server was there because before it was client- server interaction
            # now, we do not need to get the server to reprompt the client with something
            # will we ever need 
            print('Message from server: ' + data)

          # TODO: update to use buffers
          message = 'msgspls!'
          self.client.sendto(message.encode(), (host, port))
          data = self.client.recv(1024).decode()

          client_msgs = client_buf.available_messages

          if client_msgs != 'No messages available':
              available_msgs = client_msgs.split('we_love_cs262')[1:]
              self.deliver_available_msgs(available_msgs)
          # if data != 'No messages available':
          #   available_msgs = data.split('we_love_cs262')[1:]
          #   self.deliver_available_msgs(available_msgs)

          message = input("""
          To send a message, enter the recipient username, 
          'listaccts' to list all active usernames, 
          'exit' to leave program, or 
          'delete' to delete your account: 
          """)

        # will only exit while loops on 'exit' or 'delete'
        # read undelivered messages for exit
        if message.strip() == 'exit':
          # TODO: update to use buffers
          get_remaining_msgs = 'msgspls!'
          self.client.sendto(get_remaining_msgs.encode(), (host, port))
          data = self.client.recv(1024).decode()

          client_msgs = self.client_buf.available_messages

          if client_msgs != 'No messages available':
              available_msgs = client_msgs.split('we_love_cs262')[1:]
              self.deliver_available_msgs(available_msgs)

          # if data != 'No messages available':
          #   available_msgs = data.split('we_love_cs262')[1:]
          #   self.deliver_available_msgs(available_msgs)

        self.logged_in = False
        print(f'Connection closed.')
        self.client.close()


if __name__ == '__main__':
  socket = ClientSocket()
  socket.client_program()