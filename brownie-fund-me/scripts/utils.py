from brownie import network, accounts, config, MockV3Aggregator
from web3 import Web3

DECIMALS = 8
STARTING_PRICE = 200_000_000_000  # 2000
LOCAL_BLOCKCHAIN_ENVS = ["development", "ganache-local"]
FORKED_LOCAL_ENVS = ["mainnet-fork", "mainnet-fork-dev"]


def get_account():
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVS
        or network.show_active() in FORKED_LOCAL_ENVS
    ):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(
            # DECIMALS, Web3.toWei(STARTING_PRICE, "ether"), {"from": get_account()}
            DECIMALS,
            STARTING_PRICE,
            {"from": get_account()},
        )
    print("Mocks deployed!")
