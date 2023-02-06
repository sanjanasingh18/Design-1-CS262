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
"""
class MySocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)
"""
# # create an INET, STREAMing socket
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # now connect to the web server on port 80 - the normal http port
# s.connect(("www.python.org", 80))

class Server:
    def __init__(self, sock=None):
        #want to set up a server socket as we did with the sample code
        #want to create a list of accounts for this server and unsent messages

        #format of account_list is [UUID: queue of messages not yet sent]
        account_list = dict()
        
        if sock is None:
            self.server = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.server = sock

    
    def server_program(self):
        #changed to the 
        #server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #used socket.gethostname() to get the host name to connect between
        #computers
        host = 'dhcp-10-250-7-238.harvard.edu'
        print(host)
        port = 8888
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
                message = 'Please enter your username (UUID)'
                conn.sendto(message.encode(), (host, port))
            elif data.lower().strip() == 'create':
                # generate UUID and add to dictionary 
                username = uuid.uuid4()
                message = 'Your unique username is ' + str(username)
                conn.sendto(message.encode(), (host, port))
                #todo- add it to dictionary

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

"""

# create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serversocket.bind(('10.250.0.0', 8888))
# become a server socket
serversocket.listen(5)



while True:
    # accept connections from outside
    (clientsocket, address) = serversocket.accept()
    # now do something with the clientsocket
    # in this case, we'll pretend this is a threaded server
    ct = client_thread(clientsocket)
    ct.run()"""


#copied this main from other code I have
"""
if __name__ == '__main__':

    arguments = docopt(__doc__)        
    ###Grab image directory
    image_dir = arguments['<image_dir>']
    
    ###Load imaging model
    mdl_path = arguments['<model_path>']

    ###set model architecture
    m = arguments['--modelarch'].lower()
    
    ###Read tabular data
    output_df = pd.read_csv(arguments['<data_frame>'])
    
    #Read target variable
    col = arguments['--target']
        
    # Split dataset
    if(arguments["--split"]!="False"):
        output_df = output_df.loc[output_df.Dataset=="Te",]
    
    # Create imagelist
    imgs = (ImageList.from_df(df=output_df,path=image_dir)
                                .split_none()
                                .label_from_df(cols=col)
                                .transform(tfms_test,size=224)
                                .databunch(num_workers = num_workers,bs=bs).normalize(imagenet_stats))
"""
