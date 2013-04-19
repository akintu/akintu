'''
Network communication class, using Twisted networking library
'''

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.error import ConnectionLost
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver

import socket
import Queue
import cPickle
import sys
from command import *
from const import *

class ServerData(LineReceiver):
    '''
    Server protocol that is instantiated by ServerDataFactory
    '''

    def connectionMade(self):
        self.port = self.transport.getPeer().port
        if self.port not in self.factory.clients:
            print("Connection made with client on port #" + str(self.port))
            self.factory.clients[self.port] = self
        self.factory.send(self.port, self.port)

    def connectionLost(self, reason):
        if reason.type is ConnectionLost:
            print('ServerData lost connection to client on ' + str(self.port) + '.')
        else:
            print('ServerData lost connection to client on ' + str(self.port) + '.  Reason: ' + reason.getErrorMessage())
        if self.port in self.factory.clients:
            del self.factory.clients[self.port]
            self.factory.queue.put((self.port, Command("PERSON", "REMOVE")))

    def lineReceived(self, data):
        '''
        This is where the incoming data is actually picked up
        '''
        data = cPickle.loads(data)
        if socket.gethostname() in ["Jzar", "Jgor"]: print("S " + str(self.port) + "> " + str(data))
        self.factory.queue.put((self.port, data))

class ServerDataFactory(Factory):
    '''
    Server factory
    '''
    protocol = ServerData

    def __init__(self):
        print("Listening for clients...")
        self.clients = {}
        self.queue = Queue.Queue()

    def send(self, port, data):
        '''
        Sends data to the client connected on the specified port
        '''
        data = cPickle.dumps(data)
        if port in self.clients:
            self.clients[port].sendLine(data)
        elif port == 0:
            for port, protocol in self.clients.iteritems():
                protocol.sendLine(data)

class ClientData(LineReceiver):
    '''
    Client protocol
    '''
    def connectionMade(self):
        self.factory.server = self
        print("Connected to server on " + str(self.transport.getPeer()))

    def connectionLost(self, reason):
        if reason.type is ConnectionLost:
            print('ClientData lost connection.')
        else:
            print('ClientData lost connection.  Reason: ' + reason.getErrorMessage())
            self.factory.queue.put(Command("CLIENT", "QUIT"))

    def lineReceived(self, data):
        '''
        Handles data received from the server
        '''
        data = cPickle.loads(data)
        if self.factory.port is None:
            self.factory.port = data
        else:
            if socket.gethostname() in ["Jzar", "Jgor"]: print("Client> " + str(data))
            self.factory.queue.put(data)

class ClientDataFactory(Factory):
    '''
    Client factory
    '''
    protocol = ClientData
    def __init__(self):
        self.queue = Queue.Queue()
        self.port = None

    def startedConnecting(self, connector):
        print('Connecting to server...')

    def send(self, data):
        '''
        Sends data to the server.  No port necessary since that was only necessary in instantiating
        the connection in the first place.
        '''
        data = cPickle.dumps(data)
        self.server.sendLine(data)

    def clientConnectionLost(self, connector, reason):
        if reason.type is ConnectionLost:
            print('ClientDataFactory lost connection.')
        else:
            print('ClientDataFactory lost connection.  Reason: ' + reason.getErrorMessage())

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed.  Reason: ' + reason.getErrorMessage())
