import hashlib


class Block():
	def __init__(self, prev_ptr, prev_hash, post_type, username, title, content, nonce):
		self.prev_ptr = prev_ptr
		self.prev_hash = prev_hash
		self.post = [post_type, username, title, content]
		self.nonce = nonce
	
	def get_prev_ptr(self):
		return self.prev_ptr
	
	def get_prev_hash(self):
		return self.prev_hash
	
	def get_post(self):
		return self.post
	
	def get_nonce(self):
		return self.nonce


class BlogChain():
	def __init__(self):
		self.chain = []
		self.ptr = -1
		self.GENESIS_HASH = "0" * 64
	
	def find_nonce(self, post_type, username, title, content):
		# find valid nonce such that the sha256 hash begins with "000" given an input string
		if self.ptr == -1:
			# find genesis nonce
			input_string = self.GENESIS_HASH + post_type + username + title + content
		else:
			# find normal nonce
			prev_post = self.chain[self.ptr].get_post()
			prev_hash_input = (self.chain[self.ptr].get_prev_hash()) + prev_post[0] + prev_post[1] + prev_post[2] + prev_post[3] + str(self.chain[self.ptr].get_nonce())
			prev_hash = hashlib.sha256(prev_hash_input.encode('utf-8')).hexdigest()
			input_string = prev_hash + post_type + username + title + content

		nonce = 0
		while True:
			hash_val = hashlib.sha256((input_string + str(nonce)).encode('utf-8')).hexdigest()
			if (hash_val[0] == '0') or (hash_val[0] == '1'):
				return nonce
			nonce += 1
	
	def append(self, post_type, username, title, content, nonce):
		# append post to the blockchain given post_type ('POST' or 'COMMENT'), username, title, content, and nonce
		if self.ptr == -1:
			# create genesis block
			block = Block(-1, self.GENESIS_HASH, post_type, username, title, content, nonce)
			self.chain.append(block)
			self.ptr = 0
		else:
			# create normal block
			prev_post = self.chain[self.ptr].get_post()
			prev_hash_input = (self.chain[self.ptr].get_prev_hash()) + prev_post[0] + prev_post[1] + prev_post[2] + prev_post[3] + str(self.chain[self.ptr].get_nonce())
			prev_hash = hashlib.sha256(prev_hash_input.encode('utf-8')).hexdigest()
			block = Block(self.ptr, prev_hash, post_type, username, title, content, nonce)
			self.chain.append(block)
			self.ptr += 1
	
	def can_make_post(self, title):
		# return True if can make post, and False if not
		cur_ptr = self.ptr
		while cur_ptr != -1:
			cur_post = self.chain[cur_ptr].get_post()
			if cur_post[2] == title:
				return False
			cur_ptr = self.chain[cur_ptr].get_prev_ptr()
		return True
	
	def can_make_comment(self, title):
		# return True if can make comment, and False if not
		cur_ptr = self.ptr
		while cur_ptr != -1:
			cur_post = self.chain[cur_ptr].get_post()
			if cur_post[2] == title:
				return True
			cur_ptr = self.chain[cur_ptr].get_prev_ptr()
		return False
	
	def get_all_posts(self):
		# returns (title, username) of all posts on the blockchain in chronological order
		# if BlogChain is empty, return "BLOG EMPTY"
		ret = "]"
		cur_ptr = self.ptr
		while cur_ptr != -1:
			cur_post = self.chain[cur_ptr].get_post()
			if cur_post[0] == 'POST':
				ret = "(" + cur_post[2] + ", " + cur_post[1] + ")" + ret
				if cur_ptr > 0:
					ret = ", " + ret
			cur_ptr = self.chain[cur_ptr].get_prev_ptr()
		ret = "[" + ret
		
		if ret == "[]":
			return "BLOG EMPTY"
		else:
			return ret
			
	def get_user_posts(self, username):
		# returns list of (title, content) of all posts by the given user on the blockchain
		# if no posts under username, return "NO POST"
		ret = "]"
		cur_ptr = self.ptr
		while cur_ptr != -1:
			cur_post = self.chain[cur_ptr].get_post()
			if (cur_post[0] == 'POST') and (cur_post[1] == username):
				ret = "(" + cur_post[2] + ", " + cur_post[3] + ")" + ret
				if cur_ptr > 0:
					ret = ", " + ret
			cur_ptr = self.chain[cur_ptr].get_prev_ptr()
		ret = "[" + ret
		
		if ret == "[]":
			return "NO POST"
		else:
			return ret
	
	def get_post_content(self, title):
		# returns contents and comments of a post given its title
		# if not posts under title, return "POST NOT FOUND"
		ret = "]"
		cur_ptr = self.ptr
		while cur_ptr != -1:
			cur_post = self.chain[cur_ptr].get_post()
			if cur_post[2] == title:
				ret = "(" + cur_post[0] + ", " + cur_post[1] + ", " + cur_post[3] + ")" + ret
				if cur_ptr > 0:
					ret = ", " + ret
			cur_ptr = self.chain[cur_ptr].get_prev_ptr()
		ret = "[" + ret
		
		if ret == "[]":
			return "POST NOT FOUND"
		else:
			return ret
	
	def get_blogchain(self):
		# returns entire BlogChain
		ret = "]"
		cur_ptr = self.ptr
		while cur_ptr != -1:
			cur_post = self.chain[cur_ptr].get_post()
			prev_hash = self.chain[cur_ptr].get_prev_hash()
			nonce = self.chain[cur_ptr].get_nonce()
			ret = f"({prev_hash}, {cur_post[0]}, {cur_post[1]}, {cur_post[2]}, {cur_post[3]}, {nonce}){ret}"
			if cur_ptr > 0:
				ret = ", " + ret
			cur_ptr = self.chain[cur_ptr].get_prev_ptr()
		ret = "[" + ret
		return ret
	
	def get_data(self):
		# returns entire BlogChain without spaces
		ret = "]"
		cur_ptr = self.ptr
		while cur_ptr != -1:
			cur_post = self.chain[cur_ptr].get_post()
			prev_hash = self.chain[cur_ptr].get_prev_hash()
			nonce = self.chain[cur_ptr].get_nonce()
			ret = f"({prev_hash},{cur_post[0]},{cur_post[1]},{cur_post[2]},{cur_post[3]},{nonce}){ret}"
			if cur_ptr > 0:
				ret = "," + ret
			cur_ptr = self.chain[cur_ptr].get_prev_ptr()
		ret = "[" + ret
		return ret