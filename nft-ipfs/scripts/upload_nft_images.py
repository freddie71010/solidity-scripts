import os

from dotenv import load_dotenv

from scripts.utils import upload_files_to_ipfs

load_dotenv()

def upload_images(**kwargs) -> None:
    """ Pass-through function to upload_files_to_ipfs() """
    upload_files_to_ipfs(**kwargs)

def main():
    upload_images(
        folder_pathway = "./images/", 
        collection_name = os.getenv("COLLECTION_NAME"), 
        pinata_api_key = os.getenv("PINATA_API_KEY"),
        pinata_api_secret = os.getenv("PINATA_API_SECRET")
    )
