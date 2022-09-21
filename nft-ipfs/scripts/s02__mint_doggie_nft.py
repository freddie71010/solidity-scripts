from brownie import config, network, Contract, DoggieWalkNFT
from .utils import get_account, print_line, listen_for_event, get_name_of_breed
from .s01__deploy_nft_collection import deploy_collection
import os
from dotenv import load_dotenv

load_dotenv()

def mint_doggie_nft(*args):
    account = get_account(env="MM1")
    doggie_nft_collection = args[0] if args else DoggieWalkNFT[-1]
    print_line(f"Doggie Collectible contract address: {doggie_nft_collection.address}")
    starting_tx = doggie_nft_collection.requestDoggie({"from": account})
    # starting_tx = doggie_nft_collectible.requestDoggie({"from": account, "amount": 10000000000000000})    # 0.01 eth
    starting_tx.wait(1)

    print_line("Mint Doggie has started!")
    try:
        event = listen_for_event(
            doggie_nft_collection, "NftMinted", timeout=5*60, poll_interval=20
        )
        print(event)
        breed_name: str = get_name_of_breed(event.args.breed)

        print(f"Doggie ID#{event.args.tokenId} is a {breed_name}!")
    except Exception as e:
        print("No event found.")
    

def main():
    existing_collection = True
    collection_network = "rinkeby"
    number_to_mint = 5
    
    if existing_collection is True:    
        if network.show_active() != collection_network:
            network.disconnect()
            network.connect(collection_network)
        existing_contract = Contract.from_explorer(os.getenv("EXISTING_CONTRACT"))
        print(f"Connected to existing contract: {existing_contract.address}")
        for _ in range(number_to_mint):
            mint_doggie_nft(existing_contract)

    else:
        print("Deploying a new contract...")
        deploy_collection(doggiewalk_cids_filename = os.getenv("CIDS_METADATA_FILE"))
        for _ in range(number_to_mint):
            mint_doggie_nft()
    print("end")

    