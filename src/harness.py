from network import *
import threading
import sys
import time

def printQ(SDF):
    if not SDF.queue.empty():
        print("Getting queue item...")
        print(SDF.queue.get())
        print("Got queue item!")
    if reactor.running:
        print("Initiating thread call...")
        reactor.callInThread(printQ, SDF)

def readKey(CDF):
    data = raw_input()
    CDF.send(data)
    if data == 'q':
        CDF.shutdown()
    else:
        CDF.send(data)
        reactor.callInThread(readKey, CDF)

if sys.argv[1].lower() == "host":
    SDF = ServerDataFactory()
    #reactor.callLater(5, SDF.send, 0, "Hi @ " + str(time.time()))
    #reactor.callInThread(printQ, SDF)
    t1 = threading.Thread(target=start_server, args=(SDF, 1337))
    t1.start()
    print("Reactor stopped")
elif sys.argv[1].lower() == "client":
    CDF = ClientDataFactory()
    ic = reactor.connectTCP(sys.argv[2], 1337, CDF)
    reactor.callInThread(readKey, CDF)
    reactor.run()
    print("Reactor stopped")