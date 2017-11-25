# Program: mychat.py (python 2)
# Author: Yash Patel
# Description: Program runs as specifications by Robert
#              To launch the program enter a command as such from linux0: python mychat.py 55000 linux2.cs.uleth.ca 55000
#              To launch on linux 2: python mychat.py 55000 linux0.cs.uleth.ca 55000
#              They will connect and you can send messages from one terminal to the other
#              To send a Message: s "MESSAGE HERE"
#              To print recieved messages: p
#              To quit: q (It will also output remaining messages that you have not looked at)
#              

from Queue import Queue,Empty
from threading import Thread
from time import sleep
import socket,sys,errno
import sys,socket

labip = ["142.66.140.14","142.66.140.172","142.66.140.226","142.66.140.227","142.66.140.228","142.66.140.229","142.66.140.230",
        "142.66.140.231","142.66.140.232","142.66.140.233","142.66.140.234","142.66.140.235",
        "142.66.140.236","142.66.140.237","142.66.140.238","142.66.140.239","142.66.140.240",
        "142.66.140.241","142.66.140.242","142.66.140.243","142.66.140.244","142.66.140.245",
        "142.66.140.246","142.66.140.247","142.66.140.248","142.66.140.249","142.66.140.250",
        "142.66.140.70","142.66.140.71","142.66.140.72","142.66.140.73","142.66.140.74","142.66.140.75",
        "142.66.140.76","142.66.140.77","142.66.140.78","142.66.140.79","142.66.140.80","142.66.140.81",
        "142.66.140.82","142.66.140.83","142.66.140.84","142.66.140.85","142.66.140.86","142.66.140.87",
        "142.66.140.88","142.66.140.89","142.66.140.90","142.66.140.91","142.66.140.92","142.66.140.93",
        "142.66.140.94","142.66.140.95","142.66.140.96","142.66.140.97","142.66.140.98"]
ports = [55000,55001,55002,55003,55004,55005,55006,55007,55008]
peerlist = []

# Checks to see if the input has enough 
if len(sys.argv) != 3:
	print("Please Enter: {} Source_Port".format(sys.argv[0])) 
	sys.exit(1)
if not (any(x.isupper() for x in sys.argv[2]) and any(x.islower() for x in sys.argv[2])):
	print("Username must have an uppercase letter, lowercase letter, and one of - or _ or .") 
	sys.exit(1)
if "-" not in sys.argv[2] and "." not in sys.argv[2] and "_" not in sys.argv[2] :
	print("Username must have an uppercase letter, lowercase letter, and one of - or _ or .") 
	sys.exit(1)

try:
	s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except:
	print("Cannot Open Socket")
	sys.exit(1)


# GLOBAL VARIABLES
BUFLEN = 1000 # Buffer Length
queue = Queue() # Defining a queue
sourcePort = int(sys.argv[1]) # Source Port as Entered by the user
userName = sys.argv[2]
# Class Provided by Robert - slightly modified
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
				data,addr = s.recvfrom(BUFLEN)
				if data[:5] == "HELLO" :
					name = data[5:]
					if (any(x.isupper() for x in name) and any(x.islower() for x in name)):
						if "-" in name or "." in name or "_" in name :
							if ([data[6:],addr[0],addr[1]]) not in peerlist:
								peerlist.append([data[6:],addr[0],addr[1]])
				else:
					self.queue.put(data)
			except OSError as err:
				print("Cannot receive from socket: {}".format(err.strerror))
				sys.exit(1)

class autoSend(Thread):
	def __init__(self, interval=1):
		Thread.__init__(self)
		self.interval = interval                               

	def run(self):
		i=0
		while True:
			SendAutoHello()
			i=(i+1)%100
			sleep(15)



# Main Function
def main():
	startReciever()
	threading = autoSend(1)
	threading.daemon = True
	threading.start()
	print 'Your Username is: ', userName, '\n'
	print('p - Prints Received Messages\ns <msg> - Send Message\nq - Quits\n')
	init()
	cmd = raw_input('& ')
	t = 0
	while (cmd[0] != 'q'):
		if (cmd[0] == 'p'):
			RecieveMessages()
		if (cmd[0] == 's'):
			if(SendMessages(cmd) == False):
				print("Message Could Not Be Sent, NO ONE ACTIVE CURRENTLY")
		if (cmd[0] == 'l'):
			print "PEER LIST: ", peerlist
		cmd = raw_input('& ')
	quitChat()
   
# Function that Starts the Reciever
def startReciever():
	receiver = Receiver(queue)
	receiver.daemon = True
	receiver.start()
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

		for i in range(0,len(peerlist)):
			for j in range(0,len(ports)):
				if(ports[j]!= sourcePort):
					s.sendto(cmd[2:], (peerlist[i].__getitem__(1), ports[j]))
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
