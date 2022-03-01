from brownie import network
from scripts.deploy import deploy_lottery
from scripts.utils import LOCAL_BLOCKCHAIN_ENVS, get_account, fund_with_link, wait_for_randomness
import pytest
import time

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    account = get_account(env="MM1")
    account2 = get_account(env="MM2")
        
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    entries = [account, account2, account, account2]
    for e in entries:
        lottery.enter({"from": e, "value": lottery.getEntranceFee()})
    
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    randomness = wait_for_randomness(lottery)

    assert lottery.recentWinner() == entries[randomness % len(entries)].address
    assert lottery.balance() == 0
