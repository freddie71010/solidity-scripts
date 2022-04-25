from scripts.utils import get_account, print_line
from brownie import interface, network, config
from web3 import Web3

def get_weth():
    """
    Mints WETH by depositing ETH
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    deposit_amt = 0.1
    deposit_unit = "ether"
    tx = weth.deposit({"from":account, "value": Web3.toWei(deposit_amt, deposit_unit)})
    tx.wait(1)
    print_line(f"Deposited: {deposit_amt} {deposit_unit}")
    return tx


def main():
    get_weth()