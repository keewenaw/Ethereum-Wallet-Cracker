# Ethereum Wallet Cracker
## (c) 2022 Keewenaw 

A script to steal Ether from wallets suffering from insufficient entropy during key generation.

At a high level, this script does the following:
*	Pulls entropy from all files in a given directory (normally pointed to a wordlist directory like Kali's '/usr/share/wordlists/')
*	Creates an Ethereum wallet from each unit of entropy
*	Saves the public and private keys of this new wallet into a CSV file for future use
* Checks the balance of the new wallet
* If the balance is greater than zero, transfers the balance to our predefined wallet

# Benefits:
* Unlimited entropy inputs
*	Multiple permutation attempts per entropy input
* Dynamic fee generation (with changeable margin of safety) to ensure your transaction goes through
* Reporting of all generated keypairs into user-specified file
* Granular verbosity settings

# Installation
## Manual
1) ```sudo apt install python3-pip```

2) ```pip3 install os sys csv configparser web3 eth_utils eth_account```

3) ```python3 ethereum-wallet-cracker.py```

# Project TODOs
*	Add more comprehensive permutations
   * main(), tempLine > maxByteLength - do every maxByteLength-length permutation of tempLine
   * main(), maxByteLength else - do every permutation of padding (1L-255R, 2L-254R, 3L-253R, etc)
*	Check for any ERC tokens, not just Ether specifically
* Check if this address ever had coins in it and if they were previously moved
*	Generate mnemonic phrases for secondary fuzzing - https://github.com/de-centralized-systems/python-bip39/
