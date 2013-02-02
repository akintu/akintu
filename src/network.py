'''
Network communication class
'''

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

import Queue
import cPickle
from pprint import pprint

class ServerData(Protocol):
    '''
    Server protocol
    '''
    def connectionMade(self):
        self.port = self.transport.getPeer().port
        if not self.factory.clients.has_key(self.port):
            print("Connection made with client on port #" + str(self.port))
            self.factory.clients[self.port] = self

    def connectionLost(self, reason):
        print('Lost connection.  Reason:' + str(reason))
        if self.factory.clients.has_key(self.port):
            del self.factory.clients[self.port]
        self.factory.shutdown()

    def dataReceived(self, data):
        data = cPickle.loads(data)
        pprint(data)
        self.factory.queue.put((self.port, data))
        if data == 'q': #Find some other abort mechanism
            self.factory.shutdown()

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

    def shutdown(self):
        for port, protocol in self.clients.iteritems():
            protocol.transport.loseConnection()
        if reactor.running:
            reactor.stop()
        print("Server shutdown")


class ClientData(Protocol):
    '''
    Client protocol
    '''
    def connectionMade(self):
        self.factory.server = self
        print("Connected to server on " + str(self.transport.getPeer()))
        pass #Send avatar creation command

    def connectionLost(self, reason):
        print('Lost connection.  Reason:' + str(reason))

    def dataReceived(self, data):
        data = cPickle.loads(data)
        pprint(data)
        self.factory.queue.put(data)
        if data == 'q': #Find some other abort mechanism
            self.factory.shutdown()

class ClientDataFactory(Factory):
    '''
    Client factory
    '''
    protocol = ClientData
    def __init__(self):
        self.queue = Queue.Queue()

    def startedConnecting(self, connector):
        print('Connecting to server...')

    def send(self, data):
        data = cPickle.dumps(data)
        self.server.transport.write(data)

    def shutdown(self):
        self.server.transport.loseConnection()
        if reactor.running:
            reactor.stop()
        print("Connection to server closed.")

    def clientConnectionLost(self, connector, reason):
        pprint(reason)
        print('Lost connection.  Reason:' + str(reason))

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed.  Reason:' + str(reason))