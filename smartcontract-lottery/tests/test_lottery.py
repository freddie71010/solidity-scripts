from brownie import Lottery, accounts, config, network
from web3 import Web3


def test_get_entrance_fee():
    """
    As of 1/31 @ 3:30pm ET:
    $50 ~= 0.0186706497 ETH
    """
    account = accounts[0]
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": account},
    )
    entrance_fee = lottery.getEntranceFee()

    # assert entrance_fee > Web3.toWei(0.01750, "ether")
    # assert entrance_fee < Web3.toWei(0.01950, "ether")
