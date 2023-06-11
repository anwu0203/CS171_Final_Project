from utils import Blockchain

class BlogChain(Blockchain):
	# Mostly for debugging, should use other init everytime with proper implementation
	def __init__(self):
		# Nonce string to mine for
		difficulty = '000' + '1'*253

		# Initialize the blockchain to mine for this diff.
		super().__init__(difficulty)

		# Where to append our committed transactions to, our backup file for testing
		# try:
		# 	self.backup_writer = open('/saves/backup_0.txt', 'a')
		# except FileNotFoundError:
		# 	# Create a new file
		# 	print('The backup file provided does not exist')
	
	# Initialization for restoring the blockchain from failure
	# def __init__(self, difficulty, backup_file_location):
	# 	# Nonce string to mine fordifficulty = '000' + '1'*253

	# 	# Initialize the blockchain to mine for this diff.
	# 	super.__init__(difficulty)

	# 	# Am I up-to-date?
	# 	self.valid = 0

	# 	# Read the file from top to bottom (first transaction to last) 
	# 	# And replicate the blockchain last stored in the backup file
	# 	# By simply adding the transactions in order
	# 	with open(backup_file_location, 'r') as reader:
	# 		pass
		
	# 	# Once we have loaded our backup, make sure we can we append to it
	# 	try:
	# 		self.backup_writer = open(backup_file_location, 'a')
	# 	except FileNotFoundError:
	# 		# Backup file did not exist, check if folder location is valid and create a new file with that backup name
	# 		# If the folder location does not exist, fail gracefully?
	# 		print('The backup file provided does not exist')

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