from network import *

def printQ(GDF):
    if not GDF.queue.empty():
        print(GDF.queue.get())
    reactor.callInThread(printQ, GDF)

GDF = GameDataFactory()
reactor.callLater(5, GDF.send, 0, "Hi")
reactor.callInThread(printQ, GDF)
reactor.listenTCP(1337, GDF)
reactor.run()