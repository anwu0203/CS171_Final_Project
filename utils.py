import hashlib



class PriorityQueue(object):
	def __init__(self):
		self.queue = []
		
	def __str__(self):
		return ' '.join([str(i) for i in self.queue])
 
	# for checking if the queue is empty
	def isEmpty(self):
		return len(self.queue) == 0
 
	# for inserting an element in the queue
	def insert(self, data):
		self.queue.append(data)

	# for popping an element based on Priority
	def delete(self):
		try:
			max_ind = 0
			for i in range(len(self.queue)):
				if self.queue[i] < self.queue[max_ind]:
					max_ind = i
			item = self.queue[max_ind]
			del self.queue[max_ind]
			return item
		except IndexError:
			print()
	
	def top(self):
		try:
			max_val = 0
			for i in range(len(self.queue)):
				if self.queue[i] < self.queue[max_val]:
					max_val = i
			item = self.queue[max_val]
			return item
		except IndexError:
			print()

class LamportClock:
	def __init__(self, pid):
		self.time = 0
		self.pid = pid

	def __init__(self, pid, time):
		self.time = time
		self.pid = pid
	
	def __str__(self):
		return f'{self.time} {self.pid}'

	def __repr__(self):
		return f'({self.time} {self.pid})'

	def inc_time(self):
		self.time += 1
		print("Local Time:", self.time)
	
	def sync(self, recv_clock):
		self.time = max(int((recv_clock).split(' ')[0]), self.time)
		self.inc_time()
	
	def get_time(self):
		return self.time
	
	def get_pid(self):
		return self.pid 
	
class BallotNum(LamportClock):
	# def __init__(self, pid):
	# 	super().__init__(pid)
	# 	# Depth I am aware of as a node
	# 	self.depth = 0 

	def __init__(self, pid, time=0, depth=0):
		super().__init__(pid, time)
		# Depth I am aware of as a node
		self.depth = depth 

	# Call when a node commits a block
	def inc_depth(self):
		self.depth += 1
		print("Local Depth:", self.depth)

	def get_depth(self):
		return self.depth
	
	def __str__(self):
		return f'{self.time},{self.pid},{self.depth}'

	def __repr__(self):
		return f'({self.time}, {self.pid}, {self.depth})'
	
	def __lt__(self, right):
		# Only going to respond if they are consistent nodes
		if self.get_depth() == right.get_depth():
			if self.get_time() != right.get_time():
				return self.get_time() < right.get_time()
			elif self.get_pid() != right.get_pid():
				return self.get_pid() < right.get_pid()
		else:
			return False
	
	def __le__(self, right):
		# Only going to respond if they are consistent nodes
		if self.get_depth() == right.get_depth():
			return self.get_time() <= right.get_time()
		else:
			return False
		
		

class HashPointer:
	def __init__(self, index, hash_prev):
		self.index = index
		self.hash_prev = hash_prev
	def get_hash(self):
		return self.hash_prev
	def get_index(self):
		return self.index

class HashBlock:
	def __init__(self, hash_ptr, transaction = None, nonce = None, llc = None):
		# Hash Pointer to the previous block
		self.hash_ptr = hash_ptr
		# String to be treated as the transaction
		self.transaction = transaction
		# Calculated nonce less than nonce string < NONCE_STRING
		self.nonce = nonce
		# Ballot Number / Timestamp associated with the transaction
		self.llc = llc
	# String representation of the hashblock
	def __str__(self):
		return f'{self.hash_ptr.get_hash()}{str(self.transaction)}{str(self.nonce)}'
	
	# Formatted representation of the hashblock with extra information not in the block (i.e. timestamp)
	# TODO: Update this for the specific app
	def __repr__(self):
		parsed = self.transaction.split('$')
		sender = parsed[0][:2]
		recepient = parsed[0][2:]
		amount = parsed[1]
		clock = self.llc.split(' ')
		return f'({sender}, {recepient}, ${amount}, {clock[0]}.{clock[1]}{clock[2]}, {self.hash_ptr.get_hash()})'
	
	# Getter for transaction found on this block (post or comment)
	def get_transaction(self):
		return self.transaction
	
	# Get the pointer (index of the previous block) to be able to access the previous hash block
	def get_prev_ptr(self):
		return self.hash_ptr.get_index()

class Blockchain:
	def __init__(self, difficulty):
		self._chain = []
		self._head = -1
		self.NONCE_STRING = difficulty

	def __str__(self):
		bc = "["
		i = 0
		while i <= self._head:
			bc += repr(self._chain[i])
			if i < self._head:
				bc += ", "
			i += 1
		bc += "]"
		return bc
	
	def append_block(self, transaction, llc):
		if self.valid_transaction(transaction):
			if len(self._chain) == 0: # This is our Genesis (First) Block
				hash_prev = (hex(0)[2:].zfill(64))
				h_ptr = HashPointer(-1, hash_prev)
				nonce = self.mine(hash_prev, transaction)
				self._chain.append(HashBlock(h_ptr, transaction, nonce, llc))
				self._head += 1		
			else: # This is not the first transaction, must verify the transaction is valid before appending 
				index = self._head # The index of the previous block
				hash_input = str(self._chain[index])
				hash_prev = hashlib.sha256(hash_input.encode('UTF-8')).hexdigest()
				h_ptr = HashPointer(index, hash_prev)
				nonce = self.mine(hash_prev, transaction)
				self._chain.append(HashBlock(h_ptr, transaction, nonce, llc))
				self._head += 1
			return True
		else:
			return False

	def sha256(self, str_in):
		hex_str = hashlib.sha256(str_in.encode('UTF-8')).hexdigest()
		return bin(int(hex_str,16))[2:].zfill(256)
	
	def mine(self, h_prev, trans):
		nonce = 0
		mining = True
		while mining:
			attempt = str(h_prev) + str(trans) + str(nonce)
			attempt = self.sha256(attempt)
			if self.valid_nonce(attempt):
				mining = False
				break
			nonce += 1
		return nonce
	
	def valid_nonce(self, attempt):
		if attempt < self.NONCE_STRING:
			return True
		return False
	
	def valid_transaction(self, transaction):
		return False
	
	# def valid_transaction(self, transaction):
	# 	sender = transaction[:2]
	# 	amount = int(transaction.split('$')[1])
	# 	sender_balance = int(self.balance(sender)[1:])
	# 	# print(sender, sender_balance, amount)
	# 	if (sender_balance - amount) < 0: # "Insufficient Balance"
	# 		return False
	# 	return True
	
	# def balance(self, client):
	# 	total = 10
	# 	# Traverse blockchain
	# 	i = self._head
	# 	while i >= 0:
	# 		# print("Traversing for:", client)
	# 		curr_transaction = self._chain[i].get_transaction()
	# 		client_pos = curr_transaction.find(client)
	# 		if client_pos == 0: # This transaction is an expense from the client
	# 			total -= int(curr_transaction.split('$')[1])
	# 		elif client_pos > 0: # This transaction is an gain from the client
	# 			total += int(curr_transaction.split('$')[1])
	# 		i = self._chain[i].get_prev_ptr()
	# 	return "$" + str(total)