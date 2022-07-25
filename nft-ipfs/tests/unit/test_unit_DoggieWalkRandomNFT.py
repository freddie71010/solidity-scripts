from brownie import DoggieWalkNFT, network, config
import pytest, os
from scripts import s01__deploy_nft_collection
from scripts.utils import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


def test_doggie_fee():
    # Arrange
    account = get_account()
    # Act
    doggie_nft_collectible = s01__deploy_nft_collection.deploy_collection(
        dogTokenURI_cids_filename=os.getenv("CIDS_TXT_FILENAME"))
    expected_doggie_fee = Web3.toWei(0.01, "ether")
    doggie_fee = doggie_nft_collectible.getMintFee()
    # Assert
    assert doggie_fee == expected_doggie_fee