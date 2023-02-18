import os
import socket
import math
import time
import uuid
import unittest
from run_server import Server

# https://docs.python.org/2/library/unittest.html from section 25.3.1 
# Adapted from section 25.3.4

class SimpleServerTestCase(unittest.TestCase):
    #create only one instance to avoid multiple instantiations
    def setUp(self):
        self.server_instance = Server()

        #set up host, port, create connection
        host = ''
        port = 8888
        self.server_instance.server.bind((host, port))

        # accept incoming connections
        # self.server_instance.server.listen()
        # conn, addr = self.server_instance.server.accept()

    def shutDown(self):
        #conn.close()
        print('shut downwnn')

class InitServerCreateAccountListCase(SimpleServerTestCase):
    def runTest(self):
        self.assertEqual(self.server_instance.account_list, dict(),
                         'incorrect default size')

class ListAccountTestCase(SimpleServerTestCase):
    def runTest(self):
        #make the test where you can see that the length 
        #once you let users choose their username, this will be easier to test
        # TODO- update once we have username input
        self.assertEqual([''], self.server_instance.list_accounts(),
                         'incorrect accounts available')

"""class WidgetResizeTestCase(SimpleServerTestCase):
    def runTest(self):
        self.widget.resize(100,150)
        self.assertEqual(self.widget.size(), (100,150),
                         'wrong size after resize')
"""
if __name__ == '__main__':
    unittest.main()
