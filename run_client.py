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

# class MySocket:
#     """demonstration class only
#       - coded for clarity, not efficiency
#     """

#     def __init__(self, sock=None):
#         if sock is None:
#             self.sock = socket.socket(
#                             socket.AF_INET, socket.SOCK_STREAM)
#         else:
#             self.sock = sock

#     def connect(self, host, port):
#         self.sock.connect((host, port))

#     def mysend(self, msg):
#         totalsent = 0
#         while totalsent < MSGLEN:
#             sent = self.sock.send(msg[totalsent:])
#             if sent == 0:
#                 raise RuntimeError("socket connection broken")
#             totalsent = totalsent + sent

#     def myreceive(self):
#         chunks = []
#         bytes_recd = 0
#         while bytes_recd < MSGLEN:
#             chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
#             if chunk == b'':
#                 raise RuntimeError("socket connection broken")
#             chunks.append(chunk)
#             bytes_recd = bytes_recd + len(chunk)
#         return b''.join(chunks)

# # create an INET, STREAMing socket
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # now connect to the web server on port 80 - the normal http port
# s.connect(("www.python.org", 80))

class ClientSocket:

  def __init__(self, client=None):
    if client is None:
      self.client = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
    else:
      self.client = client

  #helper function to create an account
  def create_client_username(self, message, host, port):
    self.client.sendto(message.encode(), (host, port))
    #self.client.sendto(message.encode(), (host, port))
    data = self.client.recv(1024).decode()

    print(data)

  #helper function to login to a client account
  def login_client_account(self, host, port):
    print("login client account")
    message = input("""
    Please enter your username to log in: 
    """)
    #send over the username to the client
    self.client.sendto(message.encode(), (host, port))

    #will receive back confrmation that you logged in successfully
    data = self.client.recv(1024).decode()
    if data:
      #successfully logged in
      print("Successfully logged in.")

    else:
      print("Unsuccessfully logged in")

    #FILL IN BLANK HERE


    #also will need to update the value of message so you do not end up
    #with issues



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
          self.login_client_account(host, port)
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
        message = input('Reply to server1: ')
        
        #continue 
        while message.strip() != 'exit':
          #somehow have a bug where it will do create twice
            self.client.sendto(message.encode(), (host, port))
            data = self.client.recv(1024).decode()

            print('Message from server: ' + data)
            message = input('Reply to server: ')

        print(f'Connection closed.')
        self.client.close()

    # while message.lower().strip() != 'bye':
    #     client.send(message.encode())  # send message
    #     data = client.recv(1024).decode()  # receive response

    #     print('Received from server: ' + data)  # show in terminal

    #     message = input(" -> ")  # again take input

    # client.close()  # close the connection

if __name__ == '__main__':
  socket = ClientSocket()
  socket.client_program()


# # create an INET, STREAMing socket
# serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # bind the socket to a public host, and a well-known port
# serversocket.bind(('10.250.0.0', 8888))
# # become a server socket
# serversocket.listen(5)


# while True:
#     # accept connections from outside
#     (clientsocket, address) = serversocket.accept()
#     # now do something with the clientsocket
#     # in this case, we'll pretend this is a threaded server
#     ct = client_thread(clientsocket)
#     ct.run()


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
