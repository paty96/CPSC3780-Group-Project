from Queue import Queue,Empty
from threading import Thread
from threading import Timer
from time import sleep
import Message
import chat_settings
import socket,sys,errno,datetime

class GroupChat:
	# User class for Peers
	class User:
		def __init__(self, chat, username, ip, port, active, timer=None):
			self.chat = chat
			self.username = username
			self.ip = ip
			self.port = port
			self.active = True
			self.timer = timer

	# Reciever Thread that checks to see if we got any messages seperately from the main function
	class Receiver(Thread):
		def __init__(self, chat):
			Thread.__init__(self)
			self.chat = chat
			try:
 				self.s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			except:
				print("Cannot open socket")
				sys.exit(1)
			try:
				# print self.chat.sourcePort
				# print socket.gethostbyname(socket.gethostname())
				self.s.bind(('',int(self.chat.sourcePort)))
			except socket.error, msg:
				sys.stderr.write("error: %s"%msg)
				print("Cannot bind socket to port")
				sys.exit(1)

		def run(self):
			while True:
				try:
					data,addr = self.s.recvfrom(self.chat.buffer_length)
					if data[:5] == "HELLO" :
						name = data[5:]
						if (self.chat.isValidUsername(name) == True):
								usernames = []
								for p in self.chat.peerlist:
									usernames.append(p.username)
								if data[6:] in usernames:
									if (p.username == data[6:]) and (p.ip == addr[0]) and (p.port == addr[1]):
											p.timer.cancel()
											p.timer = Timer(15,self.chat.kill,[p.username])
											p.timer.start()
											p.active = True
								else:
									newuser = GroupChat.User(self.chat, username=data[6:], ip=addr[0],port=addr[1], active=True, timer=Timer(15,self.chat.kill,[data[6:]]))
									self.chat.peerlist.append(newuser)
									newuser.timer.start()
									print newuser.username + " joined!\n"
					elif data[:4] == "CHAT":
						sender_name=''
						for p in self.chat.peerlist:
							if (p.ip,p.port) == addr:
								sender_name = p.username
						msg = Message.Message(time=str(datetime.datetime.now())[:-7],sender=sender_name,text=data[4:])
						self.chat.msg_queue.put(msg)
						if self.chat.msg_queue.qsize() == 1:
							print "%d new message"%self.chat.msg_queue.qsize()
						elif self.chat.msg_queue.qsize() > 1:
							print "%d new messages"%self.chat.msg_queue.qsize()
					else:
						sender_name=''
						for p in self.chat.peerlist:
							if (p.ip,p.port) == addr:
								sender_name = p.username
						msg = Message.Message(time=str(datetime.datetime.now())[:-7],sender=sender_name,text=data[4:])
						self.chat.msg_queue.put(msg)
						if self.chat.msq_queue.qsize() == 1:
							print "%d new message"%self.chat.msg_queue.qsize()
						elif self.chat.msq_queue.qsize() > 1:
							print "%d new messages"%self.chat.msg_queue.qsize()
				except OSError as err:
					print("Cannot receive from socket: {}".format(err.strerror))
					sys.exit(1)

	# Another Thread that sends a "HELLO" + User_Name every 5 seconds
	# to update others that we are still active
	class AutoSend(Thread):
		def __init__(self, chat):
			Thread.__init__(self)
			self.chat = chat
			self.interval = 1                               

		def run(self):
			i=0
			while True:
				for p in self.chat.peerlist:
					if(p.active == False):
						self.chat.removeUser(p.username)				
				self.chat.sendAutoHello()
				i=(i+1)%100
				sleep(5)
	
	def __init__(self, source_port, my_username):
		self.sourcePort = source_port
		self.username = my_username
		self.labip = chat_settings.LAB_IP_ADDRESSES 
		self.ports = chat_settings.PORTS
		self.buffer_length = chat_settings.BUFLEN
		self.username_err = chat_settings.USERNAME_ERROR_MSG
		self.menu = chat_settings.MENU
		self.peerlist = []
		self.msg_queue = Queue()
		self.receiver = self.createReceiver()
		self.auto_sender = self.createAutoSend()
		try:
			self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except:
			print("Cannot Open Socket")
			sys.exit(1)
		self.receiver.daemon = True
		self.receiver.start()
		self.auto_sender.daemon = True
		self.auto_sender.start()
		self.sendAutoHello()
		self.cmd = 'h'

	def createReceiver(self):
		return GroupChat.Receiver(self)

	def createAutoSend(self):
		return GroupChat.AutoSend(self)

	# Function that kills the timer for a peer in the peer list every 5 seconds
	def kill(self, username):
		for p in self.peerlist:
			if p.username == username:
				p.active = False

	# Removes a user from the peer list
	def removeUser(self, username):
		userToDelete = None
		for p in self.peerlist:
			if p.username == username:
				userToDelete = p
		self.peerlist.remove(userToDelete)


	def changeUserName(self):
		print chat.username_err
		new_username = raw_input('New username: ')
		if new_username == 'q' and chat.isValidUsername(chat.username):
			return
		while not chat.isValidUsername(new_username):
			print chat.username_err
			new_username = raw_input('New username: ')
			if new_username == 'q'and chat.isValidUsername(chat.username):
				break
		if new_username != 'q':
			chat.username = new_username

	def printMessageQueue(self):
		print "You had %d unread messages."%self.msg_queue.qsize()
		while not self.msg_queue.empty():
			msg = self.msg_queue.get(False, None)
			if msg.message_text[:4]=='CHAT':
				msg.message_text = msg.message_text[4:]
			print "msg: "+msg.message_text

	def printDetailedMessageQueue(self):
		print "You had %d unread messages."%self.msg_queue.qsize()
		while not self.msg_queue.empty():
			msg = self.msg_queue.get(False, None)
			if msg.message_text[:4]=='CHAT':
				msg.message_text = msg.message_text[4:]
			print "----------------------------------------------"
			print "msg: "+msg.message_text+"\n"
			print "{0: <20s} {1: >5s}".format('From: ',msg.message_from)
			print "{0: <20s} {1: >5s}".format('Received:',msg.message_time)
			print "----------------------------------------------\n"

	# Main Function that checks the inputs from the user
	def runChat(self):
		print 'Your Username is: ', self.username, '\n'
		if not chat.isValidUsername(self.username):
			self.changeUserName()
		t = 0
		while True:
			if self.cmd == 'p':
				self.printMessageQueue()
				# self.printMessages()
			elif self.cmd == 'p+':
				self.printDetailedMessageQueue()
			elif self.cmd == 'l':
				if not self.peerlist:
					print "No one currently online."
				for user in self.peerlist:
					print user.username+" @"+user.ip
			elif self.cmd == 'h':
				print self.menu
			elif self.cmd == 'c':
				self.changeUserName()
			elif self.cmd == 'q':
				break
			else:
				self.sendMessage('CHAT'+self.cmd)
			self.cmd = raw_input('')
		self.quitChat()

	# Recieves Messages and Prints them to the screen
	def printMessages(self):
		if (self.msg_queue.empty() == True):
			print ("---")
		else:
			print('Recieved Messages: \n')
			while (self.msg_queue.empty() == False):
				msg = self.msg_queue.get(False,None)
				if msg[:4]=='CHAT':
					msg = msg[4:]
				print(msg)

	# Sends message to the destination IP at the destination port
	def sendMessage(self,cmd):
		if not self.peerlist:
			print "No one currently online."
			return
		for p in self.peerlist:
			for port in self.ports:
				self.sock.sendto(cmd, (p.ip,port))

	def sendAutoHello(self):
		try:
			for ip in self.labip:
				if ip == socket.gethostbyname(socket.gethostname()):
					continue
				for port in self.ports:
					if int(port) == int(self.sourcePort):
						continue
					self.sock.sendto("HELLO "+self.username,(ip,port))
		except socket.error, msg:
			"No other users currently online."

	# Quits the Chat and outputs the remaining recieved messages
	def quitChat(self):
		# self.printMessages()
		self.printMessageQueue()
		print ("Good Bye")

	def isValidUsername(self, username):
		if not (any(x.isupper() for x in username) and any(x.islower() for x in username)):
			return False
		if "-" not in username and "." not in username and "_" not in username :
			return False
		return True

# Checks to see if the input has enough arguments Provided 
if len(sys.argv) != 3:
	print("Please Enter: {} Source_Port User_Name".format(sys.argv[0])) 
	sys.exit(1)

chat = GroupChat(sys.argv[1], sys.argv[2])
chat.runChat()