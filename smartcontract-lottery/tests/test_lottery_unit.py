from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.deploy import deploy_lottery, start_lottery, end_lottery
import pytest

from scripts.utils import LOCAL_BLOCKCHAIN_ENVS, fund_with_link, get_account, get_contract


def test_get_entrance_fee():
    """
    As of 2/23 @ 2:00pm ET:
    $2653 ~= 1 ETH
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # entrance fee = $50
    # from utils script: STARTING_PRICE = 200_000_000_000  # $2,000
    # 50/2000 = 0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert entrance_fee == expected_entrance_fee
    
def test_cannot_enter_lottery_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    lottery.startLottery({"from": get_account()})
    # Act
    lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == get_account()

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    lottery.startLottery({"from": get_account()})
    lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # Act
    lottery.endLottery({"from": get_account()})
    # Assert
    assert lottery.lottery_state() == 2

def test_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip()
    # Arrange
    main_acc = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": main_acc})
    lottery.enter({"from": main_acc, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": main_acc})

    starting_bal_main_acc = main_acc.balance()
    bal_of_lottery = lottery.balance()
    # Act
    request_id = transaction.events["RequestRandomness"]["requestId"]
    STATIC_RNG_NUM = 207
    get_contract("vrfcoordinator").callBackWithRandomness(request_id, STATIC_RNG_NUM, lottery.address, {"from": main_acc})
    # Assert
    print(main_acc.address,"\n", 
        get_account(index=1).address,"\n", 
        get_account(index=2).address)
    assert lottery.recentWinner() == main_acc       # 207 % 3 [players.length] = 0
    assert lottery.balance() == 0
    assert main_acc.balance() == starting_bal_main_acc + bal_of_lottery
