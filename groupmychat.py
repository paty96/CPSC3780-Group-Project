# Program: groupmychat.py (python 2)
# Program By: Lucas Jakober, Yash Patel
# Description: Program runs as specifications by Robert
#              To launch the program enter a command as such: python groupmychat.py 55000 User_name
#              The program will then send a "HELLO" User_name to all the define Ip addresses and Ports
#	           The program will continue to send "HELLO" User_name every 5 seconds
#			   When a "HELLO" User_name is recieved from a new IP address, it add the IP and User_name to the Peer List
#			   The timer for each peer in the peer list is updated every time we get a "HELLO" User_name from our Peers
#              To send a Message: s "MESSAGE HERE"
#              To print recieved messages: p
#			   To show your peer list: l
#              To quit: q (It will also output remaining messages that you have not looked at)
#              

from Queue import Queue,Empty
from threading import Thread
from threading import Timer
from time import sleep
import socket,sys,errno
import sys,socket

def isValidName(username):
	if not (any(x.isupper() for x in username) and any(x.islower() for x in username)):
		return False
	if "-" not in username and "." not in username and "_" not in username :
		return False
	return True

# Checks to see if the input has enough arguments Provided 
if len(sys.argv) != 3:
	print("Please Enter: {} Source_Port User_Name".format(sys.argv[0])) 
	sys.exit(1)

if (isValidName(sys.argv[2]) == False):
	print("Username must have an uppercase letter, lowercase letter, and one of - or _ or .") 
	sys.exit(1)

try:
	s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except:
	print("Cannot Open Socket")
	sys.exit(1)

# Defining Global Variable Lab IP addresses
labip = ["142.66.140.21", "142.66.140.22", "142.66.140.23", "142.66.140.24", "142.66.140.25", "142.66.140.26",
		 "142.66.140.27", "142.66.140.28", "142.66.140.29", "142.66.140.30", "142.66.140.31", "142.66.140.32",
		 "142.66.140.33", "142.66.140.34", "142.66.140.35", "142.66.140.36", "142.66.140.37", "142.66.140.38",
		 "142.66.140.39", "142.66.140.40", "142.66.140.41", "142.66.140.42", "142.66.140.43", "142.66.140.44",
		 "142.66.140.45", "142.66.140.46", "142.66.140.47", "142.66.140.48", "142.66.140.49", "142.66.140.50",
		 "142.66.140.51", "142.66.140.52", "142.66.140.53", "142.66.140.54", "142.66.140.55", "142.66.140.56",
		 "142.66.140.57", "142.66.140.58", "142.66.140.59", "142.66.140.60", "142.66.140.61", "142.66.140.62",
		 "142.66.140.63", "142.66.140.64", "142.66.140.65", "142.66.140.66", "142.66.140.67", "142.66.140.68",
		 "142.66.140.69", "142.66.140.186", "142.66.140.172"]
# Defining Global Variables for Ports ranging from 55000-55008
ports = [55000,55001,55002,55003,55004,55005,55006,55007,55008]
# Defining a Global Variable for PeerList
peerlist = []
# Buffer Length
BUFLEN = 1000
# Defining a queue
queue = Queue()
 # Source Port as Entered by the user
sourcePort = int(sys.argv[1])
userName = sys.argv[2]




# Function that kills the timer for a peer in the peer list every 5 seconds
def kill(username):
	for p in peerlist:
		if p.username == username:
			p.active = False

# User class for Peers
class User:
	def __init__(self, username, ip, port, active, timer=None):
		self.username = username
		self.ip = ip
		self.port = port
		self.active = True
		self.timer = timer

# Removes a user from the peer list
def removeUser(username):
	global peerlist
	userToDelete = None
	for p in peerlist:
		if p.username == username:
			userToDelete = p
	peerlist.remove(userToDelete)

# Reciever Thread that checks to see if we got any messages seperately from the main function
class Receiver(Thread):
	def __init__(self, queue):
		Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			try:
 				s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			except:
				print("Cannot open socket")
				sys.exit(1)
			try:
				s.bind(('',sourcePort))
			except:
				print("Cannot bind socket to port")
				sys.exit(1)
			try:
				for p in peerlist:
					p.username, " ", p.active
				data,addr = s.recvfrom(BUFLEN)
				if data[:5] == "HELLO" :
					name = data[5:]
					if (isValidName(name) == True):
							usernames = []
							for p in peerlist:
								usernames.append(p.username)
							if data[6:] in usernames:
								if (p.username == data[6:]) and (p.ip == addr[0]) and (p.port == addr[1]):
										p.timer.cancel()
										p.timer = Timer(15,kill,[p.username])
										p.timer.start()
										p.active = True
							else:
								newuser = User(username=data[6:], ip=addr[0],port=addr[1], active=True, timer=Timer(15,kill,[data[6:]]))
								peerlist.append(newuser)
								newuser.timer.start()
				elif data[:4] == "CHAT":
					self.queue.put(data[4:])
				else:
					self.queue.put(data)
			except OSError as err:
				print("Cannot receive from socket: {}".format(err.strerror))
				sys.exit(1)

# Another Thread that sends a "HELLO" + User_Name every 5 seconds
# to update others that we are still active
class autoSend(Thread):
	def __init__(self, interval=1):
		Thread.__init__(self)
		self.interval = interval                               

	def run(self):
		i=0
		while True:
			for p in peerlist:
				if(p.active == False):
					removeUser(p.username)				
			SendAutoHello()
			i=(i+1)%100
			sleep(5)


# Main Function that checks the inputs from the user
def main():
	init()
	startReciever()
	print 'Your Username is: ', userName, '\n'
	print('p - Prints Received Messages\ns <msg> - Send Message\nl - Outputs a List Of Your Peers That Are Currently Active\nq - Quits\n')
	cmd = raw_input('& ')
	t = 0
	while (cmd[0] != 'q'):
		if (cmd[0] == 'p'):
			RecieveMessages()
		if (cmd[0] == 's'):
			if(SendMessages("CHAT" + cmd[1:]) == False):
				print("Message Could Not Be Sent, NO ONE ACTIVE CURRENTLY")
		if (cmd[:4] == "CHAT"):
			if(SendMessages(cmd) == False):
				print("Message Could Not Be Sent, NO ONE ACTIVE CURRENTLY")
		elif (cmd[0] == 'l'):
			for user in peerlist:
				print(user.username+" "+user.ip)
		cmd = raw_input('& ')
	quitChat()
   
# Function that Starts the Reciever Thread and the autoSend Thread
def startReciever():
	receiver = Receiver(queue)
	receiver.daemon = True
	receiver.start()
	threading = autoSend(1)
	threading.daemon = True
	threading.start()
	return True

# Recieves Messages and Prints them to the screen
def RecieveMessages():
	if (queue.empty() == True):
		print ("No New Messages")
	else:
		print('Recieved Messages: \n')
		while (queue.empty() == False):
			msg = queue.get(False,None)
			print(msg)
	return True

# Sends Messages to the Destination IP at the Destination Port
def SendMessages(cmd):
	try:
		if not peerlist:
			return False
		for p in peerlist:
			for j in range(0,len(ports)):
				if(ports[j]!= sourcePort):
					s.sendto(cmd, (p.ip, ports[j]))
		return True
	except:
		return False

def SendAutoHello():
	try:
		for i in range(0,len(labip)):
			for j in range(0,len(ports)):
				if(ports[j]!= sourcePort):
					s.sendto("HELLO" + " " + userName, (labip[i], ports[j]))
		return True

	except:
		return False

def init():
	try:
		for i in range(0,len(labip)):
			for j in range(0,len(ports)):
				if(ports[j]!= sourcePort):
					s.sendto("HELLO" + " " + userName, (labip[i], ports[j]))
		return True
	except:
		return False

# Quits the Chat and outputs the remaining recieved messages
def quitChat():
	if (queue.empty() == True):
		print ("No New Messages")
	else:
		print('Recieved Messages: \n')
		while (queue.empty() == False):
			msg = queue.get(False,None)
			print(msg)
			print ("----")
			print('Good Bye...')
	return True

main()
