'''
Network communication engine
'''

import sys, threading, pickle, Queue, socket
from command import *

class Client:
	"""Creates a client connection to an Akintu server process"""
	
	def __init__(self, host="127.0.0.1", port="999"):
		self._host = host
		self._port = int(port)
		self._sendBuffer = Queue.Queue()
		self._recvBuffer = Queue.Queue()
		self._stop = False
		
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.connect((self._host, self._port))
		
		self._s = threading.Thread(target=self.start_send)
		self._s.start()
		self._r = threading.Thread(target=self.start_receive)
		self._r.start()
		
	def __del__(self):
		self.close()
		
	def close(self):
		self._stop = True
		self._sendBuffer.join()
		self._socket.close()
		self._recvBuffer.join()
		
	def send(self, data):
		self._sendBuffer.put(data)
		
	def recv(self):
		data = self._recvBuffer.get()
		self._recvBuffer.task_done()
		return data

	def start_send(self):
		try:
			while not self._stop:
				command = self._sendBuffer.get()
				self._socket.send(pickle.dumps(command))
				self._sendBuffer.task_done()
				if command.lower() in ["exit", "quit"]:
					self.close()
		except:
			raise
			
	def start_receive(self):
		try:
			while not self._stop:
				command = pickle.loads(self._socket.recv(1024))
				self._recvBuffer.put(command)
				print("Server says: ", command)
		except EOFError:
			pass
		except ConnectionAbortedError:
			pass

class Server:
	def __init__(self, host="127.0.0.1", port="999"):
		self._host = host
		self._port = int(port)
		self._recvBuffer = Queue.Queue()
		self._sendBuffer = {}
		self._conn = {}
		self._stop = False
		#self._clients = {}
		
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self._i = threading.Thread(target=self.initiate_connections)
		self._i.start()
		
	def __del__(self):
		self.close()

	def initiate_connections(self):
		'''		class ClientConnection:
					def __init__(self, conn, s, r, buffer):
						self.conn = conn
						self.s = s
						self.r = r
						self.buffer = buffer
		'''
		
		self._socket.bind((self._host, self._port))
		self._socket.listen(1)
		while not self._stop:
			print('The server is ready to recieve')
			connectionSocket, addr = self._socket.accept()
			print('Connection received on', addr)
			port = int(addr[1])
			
			self._sendBuffer[port] = Queue.Queue()
			self._conn[port] = connectionSocket
			
			s = threading.Thread(target=self.start_send, args=(connectionSocket, self._sendBuffer[port]))
			s.start()
			r = threading.Thread(target=self.start_receive, args=(connectionSocket, self._recvBuffer))
			r.start()
			
#			self._clients[port] = ClientConnection(connectionSocket, s, r, buffer)
		
	def close(self):
		self._stop = True
		for buffer in self._sendBuffer:
			buffer.join()		
		for conn in self._conn:
			conn.close()
		self._recvBuffer.join()
		
	def send(self, port, data):
		self._sendBuffer[port].put(data)
		
	def recv(self):
		data = self._recvBuffer.get()
		self._recvBuffer.task_done()
		return data

	def start_send(self, conn, buffer):
		print("Host: ", self._host)
		try:
			while not self._stop:
				command = buffer.get()
				conn.send(pickle.dumps(command))
				buffer.task_done()
				if command.lower() in ["exit", "quit"]:
					self.close()
		except:
			raise
			
	def start_receive(self, conn, buffer):
		try:
			while not self._stop:
				command = pickle.loads(conn.recv(1024))
				buffer.put(command)
				print("Server says: ", command)
		except EOFError:
			pass
		except ConnectionAbortedError:
			pass
			
if __name__ == "__main__":
	if sys.argv[1].lower() == "host":
		server = Server("", 999)
	
	if sys.argv[1].lower() == "client":
		if len(sys.argv) > 3:
			client = Client(sys.argv[2], sys.argv[3])
		else:
			client = Client()
		
		def debuff(client):
			while True:
				command = client.recv()
				print(command)
				if command.lower() in ["exit", "quit"]:
					break
		t = threading.Thread(target=debuff, args=(client,))		
					
		while True:
			command = input('Enter command: ')
			client.send(command)
			if command.lower() in ["exit", "quit"]:
				break