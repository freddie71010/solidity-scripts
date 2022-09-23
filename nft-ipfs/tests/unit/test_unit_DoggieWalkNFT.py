from brownie import DoggieWalkNFT, accounts, network, config, reverts, web3 as brownie_web3
import pytest
from scripts.utils import (
    get_account,
    get_contract
)
from dotenv import load_dotenv

load_dotenv()

OWNER_ACC = get_account()

@pytest.fixture
def contract(scope="module"):
    return DoggieWalkNFT.deploy(
        get_contract("vrfcoordinatorV2"),
        config["networks"][network.show_active()]["keyhash"],
        config["networks"][network.show_active()]["callback_gas_limit"],
        config["networks"][network.show_active()]["subscription_id"],
        ['1','2','3','4'], # doggie_cids_list,
        {"from": OWNER_ACC},
    )

def test_getAllDogTokenUris(contract):
    assert contract.getAllDogTokenUris() == ['1','2','3','4']

def test_setMintFee_require(contract):
    with reverts("new mint fee must be different than the previous mint fee"):
        contract.setMintFee(brownie_web3.toWei(0.01, "ether"), {"from": OWNER_ACC})

def test_setMintFee(contract):
    contract.setMintFee(brownie_web3.toWei(0.10, "ether"), {"from": OWNER_ACC})
    assert contract.getMintFee() == brownie_web3.toWei(0.10, "ether")

def test_setChanceArray(contract):
    contract.setChanceArray([10,20,30,40], {"from": OWNER_ACC})
    contract.getChanceArray() == [10,20,30,40]
    
def test_setChanceArray_non_owner(contract):
    with reverts():
        contract.setChanceArray([10,20,30,40], {"from": accounts[1]})
