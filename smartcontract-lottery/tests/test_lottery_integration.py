from brownie import network
from scripts.deploy import deploy_lottery
from scripts.utils import LOCAL_BLOCKCHAIN_ENVS, get_account, fund_with_link
import pytest
import time

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    account = get_account()
        
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
