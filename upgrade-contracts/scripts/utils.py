import json
import os
import time
import eth_utils
from brownie import (
    Contract,
    # VRFCoordinatorV2Mock,
    accounts,
    config,
    network,
    web3 as brownie_web3,
)


DECIMALS = 8
STARTING_PRICE = 200_000_000_000  # == 2000e8 == 2,000

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]

CONTRACTS_TO_MOCK = {
    # "vrfcoordinatorV2": VRFCoordinatorV2Mock,
}

# ---------------------------------------------------------------------------


def get_publish_source() -> bool:
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or not os.getenv(
        "ETHERSCAN_TOKEN"
    ):
        return False
    else:
        return True


def print_line(string, length=100, char="=") -> None:
    print(f"{string} {(length-len(string))*char}")


def get_account(index: int = None, brownie_id: int = None, env: str = None):
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


def get_contract(contract_name: str):
    """
    If on a local network, deploy a mock contract and return that contract.
    If on a mainnet/testnet network, return the deployed contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: the most recently deployed version of the contract
    """
    contract_type = CONTRACTS_TO_MOCK[contract_name]
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

    print_line(f"Deploying mocks on network: {network.show_active()}", char="-")

    print("Deploying Mock VRFCoordinatorV2...", end="")
    mock_vrf_coordinator = VRFCoordinatorV2Mock.deploy(
        brownie_web3.toWei(0.1, "ether"), 1_000_000_000, {"from": account}
    )
    # vrfCoordinatorV2Mock = accounts[0].deploy(VRFCoordinatorV2Mock, 0.1, 0.1)
    mock_vrf_coordinator.createSubscription()
    mock_vrf_coordinator.fundSubscription(1, 10_000_000_000)
    print(f"Address: {mock_vrf_coordinator.address}")

    print_line("Mocks deployed!", char="-")


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
    web3_contract = brownie_web3.eth.contract(
        address=brownie_contract.address, abi=brownie_contract.abi
    )
    start_time = time.time()
    current_time = time.time()
    event_filter = web3_contract.events[event].createFilter(fromBlock="latest")
    print(
        f"Checking for event ({event}) every {poll_interval} seconds for a total of {timeout} seconds..."
    )
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


def encode_function_data(initializer=None, *args) -> bytes:
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
            The initializer function we want to call. Example: `box.store`.
            Defaults to None.
        args (Any, optional):
            The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade_contract(
    account,
    proxy_contract,
    new_implementation_address,
    proxy_admin=None,
    initializer=None,
    *args,
):
    """Upgrades a contract to a new version.
    Args:
        account ([brownie.network.account.Account])
        proxy_contract ([brownie.network.contract.ProjectContract])
        new_implementation_address (str):
            New address of implementation contract.
        proxy_admin ([brownie.network.contract.ProjectContract], optional)
        initializer ([brownie.network.contract.ContractTx], optional):
            The initializer function we want to call. Example: `box.store`.
            Defaults to None.
        args (Any, optional):
            The arguments to pass to the initializer function
    Returns:
        [bytes]: Return the encoded bytes.
    """
    # Admin is a ProxyAdmin contract
    if proxy_admin:
        if initializer:
            encode_initializer_call: bytes = encode_function_data(initializer, *args)
            txn = proxy_admin.upgradeAndCall(
                proxy_contract.address,
                new_implementation_address,
                encode_initializer_call,
                {"from": account},
            )
        else:
            txn = proxy_admin.upgrade(
                proxy_contract.address, new_implementation_address, {"from": account}
            )
    # Admin is a regular old wallet address
    else:
        if initializer:
            encode_initializer_call: bytes = encode_function_data(initializer, *args)
            txn = proxy_contract.upgradeToAndCall(
                new_implementation_address,
                encode_initializer_call,
                {"from": account},
            )
        else:
            txn = proxy_contract.upgradeTo(
                new_implementation_address, {"from": account}
            )
    print_line(
        f"Proxy contract upgraded! New implementation address: {new_implementation_address}"
    )
    return txn
