from tracemalloc import start
from brownie import WaterToken, accounts, config, network
from .utils import get_account, LOCAL_BLOCKCHAIN_ENVS, get_contract, print_line
import time


def deploy_water_token():
    account = get_account()
    water_token = WaterToken.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print_line("Deployed 100,000 Water ($WATR) tokens!")
    return water_token

def main():
    deploy_water_token()


    
