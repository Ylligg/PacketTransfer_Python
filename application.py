from socket import *
import sys
import _thread as thread
from tabulate import tabulate
import time
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




def stop_and_wait_reciever(connectionserver):

		message, clientadress = connectionserver.recvfrom(1024)
		acknowledgment = "ACK"
		if message != ""
			connectionserver.sendto(acknowledgment, clientaddress)
	
		
def stop_and_wait_sender(connection):
		
		sequence_number = 1
		acknowledgment_number = 0
		packet = create_packet(sequence_number, acknowledgment_number, 2, 0, args.filetransfer.encode())
		


		connection.send(packet)

		while True:
			message, serveraddress = connection.recvfrom(1024)
			print(message)
			if message == "ACK":
				print(msg)
				break
			if(message != "ACK"):
				connection.settimeout(500)
				connection.sendto(packet, serveraddress)
				break
			
		sequence_number += 1
		acknowledgment_number += 1

		

def GBNorSR():
	if(args.reliable == "gbn"):

		print("gbn is used")
	elif(args.reliable == "sr"):

		print("sr is used")
	elif(args.reliable == "sw"):
		print("s&w is used")

	
def client():

	client_socket = socket(AF_INET, SOCK_DGRAM)
	port = args.port # port
	server_ip = args.serverip # serverIp
	
	client_socket.connect((server_ip, port))
	print("Client connected with ", server_ip, ", port", port)

	if args.reliable == "sw":
		stop_and_wait_sender(client_socket)

	else:
		message = args.filetransfer # get method with variable of the html file that is going to be displayed
		client_socket.send(message.encode())

		f = open(message, "rb")
		while True:
			msg = f.read(1024)
			#print(msg)
			if msg == b'':
				break
		

			client_socket.send(msg)
	client_socket.send("fin".encode())


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


		if args.reliable == "sw":
			stop_and_wait_reciever(serverSocket)
	
		message, clientaddress = serverSocket.recvfrom(1024)
		message = message[12:].decode()
		
		if message != "":
			serverSocket.sendto("ACK".encode(),	clientaddress)

		f = open("Copy-"+message, "wb") # the html file gets opened
	
		#Send the content of the requested file to the client. It writes the content from the html file
		while True:
			msg = serverSocket.recv(1024)
			if msg == b'fin':
				break
			print(msg)
			f.write(msg)
		serverSocket.close()
		


if args.server and not args.client:
	server()
elif args.client and not args.server:
	client()
else:
	raise argparse.ArgumentTypeError('you must run either in server or client mode')


if args.reliable == "gbn":
	GBNorSR()
elif args.reliavle =="sr":
	GBNorSR()
elif args.reliable == "s&w":
	stop_and_wait()
else:
	raise argparse.ArgumentTypeError('you must choose a reliable method')