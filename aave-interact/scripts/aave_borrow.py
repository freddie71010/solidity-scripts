from brownie import network, config, interface
from .utils import get_account, print_line
from .get_weth import get_weth
from web3 import Web3

AMOUNT = Web3.toWei(0.1, "ether")

def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(config["networks"][network.show_active()]["lending_pool"])
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

def approve_erc20(spender, amount, erc20_address):
    print_line(f"Approving ERC20 token at address:{erc20_address}")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": get_account()})
    tx.wait(1)
    print_line("Approved")
    return tx

def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    print_line(f'lending_pool address: {lending_pool}')
    # Approve sending the ERC-20 tokens
    approve_erc20(lending_pool.address, AMOUNT, erc20_address)
