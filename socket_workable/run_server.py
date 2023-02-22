import os
import socket
import math
import time
import uuid
from _thread import *
import threading
from run_client import ClientSocket

set_port = 8886
set_host = ''
# set_host = 'dhcp-10-250-7-238.harvard.edu'

class Server:
    curr_user = ''
    
    # Server object
    def __init__(self, sock=None):
        # Create a list of accounts for this server to keep track of clients
        # Format of account_list is [UUID: ClientObject]
        self.account_list = dict()
        # this commented line was to check that you are able to print account_list usernames
        # of different lengths
        # self.account_list['veryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrvvvvvvveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkrveryveryverylongwordgjralkdsfjnajfhgnlasdgnmlejahsgndmjighfjndkgshdnfkmeaijrdghfnkmesjdghnkmjgkmdsijgrndfkmdedsoijgdnkmijsgdnbckmdoseijdkoghjndksoeighufdkoseijfgnxdkoseijgncdkoseijrsgfkmdoewrijfgnckmxdoseijrgfnkdleoijrfgnckmdosfeijrdfkeirjhtungkmfidjenkmrtofgijdnzerawkmlortgifuhjndekwirghufjcnkmdseijrfgndkmseijrgfnckmdxosejirtfgknmdoewaijrtcfgkdxoewajirgfncaghfkdjnahfbdjnsmjfndmsjehrdksehbrsdkmjherbcmvkxdsjhebfcnvkxdioshuerjtkngfdhiuswjbeqnrkfglhdbsanwkeriofghubcjvnxkzsalijwehurbjcnvkxaisdhuwrgjdksaioehurwgdfjknsioehuwcjknvihuxdgsbejrnktfghiodabwjenkr'] = ClientSocket()
        # Mutex lock so only one thread can access account_list at a given time
        # Need this to be a Recursive mutex as some subfunctions call on lock on 
        # top of a locked function
        self.account_list_lock = threading.RLock()

        if sock is None:
            self.server = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server = sock

    # Returns true if the username exists in the account_list database,
    # false otherwise.
    def is_username_valid(self, recipient_username):
        # lock mutex as we access account_list
        self.account_list_lock.acquire()
        result =  recipient_username in self.account_list
        # unlock mutex
        self.account_list_lock.release()
        return result


    # Function to add the message to the recipient's queue
    def add_message_to_queue(self, sender_username, recipient_username, message):
        # queue format is strings of sender_username + "" + message
        message_string = sender_username + message
        # lock mutex
        self.account_list_lock.acquire()
        self.account_list.get(recipient_username).addMessage(message_string)
        # unlock mutex
        self.account_list_lock.release()


    # returns True upon successful message delivery. returns False if it fails.
    def deliver_message(self, sender_username, recipient_username, host, port, conn):
        # If username is invalid, throw error message
        if not self.is_username_valid(recipient_username): 
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
        confirmation_message_sent = "Delivered message '" + message[:50] + " ...' to " + recipient_username + " from " + sender_username
        print(confirmation_message_sent)
        conn.sendto(confirmation_message_sent.encode(), (host, port))
        return True


    # function to create an account/username for a new user
    def create_username(self, host, port, conn):

        # server will generate UUID, print UUID, send info to client
        # and then add account information to the dictionary
        username = str(uuid.uuid4())
        print("Unique username generated for client is "+ username + ".")
        conn.sendto(username.encode(), (host, port))

        # lock mutex
        self.account_list_lock.acquire()

        # add (username: clientSocket object where clientSocket includes log-in status,
        # username, password, and queue of undelivered messages
        self.account_list[username] = ClientSocket()

        # unlock mutex
        self.account_list_lock.release()

        # client will send back a password + send over confirmation
        data = conn.recv(1024).decode()

        # update the password in the object that is being stored in the dictionary
        # lock mutex
        self.account_list_lock.acquire()
        self.account_list.get(username.strip()).setPassword(data)
        # unlock mutex
        self.account_list_lock.release()
        
        # send client confirmation of the password 
        message = "Your password is confirmed to be " + data
        conn.sendto(message.encode(), (host, port))
        
        return username

    # send messages to the client that are in the client's message queue
    def send_client_messages(self, client_username, host, port, conn, prefix=''):
        # prefix is appended to the FRONT of messages to be delivered 
        # prefix is an optional argument as everything is sent as strings
        # prefix is ONLY used in the login function to send conffirmation

        final_msg = ""
        # note that we hold the mutex in this entire area- if we let go of mutex + reacquire to
        # empty messages we may obtain new messages in that time and then empty messages
        # that have not yet been read

        # lock mutex
        self.account_list_lock.acquire()
    
        # get available messages
        msgs = self.account_list.get(client_username).getMessages()

        # if there are messages, append them to the final messages
        if msgs:
            str_msgs = ''
            for message in msgs:
                str_msgs += 'we_love_cs262' + message
            final_msg += str_msgs

            # clear all delivered messages as soon as possible to address concurent access
            self.account_list.get(client_username).emptyMessages()
        else:
            final_msg += "No messages available" 
        # unlock mutex
        self.account_list_lock.release()
        

        # first send over the length of the message
        # SEND prefix + length of final msg- there is only a prefix for login 
        len_msg = prefix + str(len(final_msg))        
        conn.sendto(len_msg.encode(), (host, port))

        # receive back confirmation from the Client (this is to control info flow)
        confirmed = conn.recv(1024).decode()

        # then, send over the final message
        conn.sendto(final_msg.encode(), (host, port))


    # function to log in to an account
    def login_account(self, host, port, conn):

        # ask for login and password and then verify if it works

        # receive username from account
        username = conn.recv(1024).decode()

        # send confirmation that username was received
        confirm_received = "Confirming that the username has been received."
        conn.sendto(confirm_received.encode(), (host, port))

        password = conn.recv(1024).decode()

        # lock mutex
        self.account_list_lock.acquire()

        # see if username is valid
        if (username.strip() in self.account_list):
            # get the password corresponding to this
            if password == self.account_list.get(username.strip()).getPassword():
                # unlock mutex
                self.account_list_lock.release()

                confirmation = 'You have logged in. Thank you!'
                self.send_client_messages(username.strip(), host, port, conn, confirmation)
                return username.strip()
                
            else:
                # unlock mutex
                self.account_list_lock.release()
                print("Account not found.")
                message = 'Error'
                conn.sendto(message.encode(), (host, port))

        # see if username is valid- some cases it is concatenated with 'login' before
        elif (username.strip()[5:] in self.account_list):
            # get the password corresponding to this
            if password == self.account_list.get(username.strip()[5:]).getPassword():
                # unlock mutex
                self.account_list_lock.release()
                confirmation = 'You have logged in. Thank you!'
                self.send_client_messages(username.strip(), host, port, conn, confirmation)
                return username.strip()[5:]
            else:
                # unlock mutex
                self.account_list_lock.release()
                print("Account not found.")
                message = 'Error'
                conn.sendto(message.encode(), (host, port))

        else:
            # unlock mutex
            self.account_list_lock.release()
            # want to prompt the client to either try again or create account
            print("Account not found.")
            message = 'Error'
            conn.sendto(message.encode(), (host, port))


    # function to delete a client account 
    def delete_account(self, username, host, port, conn):
        # You can only delete your account once you are logged in 

        # check that the username is valid
        if username in self.account_list:
            # delete account and send confirmation
            del self.account_list[username]
            print("Successfully deleted client account, remaining accounts: ", self.account_list)
            message = 'Account successfully deleted.'
            conn.sendto(message.encode(), (host, port))
        else:
            # want to inform the client that it was unable to delete account
            message = 'Error deleting account'
            print(message)
            conn.sendto(message.encode(), (host, port))


    # function to list all active (non-deleted) accounts
    # add a return statement so it is easier to Unittest
    def list_accounts(self):

        # lock mutex 
        self.account_list_lock.acquire()       
        listed_accounts = str(list(self.account_list.keys()))
        # unlock mutex
        self.account_list_lock.release()
        
        # updated to return the length of the string version of this list
        # as it will be sent over the wire as a string
        return len(listed_accounts), listed_accounts

    # function that does the heavy lifting of server, client communication
    def server_to_client(self, host, conn, port):
        
        # keep track of the current client on this thread
        curr_user = ''
        
        # while statement only breaks when client deletes their account
        # or if client exits on their side (closes connection)
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

            # check if data equals 'create'
            elif data.lower().strip()[:6] == 'create':
                curr_user = self.create_username(host, port, conn)

            # check if data equals 'delete'- take substring as we send  delete + username to server
            elif data.lower().strip()[:6] == 'delete':
                # data parsing works correctly
                # print(data, data.lower().strip(), data.lower().strip()[6:])
                # client username, host, port, conn
                self.delete_account(data.lower()[6:], host, port, conn)
                return

            # check if client request to send a message
            elif data.lower().strip()[:7] == 'sendmsg':
                # data parsing works correctly
                # print(data, data.lower().strip()[7:43], data.lower()[44:])
                # client username, recipient username, host, port, conn
                self.deliver_message(data.lower().strip()[7:43], data.lower()[44:], host, port, conn)


            # check if client request is to list all accounts
            elif data.lower().strip()[:9] == 'listaccts':
                len_list, list_of_accounts = self.list_accounts()
                # send length of the list accounts function to be sent
                conn.sendto(str(len_list).encode(), (host, port))
                # receive confirmation from the Client it is ready for the 
                # list of accts
                recieved = conn.recv(1024).decode()
                # send the list of accounts
                conn.sendto(list_of_accounts.encode(), (host, port))

            # check if client request is to get available messages
            elif data[:8] == "msgspls!":
                self.send_client_messages(curr_user, host, port, conn)


    # this program sets up the server + creates new threads for clients      
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

# create a server object and run the server program!
if __name__ == '__main__':
    a = Server()
    a.server_program()