# server.py
# Author: Jesus Oviedo, 9447947; Andy Wu, 7952278

import socket
import threading
from os import _exit
from sys import stdout
from time import sleep
from time import time
from queue import Queue
from queue import PriorityQueue
import argparse


from utils import BallotNum
from BlogChain import BlogChain

def connect():
	global missing_replies
	global out_socks
	global in_socks
	global PID
	global LEADER
	global local_blog
	global req_num
	global ballot_num
	global accept_num
	global val_dict
	global accepted_promises
	global promise_count
	global accept_count
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
			out_sock[0].sendall(bytes('Hi?/' + PID, "utf-8"))
		except:
			print("exception in sending to server", flush=True)

# Generic logic for phase II: Accept - Proposer
def broadcast_accept(val):
	global missing_replies
	global out_socks
	global in_socks
	global PID
	global LEADER
	global local_blog
	global req_num
	global ballot_num
	global accept_num
	global val_dict
	global accepted_promises
	global promise_count
	global accept_count
	null_count = 1
	accept_nums = []
	if (promise_count[0]) >= 3:
		# We have acheived a majority time to broadcast our accepted value
		# Consume the accepted promises
		# WE ARE ALSO NOW THE LEADER \(￣︶￣*\))
		print(accepted_promises, flush=True)
		for msg in accepted_promises:
			accept_nums.append(msg[1])
			if (msg[2] != 'None') and (msg[3] < req_num[0]):
				break
			null_count += 1
		if(null_count >= 3):
			# They have not seen anything different than what I have proposed
			# The value that I want to propose is going to be the val I broadcast
			accepted_promises.clear()
			accept_msg = 'ACCEPT?/' + str(ballot_num) + '+/' + val + '+/' + str(req_num[0])
			for sockID, out_sock in out_socks.items():
				try:
					out_sock[0].sendall(bytes(accept_msg, "utf-8"))
					print("Sent:",accept_msg, flush=True)
				except:
					print("exception in sending to server", flush=True)
		else:
			# TODO: Get the max of the vals in the accepted_promises from the majority
			best_ballot = accept_nums[0]
			best_val = accepted_promises[0][2]
			for msg in accepted_promises:
				if best_ballot < msg[1]:
					best_ballot = msg[1] 
					best_val = msg[2]
			accept_msg = 'ACCEPT?/' + str(best_ballot) + '+/' + best_val + '+/' + str(req_num[0])
			for sockID, out_sock in out_socks.items():
				try:
					out_sock[0].sendall(bytes(accept_msg, "utf-8"))
					print("Sent:",accept_msg, flush=True)
				except:
					print("exception in sending to server", flush=True)
			pass				

def handle_leader_tasks(event):
	global missing_replies
	global out_socks
	global in_socks
	global PID
	global LEADER
	global local_blog
	global req_num
	global ballot_num
	global accept_num
	global val_dict
	global accepted_promises
	global promise_count
	global accept_count
	while True:
		if event.is_set():
			sleep(0.1)
		# We are the leader and should consume from our request queue
		else:
			if(not request_queue.empty()):
				op, val = request_queue.get().split('(').strip(')')
				# Compute nonce 
				# Begin Phase II
				broadcast_accept(val)
				
				start = time()
				end = start + timeout
				accept_count[0] += 1
				while((accept_count[0] < 3) and (time() < end)):
					sleep(0.1)
				# WE CAN DECIDE NOW WOOHOO
				if accept_count[0] >= 3:
					# Append the proposed block to the blockchain
					# Apply the corresponding operation to its blog
					decide_msg = 'DECIDE' + '?/' + str(ballot_num) + '+/' + val + '+/' + str(req_num[0]) 
					for sockID, out_sock in out_socks.items():
						try:
							out_sock[0].sendall(bytes(decide_msg, "utf-8"))
							print("Sent:",decide_msg, flush=True)
						except:
							print("exception in sending to server at", out_sock[1], flush=True)
					pass
				else:
					# We failed to reach a majority of ACCEPTED
					# Fail and try again after some time?
					pass

				


def process_user_input(event):
	global missing_replies
	global out_socks
	global in_socks
	global PID
	global LEADER
	global local_blog
	global req_num
	global ballot_num
	global accept_num
	global val_dict
	global accepted_promises
	global promise_count
	global accept_count
	while True:
		# if event.is_set():
		# 	sleep(0.1)
		# else:
		if(not input_queue.empty()):
			# Process the top request
			command = input_queue.get()
			# Check if we need to acheive consesnus to process the command
			if command.startswith('post') or command.startswith('comment'):
				# Otherwise, begin leader election and/or repair ?
				if not LEADER:
					ballot_num.inc_time()
					val_dict['propose_val'] = command.split('(')[1].strip(')')
					decide_msg = 'PREPARE' + '?/' + str(ballot_num) + '+/' + str(req_num[0]) 
					
					start = time()
					end = start + timeout
					promise_count[0] += 1
					for sockID, out_sock in out_socks.items():
						try:
							out_sock[0].sendall(bytes(decide_msg, "utf-8"))
							print("Sent:",decide_msg, flush=True)
						except:
							print("exception in sending to server at", out_sock[1], flush=True)
					while((promise_count[0] < 3) and (time() < end)):
						print("waiting for promises",promise_count[0], end,  flush=True)
						sleep(0.1)
					if (promise_count[0]) < 3:
						print('We not the leader :(', flush=True)
					else:
						LEADER.append(PID)
						
						broadcast_accept(val_dict['propose_val'])
						start = time()
						end = start + timeout
						accept_count[0] += 1
						while((accept_count[0] < 3) and (time() < end)):
							print("waiting for accepted", flush=True)
							sleep(0.1)
						if accept_count[0] < 3:
							# We failed to reach a majority of ACCEPTED
							# Fail and try again after some time?
							print('Accept Failed but we are the leader', flush=True)
						else:
							# Append the proposed block to the blockchain
							# Apply the corresponding operation to its blog
							decide_msg = 'DECIDE' + '?/' + str(ballot_num) + '+/' + val_dict['propose_val'] + '+/' + str(req_num[0]) 
							for sockID, out_sock in out_socks.items():
								try:
									out_sock[0].sendall(bytes(decide_msg, "utf-8"))
									print("Sent:", decide_msg, flush=True)
								except:
									print("exception in sending to server at", out_sock[1], flush=True)

				# Check if we are the leader 
				elif LEADER[0] == PID:
					# If we are, begin phase two increment our request_num/index for log entry
					request_queue.put((req_num[0], input_queue.get()))
				# If we are not and know one, pass the post command to the leader
				else:
					try:
						out_socks[LEADER[0]].out_sock[0].sendall(bytes(input_queue.get(), "utf-8"))
						print("Sent:",input_queue.get(), flush=True)
					except:
						print("exception in sending to leader", flush=True)
						# Let the election start again, by saying we know no leader
						LEADER.clear()
						input_queue.put(command)
			else:
				if command.startswith('failLink'):
					target = command[9:]
					for sockID, out_sock in out_socks.items():
						if target == sockID:
							out_sock[0].close()
				elif command.startswith('fixLink'):
					target = command[8:]
					flag_linked = False
					for sockID, out_sock in out_socks.items():
						if target == sockID:
							flag_linked = True
							break
					if not flag_linked:
						try:
							port = PORTS[target]
						except:
							print(f'Invalid target: {target}', flush=True)
						try:
							out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							out_sock.connect((IP, port))
							raddr = out_sock.getpeername()
							out_socks[target] = (out_sock, raddr)
							print(f"connected to {raddr[1]}", flush=True)
						except:
							print("exception in trying to connect to server", flush=True)
						sleep(1)
						try:
							out_sock.sendall(bytes('Hi?/' + PID, "utf-8"))
						except:
							print("exception in sending to server", flush=True)
				elif command.startswith('view'):
					username = command[5:]
					print(local_blog.get_user_posts(username), flush=True)
				elif command.startswith('read'):
					title = command[5:]
					print(local_blog.get_post_content(title), flush=True)
				elif command == 'blockchain':
					print(local_blog.get_blogchain(), flush=True)
				elif command == 'queue':
					print_q_flag = True
					for op in list(request_queue.queue):
						if print_q_flag:
							print(op, end='', flush=True)
							print_q_flag = False
						else:
							print(f', {op}', end='', flush=True)
				elif command == 'blog':
					print(local_blog.get_all_posts(), flush=True)
		else:
			sleep(0.1)



def get_user_input():
	global missing_replies
	global out_socks
	global in_socks
	global PID
	global LEADER
	global local_blog
	global req_num
	global ballot_num
	global accept_num
	global val_dict
	global accepted_promises
	global promise_count
	global accept_count
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
			for sockID, out_sock in out_socks.items():
				out_sock[0].close()
			stdout.flush()
			_exit(0)
		elif user_input.startswith('failLink'):
			input_queue.put(user_input)
		elif user_input.startswith('fixLink'):
			input_queue.put(user_input)
		elif user_input == 'blockchain':
			input_queue.put(user_input)
		elif user_input == 'queue':
			input_queue.put(user_input)
		# ********** Application Commands **********
		# If it is a application command and requires replication add it to our queue
		elif user_input.startswith('post'):
			input_queue.put(user_input)
		elif user_input.startswith('comment'):
			input_queue.put(user_input)
		elif user_input == 'blog':
			input_queue.put(user_input)
		elif user_input.startswith('view'):
			input_queue.put(user_input)
		elif user_input.startswith('read'):
			input_queue.put(user_input)
		else:
			# UNCOMMENT: to broadcast messages

			for sockID, out_sock in out_socks.items():
				try:
					out_sock[0].sendall(bytes(user_input, "utf-8"))
					print("Sent:",user_input, flush=True)
				except:
					print("exception in sending to server", flush=True)
		

def handle_msg(data, conn, raddr):
	global missing_replies
	global out_socks
	global in_socks
	global PID
	global LEADER
	global local_blog
	global req_num
	global ballot_num
	global accept_num
	global val_dict
	global accepted_promises
	global promise_count
	global accept_count
	if data:
		print("Processing:", data, flush=True)
		if (data.count('?/') > 0):
			op, message = data.split('?/')

			if op == 'Hi':
				pid = message
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
					try:
						out_sock.sendall(bytes('Hi?/' + PID, "utf-8"))
					except:
						print("exception in sending to server", flush=True)
			# ********* Participant/Acceptor *********
			elif op == 'PREPARE':
				# The message contatins the ballot number
				bal, req =  message.split('+/')
				sequence_num, pid, depth = bal.split(',')
				bal = BallotNum(pid, int(sequence_num), int(depth))
				# Respond ONLY IF the ballot num of the proposer is of equal depth and newer(of a greater PID if equal time)
				if (ballot_num <= bal) and (req_num[0] <= int(req)):
					# Update our ballot_num
					ballot_num = bal
					req_num[0] = int(req)
					if not LEADER:
						LEADER.append(pid)
					else:
						LEADER[0] = pid
					reply = 'PROMISE?/' + str(bal) + '+/' + str(accept_num) + '+/' + (val_dict['accept_val']) + '+/' + str(req_num[0])
					try:
						out_socks[pid][0].sendall(bytes(reply, "utf-8"))
						print("Sent:", reply, flush=True)
					except: 
						print("exception in sending to proposer at", raddr, flush=True) 
				
			elif op == 'ACCEPT':
				bal, v, req =  message.split('+/')
				sequence_num, pid, depth = bal.split(',')
				b = BallotNum(pid, int(sequence_num), int(depth))
				if not LEADER:
					LEADER.append(pid)
				else:
					LEADER[0] = pid
				if (ballot_num <= b)and (req_num[0] <= int(req)):
					accept_num = b
					val_dict['accept_val'] = v
					reply = 'ACCEPTED?/' + str(b) + '+/' + str(v) + '+/' + str(req_num[0])
					try:
						out_socks[pid][0].sendall(bytes(reply, "utf-8"))
						print("Sent:", reply, flush=True)
					except: 
						print("exception in sending to proposer at", raddr, flush=True)
				pass
			elif op =='DECIDE':
				# TODO: Commit the value in the decide message (we already saved it) to disk
				bal, v, req =  message.split('+/')
				print('I', PID, 'DECIDE:', v, flush=True)
				pass
			# ********* Proposer/Leader *********
			elif op == 'PROMISE':
				# Ensure a majority
				if (promise_count[0]) < 3:
					# Store messages in case we discover a value here that has been accepted
					bal, b, val, req =  message.split('+/')
					sequence_num, pid, depth = bal.split(',')
					accept_sequence_num, accept_pid, accept_depth = b.split(',')
					bal = BallotNum(pid, int(sequence_num), int(depth))
					b = BallotNum(accept_pid, int(accept_sequence_num), int(accept_depth))
					promise_msg = (bal, b, val, int(req))
					# Only respond to messages with right ballot_num for the leader we know of 
					print("\rProsposed ballot:", bal, flush=True)
					if(bal == ballot_num):
						accepted_promises.append(promise_msg)
				promise_count[0] += 1

			elif op == 'ACCEPTED':
				if (accept_count[0]) < 3:
					bal, v, req =  message.split('+/')
					sequence_num, pid, depth = bal.split(',')
					b = BallotNum(pid, int(sequence_num), int(depth))
					accept_msg = (b, v, int(req))
					# Only respond to messages with right ballot_num for the leader we know of 
					if(b == ballot_num):
						accepted_promises.append(accept_msg)
						accept_count[0] += 1
					if(accept_count[0] == 3):
						threading.Thread(target=handle_leader_tasks, args=(event,)).start()




def respond(conn, raddr):
	global missing_replies
	global out_socks
	global in_socks
	global PID
	global LEADER
	global local_blog
	global req_num
	global ballot_num
	global accept_num
	global val_dict
	global accepted_promises
	global promise_count
	global accept_count
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
			for sockID, in_sock in in_socks.items():
				if in_sock[1] == raddr:
					try:
						out_socks[sockID][0].close()
						out_socks.pop(sockID)
					except:
						print(f"exception in disconnecting from {raddr[1]}", flush=True)
					try:
						in_socks.pop(sockID)
					except:
						print(f"exception in disconnecting from {raddr[1]}", flush=True)
					print(f"connection closed from {raddr[1]}", flush=True)
					break
			break

		data = data.decode()
		print(data, flush=True)
		# Append the request to the queue and pop the newest message 
		# spawn a new thread to handle message ? unsure how to not block receiving but still keeping track of all of the messages 
		# so simulated network delay and message handling don't block receive
		threading.Thread(target=handle_msg, args=(data, conn, raddr)).start()

if __name__ == "__main__":

	global missing_replies
	global out_socks
	global in_socks
	global PID
	global LEADER
	global local_blog
	global req_num
	global ballot_num
	global accept_num
	global val_dict
	global request_queue
	global input_queue
	global accepted_promises
	global promise_count
	global accept_count

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

	
	missing_replies = [5]
	timeout = 10

	NONCE_STRING = '000' + '1'*253

	# Server Blockchain
	local_blog = BlogChain() # BlogChain(NONCE_STRING, 'backup/file/location.txt')

	# Server Request Number
	req_num = [0]
	
	# Server Ballot Number, most recent accepted ballotNum
	# Only changes during leader election
	ballot_num = BallotNum(PID)
	# This should beat all processes at the start, not used for comparison
	accept_num = BallotNum('P0')
	# The transaction string that is accepted and to be comitted and attached  
	val_dict = {'accept_val':'None', 'propose_val':'None' }
	# Server Request Queue
	request_queue = PriorityQueue()
	# Accepted Promises (for when node is the leader)
	accepted_promises = []
	promise_count = [0]
	accept_count = [0]
	# start thread for user input
	event = threading.Event()
	input_queue = Queue()

	threading.Thread(target=get_user_input).start()
	threading.Thread(target=process_user_input, args=(event,)).start()
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