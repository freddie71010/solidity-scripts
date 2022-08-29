from connect_to_pinata import PinataPy
import os
from dotenv import load_dotenv

load_dotenv()

def upload_images(image_pathway: str, collection_name: str, pinata_api_key: str, pinata_api_secret: str):

    # 1
    PinataUploader = PinataPy(pinata_api_key, pinata_api_secret, collection_name)
    
    # 2
    # folder_cid = "QmQczf6ByiW1cksYbghnU6fEGo7qYNQx1vJdhjmtVTPzRH"
    # PinataUploader = PinataPy(os.getenv("PINATA_API_KEY"), os.getenv("PINATA_API_SECRET"), collection_name, ipfs_hash=folder_cid)

    resp_pin_files = PinataUploader.pin_file_to_ipfs(image_pathway)
    print(resp_pin_files)
    
    resp_pin_list = PinataUploader.pin_list({"status": "pinned", "metadata[name]": collection_name})
    print(f"Pinned List: {resp_pin_list}")

    resp_ipfs_cids = PinataUploader.get_all_ipfs_file_cids()
    print(f"IPFS File CIDs: {resp_ipfs_cids}")


if __name__ == "__main__":
    upload_images(
        image_pathway = "./images/", 
        collection_name = os.getenv("COLLECTION_NAME"), 
        pinata_api_key = os.getenv("PINATA_API_KEY"),
        pinata_api_secret = os.getenv("PINATA_API_SECRET")
    )


# resp2 = PinataUploader.pin_file_to_ipfs("/home/fvs/solidity-scripts/nft-ipfs/images/shiba-inu2.png", ipfs_destination_path="doggie2-nfts")
# print(resp2)

# resp_pin_list1 = PinataUploader.pin_list({"status": "pinned"})
# print(resp_pin_list1)

# remove_hash = 'QmZYJxJ1m98JXi47pgjXcivhruy298YMXz75r8qXYh1Koy'
# print(PinataUploader.remove_pin_from_ipfs(remove_hash))


# https://gateway.pinata.cloud/ipfs/QmQomR1JgXuz4kiG56vwhrzcMekbzXmWWwpPPFNWb7kgW5
# https://gateway.pinata.cloud/ipfs/QmZYJxJ1m98JXi47pgjXcivhruy298YMXz75r8qXYh1Koy?filename=main-doggies
# https://gateway.pinata.cloud/ipfs/QmSsYRx3LpDAb1GZQm7zZ1AuHZjfbPkD6J7s9r41xu1mf8?filename=pug.png