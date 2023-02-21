import os
import socket
import math
import time
import uuid
import chat_pb2
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint

# encode, decode, send_message, recv_message from https://krpc.github.io/krpc/communication-protocols/tcpip.html

set_port = 8887
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
    # send/receive messages), their username, password, and queue of messages that they have received.

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
  def create_client_username(self, client_buf):
    client_buf.action = 'create'

    # inform the server of the client's action to create an account
    send_message(self.client, client_buf)

    # from the server, receive a protobuffer with the client's username
    data = recv_message(self.client, chat_pb2.Data)

    # update this ClientSocket's attributes
    self.username = data.client_username
    client_buf.client_username = data.client_username

    # now, the user is logged in and able to send & receive messages
    self.logged_in = True
    print('Your unique username is '  + data.client_username)

    # add a password input
    pwd_client = input('Enter password: ')

    # Ensures the users do not enter a password or one that is too long
    while len(pwd_client) < 1 or len(pwd_client) > 950:
      print("Error: password is required to be between 1 and 950 characters")
      pwd_client = input('Enter password: ')

    # update the password in the ClientSocket object 
    client_buf.client_password = pwd_client

    # set these attributes in the client_buf to be sent over
    self.password = pwd_client
    send_message(self.client, client_buf)

    confirmation_from_server = recv_message(self.client, chat_pb2.Data).message
    print(confirmation_from_server)

    return self.getUsername()

  
  # helper function to parse messages as everything is sent as strings
  # return is of the format (sender UUID, message)
  def parse_live_message(self, message):
    # message format is senderUUID+message
    # UUID is 36 characters total (fixed length)
    # return is of the format (sender UUID, message)
    return (message[:36], message[36:])

  # function to print all available messages
  # returns the # of messages delivered
  def deliver_available_msgs(self, available_msgs):
    # receive all undelivered messages
    for received_msg in available_msgs:
      # parse the messages to retrieve the sender username and the message
      # then print the message for the user to view
      sender_username, msg = self.parse_live_message(received_msg)
      print("Message from " + sender_username + ": " + msg)

    return len(available_msgs)

  # helper function to login to a client account
  # returns the username that you log into (either with create or login)
  # or False if you exit
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

    # receive back confirmation that username was sent successfully
    data = recv_message(self.client, chat_pb2.Data)

    pwd_input = input("""
    Please enter your password to log in: 
    """)
    client_buf.client_password = pwd_input

    # in the loop, send the password to the server
    send_message(self.client, client_buf)

    # will receive confirmation from the server whether you successfully logged in
    rec_buff = recv_message(self.client, chat_pb2.Data)
    data = rec_buff.message
    #data = recv_message(self.client, chat_pb2.Data).message

    # continue re-prompting until the user logs in, creates a new account, or exits
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
        return False
        
      # create an account- return the username created
      elif message.lower().strip() == 'create':
        return self.create_client_username(client_buf)

      else: 
        # requery the client to see if this was a successful username
        # send over the username to the client
        # prompt the server to look again for login
        # the user will send over their username so we want to prompt the server
        # to anticipate the login input folowed y 
        client_buf.action = 'login'
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

        rec_buff = recv_message(self.client, chat_pb2.Data)
        # data again will let you know if this was a successful log in
        #data = recv_message(self.client, chat_pb2.Data).message
        data = rec_buff.message
    
    # can exit while loop on success (logged in) or on a break 
    if data[:30] == 'You have logged in. Thank you!':
      
      print("Successfully logged in.")
      # update attributes in the ClientSocket object
      self.logged_in = True
      self.username = username_input

      # access available_messages in most recent client buffer sent over
      client_msgs = rec_buff.available_messages

      # if there are messages, deliver them
      if client_msgs != 'No messages available':
        available_msgs = client_msgs.split('we_love_cs262')[1:]
        self.deliver_available_msgs(available_msgs)
      
      # return the username of the account logged into
      return self.username
      



  # function to delete the client account
  # return True if it was successfully deleted, False otherwise
  def delete_client_account(self, client_buf):
    
    # populate the client buffer with the action delete and client username & send to Server
    client_buf.action = 'delete'
    client_buf.client_username = str(self.username)
    send_message(self.client, client_buf)
    
    # server sends back status of whether account was successfully deleted
    data = recv_message(self.client, chat_pb2.Data).message
    if data == 'Account successfully deleted.':
      self.logged_in = False
      print("Successfully deleted account.")
      return True
    else:
      print("Unsuccessfully deleted account.")
      return False


  # this is the main client program that we run- it calls on all subfunctions
  def client_program(self):
      host = set_host
      port = set_port

      # define a client_buf object to send messages
      client_buf = chat_pb2.Data()

      self.client.connect((host, port))

      # handle initial information flow- either will login or create a new account
      # You need to either log in or create an account first
      while not self.logged_in:
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
        
        # if it is none of these key words, it will re query until you enter 'login' or 'create' or 'exit'

      # can only enter loop if you are logged in- now can send/receive messages
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
            # First check if there are remaining msgs
            client_buf.action = 'msgspls!'
            client_buf.client_username = self.getUsername()
            send_message(self.client, client_buf)
            data = recv_message(self.client, chat_pb2.Data).available_messages

            # deliver messages if available
            if data != 'No messages available':
              available_msgs = data.split('we_love_cs262')[1:]
              self.deliver_available_msgs(available_msgs)

            # then delete the account * note that messages that were already sent
            # by a user that was deleted will STILL be delivered to indivdiuals.
            self.delete_client_account(client_buf)
            break

          # if they ask to create or delete given that you are currently logged in, throw an error
          elif message.lower().strip() == 'create':
            print("Error: you must log out before creating a new account. Type 'exit' to log out.")

          # if they ask to create or delete given that you are currently logged in, throw an error
          elif message.lower().strip() == 'login':
            print("Error: you are currently logged in to an account. Type 'exit' to log out and then log into another account.")

          # list all account usernames
          elif message.lower().strip() == 'listaccts':
            client_buf.action = 'listaccts'
            send_message(self.client, client_buf)    
            
            # note: unlike the non-GRPC protocol, we do not have to send
            # over the account_list size and then the account_list because
            # the receive message function accounts for messages of all lengths
            data = recv_message(self.client, chat_pb2.Data).list_accounts
            print('Usernames: ' + data)
            
          # send message if none of the inputs are key phrases
          else:
            # populate the client buffer object with necessary inputs
            client_buf.action = 'sendmsg'
            client_buf.client_username = self.getUsername()
            client_buf.recipient_username = message
            send_message(self.client, client_buf)

            # will receive information on whether the recipient username was found by server
            data = recv_message(self.client, chat_pb2.Data).message

            # if username is found, server will return 'User found. What is your message: '
            if data == "User found. Please enter your message: ":
              message = input(data)
              client_buf.message = message
              send_message(self.client, client_buf)
              # receive confirmation from the server that it was delivered
              data = recv_message(self.client, chat_pb2.Data).message

              
            # print output of the server- either that it was successfully sent or that the user was not found.
            print('Message from server: ' + data)

          # get all messages that have been delivered to this client
          client_buf.action = 'msgspls!'
          client_buf.client_username = self.getUsername()

          # inform server that you want to get new messages
          send_message(self.client, client_buf)

          # server will send back messages
          data = recv_message(self.client, chat_pb2.Data).available_messages
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
          client_buf.action = 'msgspls!'
          send_message(self.client, client_buf)
          data = recv_message(self.client, chat_pb2.Data).available_messages
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