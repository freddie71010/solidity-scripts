from brownie import (
    network,
    accounts,
    config,
    chain,
    Contract,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
)
from web3 import Web3
import requests
import time

DECIMALS = 8
STARTING_PRICE = 200_000_000_000  # == 2000e8 == 2,000
LOCAL_BLOCKCHAIN_ENVS = ["development", "ganache-local"]
FORKED_LOCAL_ENVS = ["mainnet-fork", "mainnet-fork-dev"]
contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrfcoordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def print_line(string, length=100, char="="):
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
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    # Mainnet/Testnet Blockchains
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks(decimals=DECIMALS, initial_value=STARTING_PRICE):
    print_line(f"The active network is {network.show_active()}", char="-")
    print_line("Deploying mocks...", char="-")
    MockV3Aggregator.deploy(
        decimals,
        initial_value,
        {"from": get_account()},
    )
    link_token = LinkToken.deploy({"from": get_account()})
    VRFCoordinatorMock.deploy(link_token.address, {"from": get_account()})
    print_line("Mocks deployed!", char="-")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address)  # interface
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print_line("Fund contract with LINK complete!")
    return tx


def wait_for_randomness(lottery):
    # Keeps checking for a fulfillRandomness callback using the block explorer's API, and returns the randomness

    # Initial frequency, in seconds
    sleep_time = 120
    # Last checked block num
    from_block = len(chain)
    print("Waiting For Data...\n")
    i = 1

    # Until randomness received
    while True:
        print(f"Checking #{i} in {sleep_time} secs...\n")
        # Wait
        time.sleep(sleep_time)
        # Get last mined block num
        to_block = len(chain)

        # Check if randomness received
        # 🔗 See https://docs.etherscan.io/api-endpoints/logs
        response = requests.get(
            config["networks"][network.show_active()]["explorer_api"],
            params={
                "module": "logs",
                "action": "getLogs",
                "fromBlock": from_block,
                "toBlock": to_block,
                "address": lottery.address,
                "topic0": Web3.keccak(text="RandomnessReceived(uint256)").hex(),
                "apikey": config["api_keys"]["etherscan"],
            },
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
            },
        ).json()
        # Return randomness if received
        if response["status"] == "1":
            print(f"Randomness received!\n")
            return int(response["result"][0]["topics"][0], 16)

        # Half sleep time if longer than 15 seconds
        if sleep_time > 15:
            sleep_time /= 2

        i += 1
