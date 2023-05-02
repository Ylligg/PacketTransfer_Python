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


def client():
	
	client_socket = socket(AF_INET, SOCK_DGRAM)
	port = args.port # port
	server_ip = args.serverip # serverIp
	
	client_socket.connect((server_ip, port))
	print("Client connected with ", server_ip, ", port", port)

	message = args.filetransfer # get method with variable of the html file that is going to be displayed
	client_socket.send(message.encode())

	f = open(message, "rb")
	while True:
		msg = f.readline()
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
	
		message = serverSocket.recv(1024).decode() #message gets recvived 
		
		f = open("Copy-"+message, "wb") # the html file gets opened
	
		#Send the content of the requested file to the client. It writes the content from the html file
		ww = b''
		while True:
			msg = serverSocket.recv(1024)
			if msg == b'fin':
				break
			#print(msg)
			f.write(ww)

		


if args.server and not args.client:
	server()
elif args.client and not args.server:
	client()
else:
	raise argparse.ArgumentTypeError('you must run either in server or client mode')
