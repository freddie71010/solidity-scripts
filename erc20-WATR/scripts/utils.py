from brownie import (
    network,
    accounts,
    config,
    Contract,
    MockV3Aggregator,
)

DECIMALS = 8
STARTING_PRICE = 200_000_000_000  # == 2000e8 == 2,000
LOCAL_BLOCKCHAIN_ENVS = ["development", "ganache-local"]
FORKED_LOCAL_ENVS = ["mainnet-fork", "mainnet-fork-dev"]
contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
}


def print_line(string, length=100, char='='):
    print(f"{string} {(length-len(string))*char}")

def get_account(index=None, brownie_id=None, env=None):
    # Gets acc from pre-configured Brownie accs based on the passed index
    if index:
        return accounts[index]
    # Gets acc from Brownie's list of accs based on passed ID
    if brownie_id:
        return accounts.load(brownie_id)
    # Gets acc from the passed private key env
    if env:
        accounts.add(config["wallets"][env])
    # Gets the first acc from pre-configured Brownie accs while on a local or forked blockchain
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVS
        or network.show_active() in FORKED_LOCAL_ENVS
    ):
        return accounts[0]
    # Gets the first private key acc from env variables when on a mainnet/testnet
    return accounts.add(config["wallets"]["MM1"])


def get_contract(contract_name):
    """
    If on a local network, deploy a mock contract and return that contract.
    If on a mainnet/testnet network, return the deployed the contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: the most recently deployed version of the contract
    """
    contract_type = contract_to_mock[contract_name]

    # Local Blockchains
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVS:
        contract = contract_type[-1]
    # Mainnet/Testnet Blockchains
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract
