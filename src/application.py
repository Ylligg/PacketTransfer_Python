from socket import *
import sys
import argparse 
import ipaddress 

parser = argparse.ArgumentParser(description="positional arguments", epilog="end of help")

parser.add_argument('-s', '--server', help='Activates the server side', action='store_true')
parser.add_argument('-c', '--client', help='Activates the client side',action='store_true')
parser.add_argument('-i', '--serverip', type=str, default='127.0.0.1')
parser.add_argument('-p', '--port', type=int, default=8088)

parser.add_argument('-r', '--reliable', type=str)
parser.add_argument('-t', '--testcase', type=str)
parser.add_argument('-f', '--filetransfer', type=str)

parser.add_argument('-S', '--SYN', type=str)
parser.add_argument('-A', '--ACK', type=int)
parser.add_argument('-F', '--FIN', type=int)
parser.add_argument('-R', '--Reset', type=str)

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

#print the header size: total = 12
print (f'size of the header = {calcsize(header_format)}')


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

#now let's create a packet with sequence number 1


data = b'0' * 1460
print (f'app data for size ={len(data)}')

sequence_number = 1
acknowledgment_number = 0
window = 0 # window value should always be sent from the receiver-side
flags = 0 # we are not going to set any flags when we send a data packet

#msg now holds a packet, including our custom header and data
msg = create_packet(sequence_number, acknowledgment_number, flags, window, data)

#now let's look at the header
#we already know that the header is in the first 12 bytes

header_from_msg = msg[:12]
print(len(header_from_msg))

#now we get the header from the parse_header function
#which unpacks the values based on the header_format that 
#we specified
seq, ack, flags, win = parse_header (header_from_msg)
print(f'seq={seq}, ack={ack}, flags={flags}, recevier-window={win}')

#let's extract the data_from_msg that holds
#the application data of 1460 bytes
data_from_msg = msg[12:]
print (len(data_from_msg))


#let's mimic an acknowledgment packet from the receiver-end
#now let's create a packet with acknowledgement number 1
#an acknowledgment packet from the receiver should have no data
#only the header with acknowledgment number, ack_flag=1, win=6400
data = b'' 
print('\n\nCreating an acknowledgment packet:')
print (f'this is an empty packet with no data ={len(data)}')

sequence_number = 0
acknowledgment_number = 1   #an ack for the last sequnce
window = 0 # window value should always be sent from the receiver-side

# let's look at the last 4 bits:  S A F R
# 0 0 0 0 represents no flags
# 0 1 0 0  ack flag set, and the decimal equivalent is 4
flags = 4 

msg = create_packet(sequence_number, acknowledgment_number, flags, window, data)
print (f'this is an acknowledgment packet of header size={len(msg)}')

#let's parse the header
seq, ack, flags, win = parse_header (msg) #it's an ack message with only the header
print(f'seq={seq}, ack={ack}, flags={flags}, receiver-window={win}')

#now let's parse the flag field
syn, ack, fin = parse_flags(flags)
print (f'syn_flag = {syn}, fin_flag={fin}, and ack_flag={ack}')

 # Description: 
 # this is the reciever side of the stop and wait which does this: it recieves a packet from the stop_and_wait_sender 
 # and if it is delivered to the reciever then an ACK messae is sent back to the client.
 # when all the packets is sent, the image is done copying and a finish packet is sent 
 # Arguments: 
 # ip: holds the ip address of the server
 # port: port number of the server
 # Use of other input and output parameters in the function
 # checks dotted decimal notation and port ranges 
 # Returns: .... and why?
 #

def stop_and_wait_reciever(connectionserver):

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

		if message != "":
			connectionserver.sendto(ackPacket, clientaddress)
		return message
		

def stop_and_wait_sender(connection):
		
		seq, ack, flags, win = 1,0,0,0

		message = args.filetransfer
		f = open(message, "rb")

		while True:

			msg = f.read(1460)
			if msg == b'':
				fin_packet = create_packet(0, 0, 2, 1, b'')
				connection.send(fin_packet)
				break

			packet = create_packet(seq, ack, flags, win, msg)
			connection.send(packet)


			acknowledgment, serveraddress = connection.recvfrom(1460)
			h = acknowledgment[:12]	
			acknowledgment = acknowledgment[12:]
			seq2, ack2, flags2, win2 = parse_header (h)
			print("ACK:", ack) # prints out the amount of ack

			if seq == ack2:
				ack = ack2
				seq += 1
			
			elif(seq != ack2):
				print("No ACK recived, resending packet")
				connection.settimeout(500)
				connection.send(packet)

		finish, serveraddress = connection.recvfrom(1460)
		h = finish[:12]	
		seq2, ack2, flags2, win2 = parse_header (h)
		syn, ack, fin = parse_flags(flags2)

		if fin > 0 and ack > 0:
			print("The process is finished")  




def GBN_recviver(serverconnection):
	teller = 0		
	slidewindowData = []
	slidewindowSeq = []
	

	while True:

		message, clientaddress = serverconnection.recvfrom(1472)
	
		if message == b'':
			break

		h = message[:12]
		message = message[12:]

		if len(h) < 12:
			break

		seq, ack, flags, win = parse_header (h)

		slidewindowData.append(message)
		slidewindowSeq.append(seq)

		if len(slidewindowSeq) == win:
			for i in range(win-1):
				
				if(slidewindowSeq[i]+1 == slidewindowSeq[i+1]):
					continue
				else:
					slidewindowSeq = []
					slidewindowData = []

			if (len(slidewindowSeq) == win):
				print(slidewindowSeq)
				slidewindowSeq.pop(0)
				slidewindowData.pop(0)
		

		teller += 1
		if(teller == 2):
			continue
		else:
			# ack packet that gets sent to the client
			ackPacket = create_packet(0, seq, 4, 5, b'')
			serverconnection.sendto(ackPacket, clientaddress)
		

		if message == b'fin':
			serverconnection.sendto("finACK".encode(), clientaddress)
			break
		
		print(f'seq={seq}, ack={ack}, flags={flags}, recevier-window={win}')
		
		
		for i in range(len(slidewindowData)):
			return slidewindowData[0]
		


def GBN_sender(connection):

	seq, ack, flags, win = 1,0,0,5

	message = args.filetransfer
	f = open(message, "rb")

	slidewindowData = []
	slidewindowSeq = []
	i = 0
	feil = 0


	while True:
		
		while i != win: 

			msg = f.read(1460)
			if msg == b'':
				connection.send("fin".encode())
				break
			packet = create_packet(seq, ack, flags, win, msg)
			slidewindowData.append(packet)
			slidewindowSeq.append(seq)
			connection.send(packet)	
			i +=1
			seq += 1
		
		
		acknowledgment, serveraddress = connection.recvfrom(1460)

		h = acknowledgment[:12]
		acknowledgment = acknowledgment[12:]
		seq2, ack2, flags2, win2 = parse_header (h)
		if slidewindowSeq[0] == ack2:
			print("det funker")
			slidewindowSeq.pop(0)
			slidewindowData.pop(0)
			ack = ack2
			feil = 0
			
			
		else:
			print("det skjedde en feil")
			connection.settimeout(500)
			print(acknowledgment)
			for i in range(len(slidewindowData)):
				connection.send(slidewindowData[i])
			
			ack = ack2
			feil = 1


		if feil == 1:
			print("her skjedde det feil aaaaah")
		else:
			print("funker")
			msg = f.read(1460)
			if msg == b'':

				connection.send("fin".encode())
				break

			packet = create_packet(seq, ack, flags, win, msg)
			slidewindowData.append(packet)
			slidewindowSeq.append(seq)
			connection.send(packet)
			print(slidewindowSeq)
			seq += 1

	
			
		if acknowledgment == b"finACK":
			break	
	
		print(slidewindowSeq)


def SR(serverconnection):

	while True:

		message, clientaddress = serverconnection.recvfrom(1472)
		h = message[:12]
		seq, ack, flags, win = parse_header (h)

	array = []
	array.len(win)

	for i in array:
		array[i] = i+1

	print (array)


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
		GBN_sender(client_socket)
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

		while True:
			msg = stop_and_wait_reciever(serverSocket)
			if msg == b'fin':
				break
			#print(msg)
			if not msg:
				break  
			f.write(msg)
		serverSocket.close()

	elif args.reliable == "gbn":
		f = open("Copy-"+ message, "wb")

		while True:
			msg = GBN_recviver(serverSocket)
			if msg == b'fin':
				break
			#print(msg)
			if not msg:
				break  
			f.write(msg)
		serverSocket.close()

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


