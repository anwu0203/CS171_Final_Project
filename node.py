# server.py
# Author: Jesus Oviedo, 9447947; Andy Wu, 7952278

import socket
import threading
from os import _exit
from sys import stdout
from time import sleep

import hashlib
import argparse

from utils import BallotNum
from utils import PriorityQueue
from utils import Blockchain

class BlogChain(Blockchain):
	# Mostly for debugging, should use other init everytime with proper implementation
	def __init__(self):
		# Nonce string to mine for
		difficulty = '000' + '1'*253

		# Initialize the blockchain to mine for this diff.
		super.__init__(difficulty)

		# Where to append our committed transactions to, our backup file for testing
		try:
			self.backup_writer = open('/saves/backup_0.txt', 'a')
		except FileNotFoundError:
			# Create a new file
			print('The backup file provided does not exist')
	
	# Initialization for restoring the blockchain from failure
	def __init__(self, difficulty, backup_file_location):
		# Nonce string to mine fordifficulty = '000' + '1'*253

		# Initialize the blockchain to mine for this diff.
		super.__init__(difficulty)

		# Am I up-to-date?
		self.valid = 0

		# Read the file from top to bottom (first transaction to last) 
		# And replicate the blockchain last stored in the backup file
		# By simply adding the transactions in order
		with open(backup_file_location, 'r') as reader:
			pass
		
		# Once we have loaded our backup, make sure we can we append to it
		try:
			self.backup_writer = open(backup_file_location, 'a')
		except FileNotFoundError:
			# Backup file did not exist, check if folder location is valid and create a new file with that backup name
			# If the folder location does not exist, fail gracefully?
			print('The backup file provided does not exist')

	# Function to call when we are up to date with our depth
	def validate(self):
		self.valid = 1
	
	# Must overwrite to adapt to the blog app
	# This function is ran before mining is attempted for the post/comment to make sure we are not committing anything we shouldn't
	# Returns:
	#  * True if valid transaction (If it is a post with a username and title -OR- a the post exist to comment on)
	#  * False otherwise
	def valid_transaction(self, transaction):
		return False

def connect():
	sleep(3)
	for portID, port in PORTS.items():
		if (portID != PID):
			try:
				out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				out_sock.connect((IP, port))
				raddr = out_sock.getpeername()
				out_socks[portID] = (out_sock, raddr)
				print(f"connected to {raddr[1]}", flush=True)
			except:
				print("exception in trying to connect to server", flush=True)
	sleep(1)
	for sockID, out_sock in out_socks.items():
		try:
			out_sock[0].sendall(bytes('Hi ' + PID, "utf-8"))
		except:
			print("exception in sending to server", flush=True)

	

def get_user_input():
	while True:
		user_input = input()
		# ********** Operator Commands **********
		if user_input == 'exit':
			# exit and close all connections
			for sockID, out_sock in out_socks.items():
				out_sock[0].close()
			stdout.flush()
			_exit(0)
		elif user_input == 'connect':
			threading.Thread(target=connect).start()
		elif user_input == 'print':
			for sockID, out_sock in out_socks.items():
				print(f'Outsock ID: {sockID} conn: {out_sock[0]} addr: {out_sock[1]}', flush=True)
			for sockID, in_sock in in_socks.items():
				print(f'Insock ID: {sockID} conn: {in_sock[0]} addr: {in_sock[1]}', flush=True)
		# ********** Protocol Commands **********
		elif user_input == 'crash':
			pass
		elif user_input == 'failLink':
			pass
		elif user_input == 'fixLink':
			pass
		elif user_input == 'blockchain':
			pass
		elif user_input == 'queue':
			pass
		# ********** Application Commands **********
		elif user_input == 'post':
			pass
			# 
		elif user_input == 'comment':
			pass
		elif user_input == 'blog':
			pass
		elif user_input == 'view':
			pass
		elif user_input == 'read':
			pass
		else:
			for sockID, out_sock in out_socks.items():
				try:
					out_sock[0].sendall(bytes(user_input, "utf-8"))
				except:
					print("exception in sending to server", flush=True)


def respond(conn, raddr):
	
	# listen for incoming messages
	while True:
		try:
			data = conn.recv(1024)
		except:
			print(f"exception in receiving data from {raddr[1]}", flush=True)
			break
		if not data:
			# close connection to node
			conn.close()
			try:
				out_socks.pop(pid)
			except:
				print(f"exception in disconnecting from {raddr[1]}", flush=True)
			try:
				in_socks.pop(pid)
			except:
				print(f"exception in disconnecting from {raddr[1]}", flush=True)
			print(f"connection closed from {raddr[1]}", flush=True)
			break

		data = data.decode()
		print(data)
		if data.startswith('Hi'):
			pid = data[3:]
			for portID, port in PORTS.items():
				if pid == portID:
					in_socks[portID] = (conn, raddr)
					break

			# test outward connection to target node
			sleep(3)
			try:
				out_socks[pid][0].sendall(bytes("connection check", "utf-8"))
				print("check success", flush=True)
			except:
				print(f"check failed {pid}, {port}", flush=True)
				try:
					out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					out_sock.connect((IP, port))
					raddr = out_sock.getpeername()
					out_socks[pid] = (out_sock, raddr)
					print(f"connected to {raddr[1]}", flush=True)
				except:
					print("exception in trying to connect to server", flush=True)
				sleep(1)
				for sockID, out_sock in out_socks.items():
					try:
						out_sock[0].sendall(bytes('Hi ' + PID, "utf-8"))
					except:
						print("exception in sending to server", flush=True)
			


if __name__ == "__main__":

	sleep(1)

	# get command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('pid', type=str, help='Node ID')
	args = parser.parse_args()

	# get PID, server IP, and node port number
	PID = args.pid
	IP = socket.gethostname()
	PORTS = {'P1':9291, 'P2':9292, 'P3':9293, 'P4':9294, 'P5':9295}
	LEADER = []
	# PORTS = [9291, 9292, 9293, 9294, 9295]
	PORT = PORTS[PID]
	
	# open listening socket
	in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	in_sock.bind((IP, PORT))
	in_sock.listen()

	# containers for connections
	out_socks = {}
	in_socks = {}

	global missing_replies
	missing_replies = [5]

	NONCE_STRING = '000' + '1'*253

	# Server Blockchain
	local_blog = BlogChain() # BlogChain(NONCE_STRING, 'backup/file/location.txt')
	
	# Server Ballot Number, contains local time and depth of our current blockchain
	ballot_num = BallotNum(PID)

	# Server Request Queue
	request_queue = PriorityQueue()

	# start thread for user input
	threading.Thread(target=get_user_input).start()
	threading.Thread(target=connect).start()

	# receive incoming connections
	while True:
		try:
			conn, addr = in_sock.accept()
			print(f"accepted connection from {addr[1]}", flush=True)
		except:
			print("exception in accepting incoming connection", flush=True)
			break
		threading.Thread(target=respond, args=(conn, addr)).start()