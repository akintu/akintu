'''
Network communication class
'''

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.error import ConnectionLost
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import Queue
import cPickle
import sys
from command import *

class ServerData(Protocol):
    '''
    Server protocol
    '''
    def connectionMade(self):
        self.port = self.transport.getPeer().port
        if not self.factory.clients.has_key(self.port):
            print("Connection made with client on port #" + str(self.port))
            self.factory.clients[self.port] = self
        self.factory.send(self.port, self.port)

    def connectionLost(self, reason):
        if reason.type is ConnectionLost:
            print('ServerData lost connection to client on ' + str(self.port) + '.')
        else:
            print('ServerData lost connection to client on ' + str(self.port) + '.  Reason: ' + reason.getErrorMessage())
        if self.factory.clients.has_key(self.port):
            del self.factory.clients[self.port]

    def dataReceived(self, data):
        data = cPickle.loads(data)
        print("Server recv from " + str(self.port) + "> " + str(data))
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
        data = cPickle.dumps(data)
        if self.clients.has_key(port):
            self.clients[port].transport.write(data)
        elif port == 0:
            for port, protocol in self.clients.iteritems():
                protocol.transport.write(data)

class ClientData(Protocol):
    '''
    Client protocol
    '''
    def connectionMade(self):
        self.factory.server = self
        print("Connected to server on " + str(self.transport.getPeer()))
        pass #Send avatar creation command

    def connectionLost(self, reason):
        if reason.type is ConnectionLost:
            print('ClientData lost connection.')
        else:
            print('ClientData lost connection.  Reason: ' + reason.getErrorMessage())
        if reactor.running:
            reactor.stop()

    def dataReceived(self, data):
        data = cPickle.loads(data)
        if self.factory.port is None:
            self.factory.port = data
        else:
            print("Client recv> " + str(data))
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
        data = cPickle.dumps(data)
        self.server.transport.write(data)

    def clientConnectionLost(self, connector, reason):
        if reason.type is ConnectionLost:
            print('ClientDataFactory lost connection.')
        else:
            print('ClientDataFactory lost connection.  Reason: ' + reason.getErrorMessage())

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed.  Reason: ' + reason.getErrorMessage())