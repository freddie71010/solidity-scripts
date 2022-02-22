from brownie import (
    network,
    accounts,
    config,
    Contract,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interface
)
from web3 import Web3

DECIMALS = 8
STARTING_PRICE = 200_000_000_000  # 2,000
LOCAL_BLOCKCHAIN_ENVS = ["development", "ganache-local"]
FORKED_LOCAL_ENVS = ["mainnet-fork", "mainnet-fork-dev"]
contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrfcoordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def print_line(string, length=100, char='='):
    print(f"{string} {(length-len(string))*char}")

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVS
        or network.show_active() in FORKED_LOCAL_ENVS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    """
    This function grabs the contract addresses from the Brownie config (if defined), otherwise
    it will deploy a mock version of that contract and return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: the most recently deployed version of the contract
    """
    contract_type = contract_to_mock[contract_name]

    # Local Blockchains
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    # Testnet Blockchains
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks(decimals=DECIMALS, initial_value=STARTING_PRICE):
    print_line(f"The active network is {network.show_active()}", char='-')
    print_line("Deploying mocks...", char='-')
    MockV3Aggregator.deploy(
        decimals,
        initial_value,
        {"from": get_account()},
    )
    link_token = LinkToken.deploy({"from": get_account()})
    VRFCoordinatorMock.deploy(link_token.address, {"from": get_account()})
    print_line("Mocks deployed!", char='-')


def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000):  # 0.1 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address)  # interface
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print_line("Fund contract!")
    return tx

