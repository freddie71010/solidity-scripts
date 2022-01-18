import json

from solcx import compile_standard, install_solc
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

_solc_version = "0.6.0"
install_solc(_solc_version)

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

    # Compile our solidity
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version=_solc_version,
    )
# Outputs Compiled Code to a JSON file
with open("./compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# create Ganache connection
# w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
# chain_id = 5777
# my_address = "0xc97324eF2a664157913D2DE890a308153254AF8D"  # Ganache address 1 - workspace: INCOMPETENT-FACT
# private_key = os.getenv("GANACHE_ADD1_PRIVATE_KEY")
# print(f"Ganache: {private_key}")
# # # ganache-cli -p 7545 -m "explain divide million month balance arrange hour ball ripple floor know kiss" --chainId 5777

# Infura - Rinkeby
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/8ac19795cd9646aaadb2da412808b4bb")
)
chain_id = 4
my_address = "0xB1e2760Cc0Ad0557A14DAd306285A7720F31ECde"  # MetaMask - TEST_WALLET
private_key = os.getenv("MM_PRIVATE_KEY")
print(f"MetaMask: {private_key}")


# Create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get latest trans
nonce = w3.eth.getTransactionCount(my_address)
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
send_txn = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
receipt_txn = w3.eth.wait_for_transaction_receipt(send_txn)

simple_storage = w3.eth.contract(address=receipt_txn.contractAddress, abi=abi)
print("created contract!")

build_favorite_num_txn = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
sign_favorite_num_txn = w3.eth.account.sign_transaction(
    build_favorite_num_txn, private_key=private_key
)
send_favorite_num_txn = w3.eth.send_raw_transaction(
    sign_favorite_num_txn.rawTransaction
)
receipt_favorite_num_txn = w3.eth.wait_for_transaction_receipt(send_favorite_num_txn)
print("calling retrieve() after sending first transaction...")
print(simple_storage.functions.retrieve().call())
