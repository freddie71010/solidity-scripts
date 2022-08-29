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

    def create_collection_metadata(self):
        print("Creating metadata JSON files...")
        (doggie_dict, _) = get_dog_cids(self.dogTokenURI_cids_filename, limit_collection=True)

        metadata_file_pathway: Path = Path(f"./metadata/{self.collection_network}/")
        metadata_file_pathway.mkdir(parents=True, exist_ok=True)

        for i, doggie in enumerate(doggie_dict.keys(),start=1):
            num: str = f"0{str(i)}" if i < 10 else f"{str(i)}"
            metadata_file_name: str = f"{num}_{doggie.split('.')[0]}.json"
            
            if Path(str(metadata_file_pathway) + "/" + metadata_file_name).exists():
                raise FileExistsError(f"{metadata_file_name} already found, delete it to overwrite!")
            else:
                print(f"Creating Metadata file: {metadata_file_name}", end="")
                md = metadata_json = metadata_template.template

                ipfs_img_hash = doggie_dict[doggie]
                image_uri = f"ipfs://{ipfs_img_hash}"
                doggie_name = doggie.split(".")[0].replace("-", " ").title()
                
                md['name'] = doggie_name
                md['description'] = f"A {doggie_name} dog!"
                md['image'] = image_uri
                md['attributes']['trait_type'] = ["cuteness", "happiness", "anger"][len(doggie_name) % 3]
                md['attributes']['level'] = (len(doggie_name) % 10) + 1

                # Save metadata to JSON file
                with open(f"{metadata_file_pathway}/{metadata_file_name}", "w") as f:
                    json.dump(metadata_json, f)
                
                print(" -> Done!")
                
        print("All metadata JSON files saved!")

    def upload_metadata(self):
        # check 
        ...



def main():
    metadata_collection = MetadataCollection(        
        dogTokenURI_cids_filename = os.getenv("CIDS_TXT_FILENAME"),
        # collection_network = 'rinkeby'
    )
    metadata_collection.create_collection_metadata()
    metadata_collection.upload_metadata()

if __name__ == "__main__":
    main()
