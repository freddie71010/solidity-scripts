import json
import os
from pathlib import Path

from brownie import Contract, DoggieWalkNFT, config, network
from dotenv import load_dotenv
from metadata import metadata_template

from scripts.utils import read_cid_summary_file, upload_files_to_ipfs

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
        (doggie_dict, _) = read_cid_summary_file(self.dogTokenURI_cids_filename, set_collection_size_limit=True)

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
        self.metadata_basedir = metadata_basedir  # Set base directory path

        for i, doggie in enumerate(doggie_dict.keys(), start=1):
            # num: str = f"0{str(i)}" if i < 10 else f"{str(i)}"
            # metadata_file_name: str = f"{num}_{doggie.split('.')[0]}.json"
            metadata_file_name: str = f"{doggie}.json"
            print(f"Creating Metadata file #{i}: {metadata_file_name}", end="")
            md = metadata_json = metadata_template.template
            image_uri = f"ipfs://{doggie_dict[doggie]['Hash']}"
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

    def upload_metadata(self, **kwargs) -> None:
        """ Pass-through function to upload_files_to_ipfs() """
        upload_files_to_ipfs(**kwargs)


def main():
    metadata_collection = MetadataCollection(        
        dogTokenURI_cids_filename = os.getenv("CIDS_IMAGES_FILE"),
        # collection_network = 'rinkeby'
    )
    metadata_collection.create_collection_metadata(overwrite=True)
    metadata_collection.upload_metadata(
        folder_pathway = str(metadata_collection.metadata_basedir), 
        collection_name = os.getenv("COLLECTION_NAME") + "_metadata", 
        pinata_api_key = os.getenv("PINATA_API_KEY"),
        pinata_api_secret = os.getenv("PINATA_API_SECRET")
    )
