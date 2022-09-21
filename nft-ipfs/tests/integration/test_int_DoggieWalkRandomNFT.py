import pytest, os
from brownie import DoggieWalkNFT, network, config
from scripts.utils import (
    get_account,
    get_contract,
    listen_for_event,
    get_name_of_breed,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from dotenv import load_dotenv

load_dotenv()

def test_can_create_doggiewalknft():
    # Arrange
    account = get_account()
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for integration testing")

    doggie_nft_collectible = DoggieWalkNFT.deploy(
        get_contract("vrfcoordinator"),
        config["networks"][network.show_active()]["keyhash_v2"],
        config["networks"][network.show_active()]["callback_gas_limit_v2"],
        config["networks"][network.show_active()]["subscription_id"],
        [], # doggie_cids_list,
        {"from": account},
    )

    # Act
    doggie_nft_collectible.requestDoggie({"from": account})
    event = listen_for_event(
        doggie_nft_collectible, "NftRequested", timeout=5*60, poll_interval=20
    )
    print(event)
    minted_breed_num = event["breed"]
    breed = doggie_nft_collectible.Breed[minted_breed_num]
    breed2 = get_name_of_breed(breed)
    tokenid = event["tokenId"]

    print(f"Doggie #{tokenid} is a {breed}!")
    
    # Assert
    assert doggie_nft_collectible.getTokenCounter() > 0