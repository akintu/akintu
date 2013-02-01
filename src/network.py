'''
Network communication class
'''

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

import Queue

class GameData(Protocol):
    def __init__(self, port):
        self.port = port

    def connectionMade(self):
        if not self.factory.clients.has_key(self.port):
            print("Connection made with client on port #" + str(self.port))
            self.factory.clients[self.port] = self

    def connectionLost(self, reason):
        print("Stopping...")
        reactor.stop()
        if self.factory.clients.has_key(self.port):
            del self.factory.clients[self.port]
        print("Stopped")

    def dataReceived(self, data):
        self.factory.queue.put((self.port, data))

class GameDataFactory(Factory):
    def __init__(self):
        print("Listening for clients...")
        self.clients = {}
        self.queue = Queue.Queue()

    def buildProtocol(self, addr):
        p = GameData(addr.port)
        p.factory = self
        return p

    def send(self, port, data):
        if self.clients.has_key(port):
            self.clients[port].transport.write(data)
