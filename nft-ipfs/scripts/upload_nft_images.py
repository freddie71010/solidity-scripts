from .connect_to_pinata import PinataPy
import os
from dotenv import load_dotenv

load_dotenv()

def upload_images(image_pathway: str, collection_name: str, pinata_api_key: str, pinata_api_secret: str):

    PinataUploader = PinataPy(pinata_api_key, pinata_api_secret, collection_name)
    resp_pin_files = PinataUploader.pin_file_to_ipfs(
        image_pathway, 
        ipfs_destination_path=collection_name, 
        save_absolute_paths=False
    )
    print(f"Result: {resp_pin_files}")

    if resp_pin_files.get('isDuplicate') == False:
        resp_pin_list = PinataUploader.pin_list({"status": "pinned", "metadata[name]": collection_name})
        print(f"Pinned List: {resp_pin_list}")

    resp_ipfs_cids = PinataUploader.download_ipfs_file_cids()
    print(f"IPFS File CIDs: {resp_ipfs_cids}")


def main():
    upload_images(
        image_pathway = "./images/", 
        collection_name = os.getenv("COLLECTION_NAME"), 
        pinata_api_key = os.getenv("PINATA_API_KEY"),
        pinata_api_secret = os.getenv("PINATA_API_SECRET")
    )
