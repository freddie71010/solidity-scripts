from tracemalloc import start
from brownie import DoggieWalkNFTs, accounts, config, network
from .utils import get_account, LOCAL_BLOCKCHAIN_ENVS, get_contract, fund_with_link, print_line
import time


def deploy_doggies():
    account = get_account()
    doggieWalkNFTs = DoggieWalkNFTs.deploy(
        config["networks"][network.show_active()]["vrfcoordinator_v1"],
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash_v1"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", True),
    )
    print_line("Deployed!")
    return doggieWalkNFTs

def main():
    deploy_doggies()
