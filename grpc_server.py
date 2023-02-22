import socket
import uuid
import time
from _thread import *
import threading
from run_client import ClientSocket
import chat_pb2
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint

# encode, decode, send_message, recv_message from https://krpc.github.io/krpc/communication-protocols/tcpip.html

set_port = 8888
set_host = ''
# set_host = 'dhcp-10-250-7-238.harvard.edu'

# reference source code from https://docs.python.org/3/howto/sockets.html


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

    # function to see whether the username is in the accoutn list
    def is_username_valid(self, recipient_username):
        # lock mutex while you access the account_list
        self.account_list_lock.acquire()
        result =  recipient_username in self.account_list
        # unlock mutex
        self.account_list_lock.release()
        return result


    # if the recipient isn't logged in, add the message to the queue
    def add_message_to_queue(self, sender_username, recipient_username, message):
        # queue format is strings of <sender_username + "" + message>
        message_string = sender_username + message
        # lock mutex
        self.account_list_lock.acquire()
        # add message to queue
        # TODO- send error message if this doesn't work. Soph can you 
        # do this, I built out the rest of the functionality for this
        self.account_list.get(recipient_username).addMessage(message_string)
        # unlock mutex
        self.account_list_lock.release()
        return True

    # returns True upon successful delivery. returns False if it fails.
    def deliver_message(self, sender_username, recipient_username, client_buf, conn):
        # If username is invalid, print error message + send to Client
        if not self.is_username_valid(recipient_username): 
            recipient_not_found = "User not found."
            print(recipient_not_found)
            client_buf.message = recipient_not_found
            send_message(conn, client_buf)
            return False

        # Send a message to the client to enter a message
        confirmed_found_recipient = "User found. Please enter your message: "
        print("User found.")
        client_buf.message = confirmed_found_recipient
        send_message(conn, client_buf)

        # server will receive what the message the client wants to send is 
        message = recv_message(conn, chat_pb2.Data).message

        # regardless of client status (logged in or not), add the message to the recipient queue
        if self.add_message_to_queue(sender_username, recipient_username, message): 

            # print + deliver confirmation- show abridged version of message in the console
            confirmation_message_sent = "Delivered message '" + message[:50] + " ...' to " + recipient_username + " from " + sender_username
            print(confirmation_message_sent)
            client_buf.message = confirmation_message_sent
            send_message(conn, client_buf)
            return True
        
        # if the message did not deliver, deliver an error message
        else:
            message_did_not_work = "Message could not be delivered. Please try again."
            print(message_did_not_work)
            client_buf.message = message_did_not_work
            send_message(conn, client_buf)
            return False

    # function we use to create an account/username for a new user
    def create_username(self, client_buf, conn):

        # server will generate UUID, print UUID, send info to client, and then add it to the dict
        username = str(uuid.uuid4())
        print("Unique username generated for client is "+ username + ".")
        client_buf.client_username = username

        send_message(conn, client_buf)

        # add (username: clientSocket object where clientSocket includes log-in status,
        # username, password, and queue of undelivered messages

        # lock mutex
        self.account_list_lock.acquire()
        self.account_list[username] = ClientSocket()
        # unlock mutex
        self.account_list_lock.release()

        # client will send back a password + send over confirmation
        pwd = recv_message(conn, chat_pb2.Data).client_password

        # update the password in the object that is being stored in the dictionary
        # lock mutex
        self.account_list_lock.acquire()
        self.account_list.get(username.strip()).setPassword(pwd)
        # unlock mutex
        self.account_list_lock.release()
        
        # send confirmation that the password was processed by server
        message = "Your password is confirmed to be " + pwd
        client_buf.message = message
        send_message(conn, client_buf)
        
        return username

    # send messages to the client that are in the queue to be delivered for that client
    # returns what messages are sent over
    def send_client_messages(self, client_username, client_buf, conn, prefix=''):
        # want to receive all undelivered messages
        final_msg = prefix

        # note that we hold the mutex in this entire area- if we let go of mutex + reacquire to
        # empty messages we may obtain new messages in that time and then empty messages
        # that have not yet been read

        # lock mutex & get messages
        self.account_list_lock.acquire()
        msgs = self.account_list.get(client_username).getMessages()

        # if there are available messages, concatenate them to the final list
        if msgs:
            str_msgs = ''
            for message in msgs:
                str_msgs += 'we_love_cs262' + message
            final_msg += str_msgs

            # clear all delivered messages as soon as possible to address concurent access
            # clearing so you do not double deliver messages
            self.account_list.get(client_username).emptyMessages()
        else:
            final_msg += "No messages available"
        # unlock mutex
        self.account_list_lock.release()
        
        # note that client_buf.message will have a confirmation that you have logged in as well
        # if you are running this function within 'login'
        # send the formatted messages to the client
        client_buf.available_messages = final_msg
        send_message(conn, client_buf)

        return final_msg


    # function to log in to an account
    # Returns the username if the account is logged into, or False otherwise
    def login_account(self, client_buf, conn):
        # ask for login and password and then verify if it works
        time.sleep(1)

        data = recv_message(conn, chat_pb2.Data)
        username = data.client_username
        password = data.client_password
        # lock mutex
        self.account_list_lock.acquire()
        # check if username, password pair is valid
        if (username.strip() in self.account_list):
            # get the password corresponding to this
            if password == self.account_list.get(username.strip()).getPassword():
                # unlock mutex
                self.account_list_lock.release()
                
                # send confirmation that you have logged in successfully
                confirmation = 'You have logged in. Thank you!'
                client_buf.message = confirmation
                self.send_client_messages(username.strip(), client_buf, conn)
                return username.strip()
                
            else:
                # send message that you have not logged in
                # unlock mutex
                self.account_list_lock.release()
                print("Account not found.")
                message = 'Error'
                client_buf.message = message
                send_message(conn, client_buf)
                return False

        elif (username.strip()[5:] in self.account_list):
            # get the password corresponding to this
            if password == self.account_list.get(username.strip()[5:]).getPassword():
                # unlock mutex
                self.account_list_lock.release()

                # send confirmation that you have logged in successfully
                confirmation = 'You have logged in. Thank you!'
                client_buf.message = confirmation
                self.send_client_messages(username.strip(), client_buf, conn)
                return username.strip()[5:]
            else:
                # send message that you have not logged in
                # unlock mutex
                self.account_list_lock.release()
                print("Account not found.")
                message = 'Error'
                client_buf.message = message
                send_message(conn, client_buf)
                return False

        else:
            # unlock mutex
            self.account_list_lock.release()
            # want to prompt the client to either try again or create account
            print("Account not found.")
            message = 'Error'
            client_buf.message = message
            send_message(conn, client_buf)
            return False

    # function to delete a client account 
    # return True if it was successfully deleted, False otherwise
    def delete_account(self, username, client_buf, conn):
        # You can only delete your account once you are logged in so this handles
        # undelivered messages
        if username in self.account_list:
            # delete the account + send a confirmation
            del self.account_list[username]
            print("Successfully deleted client account, remaining accounts: ", self.account_list)
            message = 'Account successfully deleted.'
            client_buf.message = message
            send_message(conn, client_buf)
            return True
        else:
            # want to prompt the client to either try again or create account
            message = 'Error deleting account'
            print(message)
            client_buf.message = message
            send_message(conn, client_buf)
            return False


    # function to return all active (non-deleted) accounts
    # returns the list of accounts
    def list_accounts(self):
        # lock mutex 
        self.account_list_lock.acquire()       
        listed_accounts = str(list(self.account_list.keys()))
        # unlock mutex
        self.account_list_lock.release()

        return listed_accounts

    
    def server_to_client(self, host, conn, port):
        curr_user = ''

        client_buf = chat_pb2.Data()

        while True:
            # receive from client
            data = recv_message(conn, chat_pb2.Data)
            
            # check if connection closed- if so, close thread
            if not data:
                # close thread
                return

            print('Message from client: ' + data.action)

            # check if data equals 'login'
            if data.action == 'login':
                curr_user = self.login_account(client_buf, conn)

            # check if data equals 'create'
            elif data.action == 'create':
                curr_user = self.create_username(client_buf, conn)

            # check if data equals 'delete'
            elif data.action == 'delete':
                self.delete_account(data.client_username, client_buf, conn)
                return

            # check if client request to send a message
            elif data.action == 'sendmsg':
                self.deliver_message(data.client_username, data.recipient_username, client_buf, conn)

            # check if client request is to list all accounts
            elif data.action == 'listaccts':
                client_buf.list_accounts = self.list_accounts()
                send_message(conn, client_buf)

            elif data.action == "msgspls!":
                self.send_client_messages(data.client_username, client_buf, conn)
                    
    def server_program(self):
        host = set_host
        port = set_port
        self.server.bind((host, port))
        self.server.listen()
        print('Server is active')

        # Accept new connections and create new threads 
        while True:
            conn, addr = self.server.accept()

            print(f'{addr} connected to server.')

            # Start a new thread with each client
            curr_thread = threading.Thread(target=self.server_to_client, args=(host, conn, port,))
            curr_thread.start()

if __name__ == '__main__':
    a = Server()
    a.server_program()
