import json

from solcx import compile_standard, install_solc
from web3 import Web3

_solc_version = "0.6.0"
# install_solc(_solc_version)

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
# w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
# chain_id = 5777
# my_address = ""  # Ganache-cli
# private_key = "0x" + "0912cd34c0f0d83aec8982ba2fbac8c947a4af3c082315b1c09bc30d70adc950"

# w3 = Web3(Web3.HTTPProvider("http://0.0.0.0:7545"))
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 5777
my_address = "0xc97324eF2a664157913D2DE890a308153254AF8D"  # Ganache address 1 - workspace: INCOMPETENT-FACT
private_key = "0x" + "2cc07ee79cc3fc43047c1d8189e0b86e4ee1dabe08c10575895142b43e4bacd5"

# ganache-cli -p 7545 -m "explain divide million month balance arrange hour ball ripple floor know kiss" --chainId 5777


# w3 = Web3(Web3.HTTPProvider("http://172.29.224.1:7545"))
# chain_id = 5777
# my_address = "0x852F4fa210C8Ab7939e43b83333A221f2a4F2523"  # Ganache address 1 - workspace: MADDENING-ROLL
# private_key = "0x" + "0912cd34c0f0d83aec8982ba2fbac8c947a4af3c082315b1c09bc30d70adc950"

# Create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get latest trans
nonce = w3.eth.getTransactionCount(my_address)
print(nonce)
