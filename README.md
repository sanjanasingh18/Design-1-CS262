# Design-1-CS262

How to set up the Chat System (1 server, mutliple clients):

Setting up the non-GRPC server-client chat application:

* Versions + Packages necessary - We use Python 3.7+, the socket, time, uuid, 
_thread, and threading packages.


To have multiple clients ALL on the same computer as the server, set your host as follows:

Line 8 on run_client.py:
    set_host = ''

Line 11 on run_server.py:
    set_host = ''
    

To have clients on different computers as the server, carry out the following steps:

Run the following code:

import socket
print(socket.gethostname())
hostName = socket.gethostname()

This will give you the host name to connect between computers. Ensure that computers are connected
to the same WiFi network.

Line 8 on run_client.py:
    set_host = hostName

Line 11 on run_server.py:
    set_host = hostName


Setting up the GRPC server-client chat application:

* Versions + Packages necessary - We use Python 3.7+, the socket, time, uuid, 
_thread, threading, google.protobuf.internal.encoder and google.protobuf.internal.decoder
 packages.


To have multiple clients ALL on the same computer as the server, set your host as follows:

Line 13 on grpc_client.py:
    set_host = ''

Line 13 on grpc_server.py:
    set_host = ''
    

To have clients on different computers as the server, carry out the following steps:

Run the following code:

import socket
print(socket.gethostname())
hostName = socket.gethostname()

This will give you the host name to connect between computers. Ensure that computers are connected
to the same WiFi network.

Line 13 on grpc_client.py:
    set_host = hostName

Line 13 on grpc_server.py:
    set_host = hostName


Common issues:
- 'Address already in use' issue when you run the files run_server.py or grpc_server.py. Change the set_port variable (line 10, run_server.py OR line 12, grpc_server.py) to be a different value (e.g. 8888) . Then, update the set_port variable ( OR line 12, grpc_client.py) to be that SAME value (e.g. also 8888).

