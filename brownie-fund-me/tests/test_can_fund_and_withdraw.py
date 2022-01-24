from webbrowser import get
from brownie import accounts, FundMe, network, exceptions
from scripts.utils import *
from scripts.deploy import deploy_fund_me
import pytest


def test_can_fund():
    # Arrange
    account = get_account()
    # Act
    fundme = deploy_fund_me()
    starting_entrance_fee = fundme.getEntranceFee()
    tx = fundme.fund({"from": account, "value": starting_entrance_fee})
    tx.wait(1)
    # Assert
    assert fundme.addressToAmountFunded(account.address) == starting_entrance_fee


def test_can_withdraw():
    # Arrange
    account = get_account()
    # Act
    fundme = deploy_fund_me()
    starting_entrance_fee = fundme.getEntranceFee()
    tx = fundme.fund({"from": account, "value": starting_entrance_fee})
    tx.wait(1)
    tx2 = fundme.withdraw({"from": account})
    tx2.wait(1)
    # Assert
    assert fundme.addressToAmountFunded(account.address) == 0


def test_only_owner_can_withdraw():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVS:
        pytest.skip("Only for local testing")
    fundme = deploy_fund_me()
    bad_actor = accounts.add()
    with pytest.raises(exceptions.VirtualMachineError):
        fundme.withdraw({"from": bad_actor})
