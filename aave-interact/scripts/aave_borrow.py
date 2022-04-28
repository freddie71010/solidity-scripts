from builtins import print
from brownie import network, config, interface
from .utils import get_account, print_line, tx_divider
from .get_weth import get_weth
from web3 import Web3

AMOUNT = Web3.toWei(0.1, "ether")


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_address_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(spender, amount, erc20_address):
    print_line(f"Approving ERC20 token:{erc20_address}")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": get_account()})
    tx.wait(1)
    print_line("Approved!")
    return tx


def get_aave_user_data(lending_pool_contract, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_to_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool_contract.getUserAccountData(account.address)

    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    available_to_borrow_eth = Web3.fromWei(available_to_borrow_eth, "ether")
    print(f"Your provided collteral total:\t{total_collateral_eth}")
    print(f"Your total outstanding debt:\t{total_debt_eth}")
    print(f"Your amount available to borrow:\t{available_to_borrow_eth}")
    return (float(available_to_borrow_eth), float(total_debt_eth))


def borrow_dai(price_feed):
    price_feed = interface.AggregatorV3Interface

    # TO DO: 9:33:34 implement AggregatorV3Interface for Dai price feed


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool_contract = get_lending_pool()
    print_line(f"lending_pool: {lending_pool_contract}")
    # Approve sending the ERC-20 tokens
    approve_erc20(lending_pool_contract.address, AMOUNT, erc20_address)
    # Deposit ERC-20 tokens into AAVE
    print_line("Depositing...")
    tx = lending_pool_contract.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print_line("Deposited")
    # Get user AAVE data
    available_to_borrow_eth, total_debt_eth = get_aave_user_data(
        lending_pool_contract, account
    )
    # Borrow
    dai_eth_price_feed_address = config["networks"][network.show_active()][
        "dai_eth_price_feed"
    ]
    borrow_dai(dai_eth_price_feed_address)
