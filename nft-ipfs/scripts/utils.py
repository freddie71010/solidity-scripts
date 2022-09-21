import json
import os
import time
import requests
from brownie import (AggregatorV3Mock, Contract, VRFCoordinatorV2Mock,
                     accounts, chain, config, network, web3)

from scripts.connect_to_pinata import PinataPy, ResponsePayload

DECIMALS = 8
STARTING_PRICE = 200_000_000_000  # == 2000e8 == 2,000

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]

contract_to_mock = {
    "eth_usd_price_feed": AggregatorV3Mock,
    "vrfcoordinator": VRFCoordinatorV2Mock,
}

# ---------------------------------------------------------------------------

def get_publish_source():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS \
    or not os.getenv("ETHERSCAN_TOKEN"):
        return False
    else:
        return True


def get_name_of_breed(breed_number):
    switch = {0: "PUG", 1: "SHIBA_INU", 2: "ST_BERNARD", 3: "SHIBA_INU_HAT"}
    return switch[breed_number]


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
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
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
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
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


def deploy_mocks():
    account = get_account()
    
    print_line(f"The active network is {network.show_active()}", char='-')
    print_line("Deploying mocks...")
    
    print("Deploying Mock ETH-USD Price Feed...")
    mock_price_feed = AggregatorV3Mock.deploy(
        DECIMALS, STARTING_PRICE, 
        {"from": account}
        )
    print(f"Deployed to {mock_price_feed.address}")

    print("Deploying Mock VRFCoordinatorV2...")
    mock_vrf_coordinator = VRFCoordinatorV2Mock.deploy(
        web3.Web3.toWei(0.1, "ether"), 1000000000, 
        {"from": account}
    )
    print(f"Deployed to {mock_vrf_coordinator.address}")
    
    print_line("Mocks deployed!", char='-')



def listen_for_event(brownie_contract, event, timeout=60, poll_interval=2):
    """Listen for an event to be fired from a contract.
    We are waiting for the event to return, so this function is blocking.
    Args:
        brownie_contract ([brownie.network.contract.ProjectContract]):
        A brownie contract of some kind.
        event ([string]): The event you'd like to listen for.
        timeout (int, optional): The max amount in seconds you'd like to
        wait for that event to fire. Defaults to 60 seconds.
        poll_interval ([int]): How often to call your node to check for events.
        Defaults to 2 seconds.
    """
    web3_contract = web3.eth.contract(
        address=brownie_contract.address, abi=brownie_contract.abi
    )
    start_time = time.time()
    current_time = time.time()
    event_filter = web3_contract.events[event].createFilter(fromBlock="latest")
    print(f"Checking for event ({event}) every {poll_interval} seconds for a total of {timeout} seconds...")
    while current_time - start_time < timeout:
        for event_response in event_filter.get_new_entries():
            if event in event_response.event:
                print("Found event!")
                return event_response
        print("...")
        time.sleep(poll_interval)
        current_time = time.time()
    print_line(f"Timeout of {timeout} seconds reached, no event found.")
    return {"event": None}

def read_cid_summary_file(cids_filename: str, set_collection_size_limit: bool = False) -> (dict, list):
    """
    Opens IPFS Summary file and returns only Dog associated data (excludes directories).
    """
    try: 
        with open(os.getcwd() + f"/ipfs_cids_summary/{cids_filename}", "r") as f:
            cids_summary_file: dict = json.load(f)
            for dog in list(cids_summary_file):
                if set_collection_size_limit and dog not in ['pug', 'st-bernard', 'shiba-inu']:
                    del cids_summary_file[dog]
                    continue
                if cids_summary_file[dog]["FileType"] == "dir":
                    del cids_summary_file[dog]
                    continue

        doggie_cids_list: list = [cids_summary_file[dog]['Hash'] for dog in cids_summary_file.keys()]
        if set_collection_size_limit:
            print("INFO: NFT Collection limited to 3 default Doggies.")
        else:
            print(f"INFO: NFT Collection has a length of {len(doggie_cids_list)} Doggies.")
        return (cids_summary_file, doggie_cids_list)
    except FileNotFoundError as e:
        raise(e)


def upload_files_to_ipfs(
        folder_pathway: str, 
        collection_name: str, 
        pinata_api_key: str, 
        pinata_api_secret: str) -> None:
    """ Runs three functions:
    1. Uploads a folder containing files to IPFS via PinataPy. 
    2. Pins the folder to the user's pinned list.
    3. Retrieves a list of all uploaded files' IPFS data (excludes nested directories).

    Args:
        folder_pathway (str): Location of folder to upload to IPFS
        collection_name (str): Folder name of uploaded folder as displayed on Pinata Cloud UI
        pinata_api_key (str): User API Key
        pinata_api_secret (str): User Secret Key
    """

    PinataUploader = PinataPy(pinata_api_key, pinata_api_secret, collection_name)
    resp_pin_files: ResponsePayload = PinataUploader.pin_file_to_ipfs(
        folder_pathway, 
        ipfs_destination_path=collection_name, 
        save_absolute_paths=False
    )
    print(f"Result: {resp_pin_files}")

    if resp_pin_files.get('isDuplicate') == False:
        resp_pin_list: ResponsePayload = PinataUploader.pin_list(
            {"status": "pinned", "metadata[name]": collection_name}
        )
        print(f"Pinned List: {resp_pin_list}")

    resp_ipfs_cids: dict = PinataUploader.download_ipfs_file_cids()
    print(f"IPFS File CIDs: {resp_ipfs_cids}")
