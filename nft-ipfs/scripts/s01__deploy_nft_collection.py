from brownie import config, network, DoggieWalkNFT
from .utils import get_account, print_line, get_publish_source, read_cid_summary_file
import os
from dotenv import load_dotenv

load_dotenv()

def deploy_collection(doggiewalk_cids_filename: str):
    (_, doggie_cids_list) = read_cid_summary_file(doggiewalk_cids_filename)
    
    account = get_account(env="MM1")
    # account = get_account(index=1)

    doggie_nft_collectible = DoggieWalkNFT.deploy(
        config["networks"][network.show_active()]["vrfcoordinator"],
        config["networks"][network.show_active()]["keyhash"],
        config["networks"][network.show_active()]["callback_gas_limit"],
        config["networks"][network.show_active()]["subscription_id"],
        doggie_cids_list,
        {"from": account},
        publish_source=get_publish_source()
    )
    _chainlink_subscription_warning()
    return doggie_nft_collectible


def _chainlink_subscription_warning():
    print_line("Deployed Doggie NFT Collectible!")
    print("")
    print_line("WARNING", char="*")
    print_line("MAKE SURE YOU ADD NEWLY DEPLOYED CONTRACT TO CHAINLINK SUBSCRIPTION - https://vrf.chain.link/", char="*")
    input("Add address as a 'Consumer' to VRF Chainlink Manager to continue. Push 'Enter' when ready:")


def main():
    deploy_collection(doggiewalk_cids_filename = os.getenv("CIDS_METADATA_FILE"))
    print("end")