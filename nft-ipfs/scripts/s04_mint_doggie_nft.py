import os

from brownie import Contract, DoggieWalkNFT, web3 as brownie_web3
from dotenv import load_dotenv

from .s03_deploy_nft_collection import deploy_collection
from .utils import get_account, get_name_of_breed, listen_for_event, print_line

load_dotenv()

def mint_doggie_nft(**kwargs):
    account = get_account(env="MM1")
    doggie_nft_collection = kwargs.get('contract', DoggieWalkNFT[-1])
    print_line(f"Doggie Collectible contract address: {doggie_nft_collection.address}")
    starting_tx = doggie_nft_collection.requestDoggie(
        {"from": account, "amount": kwargs.get('fee', brownie_web3.toWei(0.01, "ether")) + 100}
    )
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
    existing_collection = False
    number_to_mint = 5
    mint_fee = brownie_web3.toWei(0.02, "ether")
    
    if existing_collection is True:    
        existing_contract = Contract.from_explorer(os.getenv("EXISTING_CONTRACT"))
        print(f"Connected to existing contract: {existing_contract.address}")
        for _ in range(number_to_mint):
            mint_doggie_nft(contract=existing_contract, fee=mint_fee)
    else:
        print("Deploying a new contract...")
        deploy_collection(doggiewalk_cids_filename = os.getenv("CIDS_METADATA_FILE"))
        for _ in range(number_to_mint):
            mint_doggie_nft(fee=mint_fee)
    print("end")

    