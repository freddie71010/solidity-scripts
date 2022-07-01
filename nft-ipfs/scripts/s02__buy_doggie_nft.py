from brownie import config, network, DoggieWalkNFT
from .utils import get_account, print_line, listen_for_event, get_breed
from .deploy_nft_collection_1 import deploy_collection
import os
from dotenv import load_dotenv

load_dotenv()

def buy_doggie_nft():
    account = get_account(env="MM1")
    doggie_nft_collectible = DoggieWalkNFT[-1]
    print_line(f"Doggie Collectible contract address: {doggie_nft_collectible.address}")
    starting_tx = doggie_nft_collectible.requestDoggie({"from": account})
    # starting_tx = doggie_nft_collectible.requestDoggie({"from": account, "amount": 10000000000000000})    # 0.01 eth
    starting_tx.wait(1)

    print_line("Mint Doggie has started!")
    event = listen_for_event(
        doggie_nft_collectible, "NftRequested", timeout=5*60, poll_interval=20
    )
    print(event)
    minted_breed_num = event["breed"]
    breed = doggie_nft_collectible.Breed[minted_breed_num]
    breed2 = get_breed(breed)
    tokenid = event["tokenId"]

    print(f"Doggie #{tokenid} is a {breed}!")
    print("end")

def main():
    deploy_collection(dogTokenURI_cids_filename=os.getenv("CIDS_TXT_FILE"))
    buy_doggie_nft()