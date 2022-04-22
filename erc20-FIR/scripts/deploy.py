from tracemalloc import start
from brownie import FireToken, accounts, config, network
from .utils import get_account, LOCAL_BLOCKCHAIN_ENVS, get_contract, fund_with_link, print_line
import time


def deploy_fire_token():
    account = get_account()
    fire_token = FireToken.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print_line("Deployed FIR Token!")
    return fire_token

def main():
    deploy_fire_token()

    
