import json
from brownie import config, network, Contract, DoggieWalkNFT
from scripts.utils import get_account, print_line, listen_for_event, get_name_of_breed, get_dog_cids
from scripts.connect_to_pinata import PinataPy
import os
from metadata import metadata_template
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class MetadataCollection:
    def __init__(self, dogTokenURI_cids_filename: str, collection_network: str = network.show_active()):
        """
        Args:
            dogTokenURI_cids_filename (str): Filename that contains all CIDs.
            collection_network (str): Network name of metadata files. Var used in pathway location of files.
        """
        self.dogTokenURI_cids_filename: str = dogTokenURI_cids_filename
        self.collection_network: str = collection_network 
        self.metadata_basedir: str = ""

    def create_collection_metadata(self, overwrite: bool = False):
        print(f"Creating metadata JSON files for *{self.collection_network}* network...")
        (doggie_dict, _) = get_dog_cids(self.dogTokenURI_cids_filename, set_collection_size_limit=True)

        # Check local folder and files
        metadata_basedir: Path = Path(f"./metadata/{self.collection_network}/")
        if Path(metadata_basedir).exists() and not overwrite:
            raise FileExistsError(f"'{metadata_basedir}' already exists, delete it to continue!")
        elif Path(metadata_basedir).exists() and overwrite:
            print(f"'{metadata_basedir}' already exists, wiping folder clean and regenerating data.")
            print(f"Removing: {len(list(metadata_basedir.iterdir()))} files", end=" ")
            [file.unlink() for file in metadata_basedir.iterdir()]
            print("-> All files removed.")
                
        metadata_basedir.mkdir(parents=True, exist_ok=True)
        self.metadata_basedir = metadata_basedir

        for i, doggie in enumerate(doggie_dict.keys(), start=1):
            # num: str = f"0{str(i)}" if i < 10 else f"{str(i)}"
            # metadata_file_name: str = f"{num}_{doggie.split('.')[0]}.json"
            metadata_file_name: str = f"{doggie}.json"
            print(f"Creating Metadata file #{i}: {metadata_file_name}", end="")
            md = metadata_json = metadata_template.template
            image_uri = f"ipfs://{doggie_dict[doggie]}"
            doggie_name = doggie.replace("-", " ").title()
            
            md['name'] = doggie_name
            md['description'] = f"A {doggie_name} dog!"
            md['image'] = image_uri
            md['attributes']['trait_type'] = ["cuteness", "happiness", "anger"][len(doggie_name) % 3]
            md['attributes']['level'] = (len(doggie_name) % 10) + 1

            # Save metadata to JSON file
            with open(f"{metadata_basedir}/{metadata_file_name}", "w") as f:
                json.dump(metadata_json, f, indent=4)
            
            print(" -> Done!")
                
        print("All metadata JSON files saved!")

    def upload_metadata(self, image_pathway: str, collection_name: str, pinata_api_key: str, pinata_api_secret: str):
            # customize
            image_pathway = self.metadata_basedir
            if image_pathway is None or image_pathway == "":
                raise Exception

            PinataUploader = PinataPy(pinata_api_key, pinata_api_secret, collection_name)
            resp_pin_files: ResponsePayload = PinataUploader.pin_file_to_ipfs(
                image_pathway,
                ipfs_destination_path=collection_name, 
                save_absolute_paths=False
            )
            print(f"Result: {resp_pin_files}")

            if resp_pin_files.get('isDuplicate') == False:
                resp_pin_list: ResponsePayload = PinataUploader.pin_list({"status": "pinned", "metadata[name]": collection_name})
                print(f"Pinned List: {resp_pin_list}")

            resp_ipfs_cids: dict = PinataUploader.download_ipfs_file_cids()
            print(f"IPFS File CIDs: {resp_ipfs_cids}")


def main():
    metadata_collection = MetadataCollection(        
        dogTokenURI_cids_filename = os.getenv("CIDS_SUMMARY_FILE"),
        # collection_network = 'rinkeby'
    )
    metadata_collection.create_collection_metadata(overwrite=True)
    metadata_collection.upload_metadata(
        image_pathway = None, 
        collection_name = os.getenv("COLLECTION_NAME") + "_metadata", 
        pinata_api_key = os.getenv("PINATA_API_KEY"),
        pinata_api_secret = os.getenv("PINATA_API_SECRET")
    )
