from socket import *
import sys
import argparse 
import ipaddress
import time

parser = argparse.ArgumentParser(description="positional arguments", epilog="end of help")

parser.add_argument('-s', '--server', help='Activates the server side', action='store_true')
parser.add_argument('-c', '--client', help='Activates the client side',action='store_true')
parser.add_argument('-i', '--serverip', type=str, default='127.0.0.1')
parser.add_argument('-p', '--port', type=int, default=8088)

parser.add_argument('-r', '--reliable', type=str)
parser.add_argument('-t', '--testcase', type=str)
parser.add_argument('-f', '--filetransfer', type=str)


args = parser.parse_args()

'''
    #Utility functions: 1) to create a packet of 1472 bytes with header (12 bytes) (sequence number, acknowledgement number,
    #flags and receiver window) and applicaton data (1460 bytes), and 2) to parse
    # the extracted header from the application data. 
'''

from struct import *


# I integer (unsigned long) = 4bytes and H (unsigned short integer 2 bytes)
# see the struct official page for more info

header_format = '!IIHH'


def create_packet(seq, ack, flags, win, data):
    #creates a packet with header information and application data
    #the input arguments are sequence number, acknowledgment number
    #flags (we only use 4 bits),  receiver window and application data 
    #struct.pack returns a bytes object containing the header values
    #packed according to the header_format !IIHH
    header = pack (header_format, seq, ack, flags, win)

    #once we create a header, we add the application data to create a packet
    #of 1472 bytes
    packet = header + data

    return packet


def parse_header(header):
    #taks a header of 12 bytes as an argument,
    #unpacks the value based on the specified header_format
    #and return a tuple with the values
    header_from_msg = unpack(header_format, header)
    #parse_flags(flags)
    return header_from_msg
    

def parse_flags(flags):
    #we only parse the first 3 fields because we're not 
    #using rst in our implementation
    syn = flags & (1 << 3)
    ack = flags & (1 << 2)
    fin = flags & (1 << 1)
    return syn, ack, fin


 # Description: 
 # this is the reciever side of the stop and wait which does this: it recieves a packet from the stop_and_wait_sender 
 # and if it is delivered to the reciever then an ACK messae is sent back to the client.
 # when all the packets is sent, the image is done copying and a finish packet is sent, if an acknowledge is not sent then the client will send the packet again.  
 # it recives the packet from the client side and splits it into the header (12 bytes) and message(1460 bytes)
 # when everything is recived a fin packet is sent back to the client
 # for every packet 
 #
 #Arguments: 
 # ip: holds the ip address of the server
 # port: port number of the server
 # 
 # Returns: .... and why?
 #

def stop_and_wait_reciever(connectionserver, teller):

	while True:

		message, clientaddress = connectionserver.recvfrom(1472)

		h = message[:12] # we extract the header information of the packet
		seq, ack, flags, win = parse_header (h) # gets the info for the header 
		message = message[12:]
		syn1, ack1, fin1 = parse_flags(flags)

		if fin1 > 0:
			finAck_packet = create_packet(0, 0, 6, 1, b'')
			connectionserver.sendto(finAck_packet, clientaddress)
			break

		print(f'seq={seq}, ack={ack}, flags={flags}, recevier-window={win}') # prints out the packet
		ackPacket = create_packet(0, seq, 4, 5, b'') # creates an acknowledgement packet to be sent back to the client
		
		#if(teller == 3):
			#print("Skips")
		#else:
		if message != "":
			connectionserver.sendto(ackPacket, clientaddress)

		return message
		

def stop_and_wait_sender(connection):

		connection.settimeout(0.5)
		
		seq, ack, flags, win = 1,0,0,0
		throughput = 0
		message = args.filetransfer
		f = open(message, "rb")

		while True:

			msg = f.read(1460)

			throughput += len(msg)

			start = time.time()

			if msg == b'':
				fin_packet = create_packet(0, 0, 2, 1, b'')
				connection.send(fin_packet)
				break

			packet = create_packet(seq, ack, flags, win, msg)

			##### test case 3 (Skip seq) #####

			if(seq == 1):
				print("skip")
			else:
				connection.send(packet)
				seq += 1
			acknowledgment = b''

			while True:
				try:
					acknowledgment, serveraddress = connection.recvfrom(1460)
					break
				except:
					print("No ACK recived, resending packet")
					connection.send(packet)

			h = acknowledgment[:12]	
			acknowledgment = acknowledgment[12:]
			seq2, ack2, flags2, win2 = parse_header (h)
			print("ACK:", ack2) # prints out the amount of ack
			
			if seq == ack2:
				ack = ack2
				seq += 1
			
		finish, serveraddress = connection.recvfrom(1460)
		h = finish[:12]	
		seq2, ack2, flags2, win2 = parse_header (h)
		syn, ack, fin = parse_flags(flags2)

		if fin > 0 and ack > 0:
			print("The process is finished") 
		end = time.time()

		throughput = 8*throughput/(end-start)
		throughput = throughput/1_000_000

		print("throughput", throughput, "mbps")




def GBN_recviver(serverconnection, teller, sjekk):
		
	slidewindowData = []
	slidewindowSeq = []


	message, clientaddress = serverconnection.recvfrom(1472)

	h = message[:12]

	seq, ack, flags, win = parse_header (h)
	
	slidewindowData.append(message)
	slidewindowSeq.append(seq)

	if len(slidewindowSeq) == win:

		for i in range(win-1):
			
			if(slidewindowSeq[i]+1 == slidewindowSeq[i+1]):
				print("")
			else:
				slidewindowSeq = []
				slidewindowData = []

		if (len(slidewindowSeq) == win):
			print(slidewindowSeq)
			slidewindowSeq.pop(0)
			slidewindowData.pop(0)
	
	###### test case 2 (skip ack) #######

	if(teller == 3):
		print("Skips")
	else:
		ackPacket = create_packet(0, seq, 4, 5, b'')
		serverconnection.sendto(ackPacket, clientaddress)

	if message == b'fin':
		serverconnection.sendto("finACK".encode(), clientaddress)
	
	print(f'seq={seq}, ack={ack}, flags={flags}, recevier-window={win}')
	
	
	return slidewindowData[0]
	


def GBN_sender(connection, feil):

	seq, ack, flags, win = 1,0,0,5

	message = args.filetransfer
	f = open(message, "rb")

	slidewindowData = []
	slidewindowSeq = []
	i = 0

	throughput = 0
	start = time.time()
	test = True

	while i != win: 

			msg = f.read(1460)
			if msg == b'':
				connection.send("fin".encode())
				break
			packet = create_packet(seq, ack, flags, win, msg)
			slidewindowData.append(packet)
			slidewindowSeq.append(seq)
			connection.send(slidewindowData[i])	
			i += 1
			seq += 1
		
	while True:

		print(slidewindowSeq)
		

		acknowledgment, serveraddress = connection.recvfrom(1460)
		h = acknowledgment[:12]
		acknowledgment = acknowledgment[12:]
		seq2, ack2, flags2, win2 = parse_header (h)


		if (feil == win-1):
			feil = 0
		
		if (feil > 0):
			feil += 1
			continue

		elif slidewindowSeq[0] == ack2:
			slidewindowSeq.pop(0)
			slidewindowData.pop(0)
			ack = ack2

			msg = f.read(1460)
			throughput += len(msg)
			if msg == b'':
				connection.send("fin".encode())
				break

			packet = create_packet(seq, ack, flags, win, msg)
			
			slidewindowData.append(packet)
			slidewindowSeq.append(seq)


			##### test case 3 (skip seq)######
			#if (seq == 8 and test):
				#test = False
				#print("skip")
			#else:
			connection.send(packet)
			seq += 1

		else:
			feil += 1
			print("det skjedde en feil")
			connection.settimeout(0.5)
			print(acknowledgment)
			for i in range(len(slidewindowData)):
				connection.send(slidewindowData[i])

		if acknowledgment == b"finACK":
			break	

	end = time.time()
	throughput = 8*throughput/(end-start)
	throughput = throughput/1_000_000

	print("throughput", throughput, "mbps")

	
		
def SR_Recviever(serverconnection, teller, sjekk):

	slidewindowData = []
	slidewindowSeq = []


	message, clientaddress = serverconnection.recvfrom(1472)

	h = message[:12]



	seq, ack, flags, win = parse_header (h)
	
	slidewindowData.append(message)
	slidewindowSeq.append(seq)

	if len(slidewindowSeq) == win:

		for i in range(win-1):
			
			if(slidewindowSeq[i]+1 == slidewindowSeq[i+1]):
				print("")
			else:
				slidewindowSeq = []
				slidewindowData = []

		if (len(slidewindowSeq) == win):
			print(slidewindowSeq)
			slidewindowSeq.pop(0)
			slidewindowData.pop(0)
	
	
	if(teller == 3):
		print("Skips")

	else:
		ackPacket = create_packet(0, seq, 4, 5, b'')
		serverconnection.sendto(ackPacket, clientaddress)

	if message == b'fin':
		serverconnection.sendto("finACK".encode(), clientaddress)
	
	print(f'seq={seq}, ack={ack}, flags={flags}, recevier-window={win}')
	
	
	return slidewindowData[0]


def SR_Sender(connection, feil):

	seq, ack, flags, win = 1,0,0,5

	message = args.filetransfer
	f = open(message, "rb")

	slidewindowData = []
	slidewindowSeq = []
	i = 0

	while i != win: 

			msg = f.read(1460)
			if msg == b'':
				connection.send("fin".encode())
				break
			packet = create_packet(seq, ack, flags, win, msg)
			slidewindowData.append(packet)
			slidewindowSeq.append(seq)
			connection.send(slidewindowData[i])	
			i += 1
			seq += 1
		
	while True:

		print(slidewindowSeq)

		acknowledgment, serveraddress = connection.recvfrom(1460)
		h = acknowledgment[:12]
		acknowledgment = acknowledgment[12:]
		seq2, ack2, flags2, win2 = parse_header (h)
		

		if slidewindowSeq[0] == ack2:
			slidewindowSeq.pop(0)
			slidewindowData.pop(0)
			ack = ack2

			msg = f.read(1460)
			if msg == b'':
				connection.send("fin".encode())
				break

			packet = create_packet(seq, ack, flags, win, msg)
			slidewindowData.append(packet)
			slidewindowSeq.append(seq)
			connection.send(packet)
			seq += 1

		elif(feil > 0):
			print("")
			if feil == 4:
				feil = 0
				continue

		else:
			print("det skjedde en feil")
			connection.settimeout(0.5)
			print(acknowledgment)
			connection.send(slidewindowData[0])
			feil +=1

		if acknowledgment == b"finACK":
			break	
		
def client():

	client_socket = socket(AF_INET, SOCK_DGRAM)
	port = args.port # port
	server_ip = args.serverip # serverIp
	
	client_socket.connect((server_ip, port))
	print("Client connected with ", server_ip, ", port", port)


	message = args.filetransfer # get method with variable of the html file that is going to be displayed
	client_socket.send(message.encode())



	if args.reliable == "sw":
		stop_and_wait_sender(client_socket)

	elif args.reliable == "gbn":
		feil = 0
		GBN_sender(client_socket, feil)
	elif args.reliable == "sr":
		feil = 0
		SR_Sender(client_socket, feil)
	else:

		f = open(message, "rb")
		while True:
			msg = f.read(1460)
			#print(msg)
			if msg == b'':
				break
		
			client_socket.send(msg)

		client_socket.send("fin".encode())
	client_socket.close()

# Description: 
 # the server function creates a socket in UDP which is unreliable. 
 # a connection is made by using the port and ip when connected with the client it is now able to transfer a file.
 # Arguments:
 # ip & port: they use flags to be able to connect via the socket
 # try & except: the socket binds if the ip or port does not match with (client and server) then the system gets exited.
 # reliable: checks if the flag is used and calls on the stop_and_wait functions 
 # message, clientadress: 
 #
 #Returns: a copy of a img sent from the client side 
 #

def server():
	serverSocket = socket(AF_INET, SOCK_DGRAM) 
	serverPort = args.port
	server_ip = args.serverip

	try:
		serverSocket.bind((server_ip,serverPort))
	except:
		print("Binding did not work")
		sys.exit()

	print('A Simpleperf server is listening on port', serverPort, "\n")

	message, clientaddress = serverSocket.recvfrom(1460)
	message = message[:17].decode() # the name of the file (apollo_creed.jpg)

	if args.reliable == "sw":
		f = open("Copy-"+ message, "wb")
		teller = 0
		while True:
			msg = stop_and_wait_reciever(serverSocket, teller)
			teller += 1
			if msg == b'fin':
				break
			#print(msg)
			if not msg:
				break
			msg  
			f.write(msg)
		serverSocket.close()

	elif args.reliable == "gbn":
		f = open("Copy-"+ message, "wb")
		teller = 0
		sjekk = 1
		while True:
			msg = GBN_recviver(serverSocket, teller, sjekk)
			teller += 1

			
			h = msg [:12]
			msg = msg[12:]

			seq, ack, flags, win = parse_header(h)

			if msg == b'fin':
				break
			#print(msg)
			if not msg:
				break
			

			if(sjekk == seq): 
				f.write(msg)
				sjekk += 1

		serverSocket.close()
	elif  args.reliable == "sr":
		f = open("Copy-"+ message, "wb")
		teller = 0
		sjekk = 1
		arraymsg = []
		arrayseq = []
		while True:
			msg = SR_Recviever(serverSocket, teller, sjekk)
			teller += 1

			h = msg [:12]
			msg = msg[12:]

			seq, ack, flags, win = parse_header(h)

			if msg == b'fin':
				break
			#print(msg)
			if not msg:
				break
			arrayseq.append(seq)
			arraymsg.append(msg)

			if(seq == arrayseq[seq-1]):
				f.write(arraymsg[seq-1])
				sjekk += 1
			else:
				for i in range(len(arrayseq)-1):
					if(arrayseq[i] < arrayseq[i+1]):
						continue
					else:

						temp = arrayseq[i] 
						arrayseq[i] = arrayseq[i+1] 
						arrayseq[i+1] = temp 

						temp2 = arraymsg[i] 
						arraymsg[i] = arraymsg[i+1] 
						arraymsg[i+1] = temp2
			

	else:
				
		if message != "":
			serverSocket.sendto("ACK".encode(),	clientaddress)

		f = open("Copy-"+ message, "wb") # the html file gets opened

		while True:
			msg = serverSocket.recv(1460)
			if msg == b'fin':
				break
			#print(msg)
			f.write(msg)
		serverSocket.close()
		
		
# Description: 
 # this checks if either the client or server flag is used, when used a call is made to their respected functions
 # Arguments: 
 # if & elif: server flag is used and not client then the server() function is called and vice versa
 # if non of these two are used then an error is raised (you must run either in server or client mode)
 #

if args.server and not args.client:
	server()
elif args.client and not args.server:
	client()
else:
	raise argparse.ArgumentTypeError('you must run either in server or client mode')


