from brownie import config, network, DoggieWalkNFT
from .utils import get_account, print_line, get_publish_source
import os
from dotenv import load_dotenv

load_dotenv()

def deploy_collection(dogTokenURI_cids_filename: str):
    (_, dog_token_uris_list) = _check_for_cids_file(dogTokenURI_cids_filename)
    
    account = get_account(env="MM1")
    doggie_nft_collectible = DoggieWalkNFT.deploy(
        config["networks"][network.show_active()]["vrfcoordinator_v2"],
        config["networks"][network.show_active()]["keyhash_v2"],
        config["networks"][network.show_active()]["callback_gas_limit_v2"],
        config["networks"][network.show_active()]["subscription_id"],
        dog_token_uris_list,
        {"from": account},
        publish_source=get_publish_source()
    )
    _chainlink_subscription_warning()
    return doggie_nft_collectible

def _check_for_cids_file(dogTokenURI_cids_filename: str):
    """Parses newly generated CIDs.txt file for all CIDs to be used 
    """
    # check if filename exists
    try: 
        with open(os.getcwd() + f"/uploaded_file_cids/{dogTokenURI_cids_filename}", "r") as f:
            dog_token_uris: dict = {}
            for line in f:
                data: list = line.strip().split("|")
                if data[1] == "dir":
                    continue
                dog_token_uris[data[0]] = data[2]

        dog_token_uris_list: list = list(dog_token_uris.values())
        print(dog_token_uris)
        print(dog_token_uris_list)
        return (dog_token_uris, dog_token_uris_list)
    except FileNotFoundError as e:
        print(e)

def _chainlink_subscription_warning():
    print_line("Deployed Doggie NFT Collectible!")
    print("")
    print_line("WARNING", char="*")
    print_line("MAKE SURE YOU ADD NEWLY DEPLOYED CONTRACT TO CHAINLINK SUBSCRIPTION - https://vrf.chain.link/", char="*")
    input("Add address as a 'Consumer' to VRF Chainlink Manager to continue. Push 'Enter' when ready:")

def main():
    deploy_collection(dogTokenURI_cids_filename=os.getenv("CIDS_TXT_FILE"))