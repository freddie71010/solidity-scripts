"""
Code modified from: https://github.com/Vourhey/pinatapy
"""
from unicodedata import name
import requests
import os
import json
import typing as tp
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Custom type hints
ResponsePayload = tp.Dict[str, tp.Any]
OptionsDict = tp.Dict[str, tp.Any]
Headers = tp.Dict[str, str]

# global constants
API_ENDPOINT: str = "https://api.pinata.cloud/"


class PinataPy:
    """A pinata api client session object"""

    def __init__(self, 
        pinata_api_key: str,
        pinata_secret_api_key: str, 
        collection_name: str = "main-collection", 
        ipfs_hash: str = None
    ) -> None:
        self._auth_headers: Headers = {
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_secret_api_key,
        }
        
        if collection_name is None or "" or len(collection_name) < 1:
            raise ValueError
        self.collection_name: str = collection_name
        self.ipfs_files: dict = {}
        self.ipfs_local_filename: dict = f"{collection_name}_CIDs.json"
        self.ipfs_hash: str = ipfs_hash
        self.existing_ipfs_hash_bool: bool = True if ipfs_hash else False

        if self.existing_ipfs_hash_bool:
            print(f"Pulling data on existing collection CID: {self.ipfs_hash}...")
        else:
            print(f"Creating a collection called '{self.collection_name}'...")


    @staticmethod
    def _error(response: requests.Response) -> ResponsePayload:
        """Construct dict from response if an error has occurred"""
        return {"status": response.status_code, "reason": response.reason, "text": response.text}

    @staticmethod
    def _validate_destination_folder_name(path: str) -> str:
        """
        Validates the IPFS destination folder name is valid by removing
        blankspaces and adding '/' to the end of the path
        """
        path = path.replace(" ", "")
        if not path.endswith("/"):
            path = path + "/"
        return path

    def pin_file_to_ipfs(
            self,
            path_to_file: str,
            ipfs_destination_path: str = "/",
            save_absolute_paths: bool = True,
            options: tp.Optional[OptionsDict] = None,
    ) -> ResponsePayload:
        """
        Pin any file, or directory, to Pinata's IPFS nodes
        Args:
            path_to_file: local path of file/directory to upload to IPFS node
            ipfs_destination_path: destination path of file(s) on the IPFS node. 
                You can only set one destination path per call. 
                Pathway can be viewed in the Pinata Cloud Pin Manager (https://app.pinata.cloud/pinmanager).
                Ex: input => destination path
                    '' => /
                    'animal-nfts/' => /animal-nfts/
                    'retro-nfts/animals' => /retro-nfts/animals/
            save_absolute_paths: parameter to control filepaths cutting.
                Ex: input => destination path
                    true: /dir1/dir2/dir3/filename => /dir1/dir2/dir3/filename
                    false: /dir1/dir2/dir3/filename => filename
            options: optional parameters (pinataMetadata, pinataOptions)
        Returns:
            JSON response
        More: https://docs.pinata.cloud/pinata-api/pinning/pin-file-or-directory
        """
        url: str = API_ENDPOINT + "pinning/pinFileToIPFS"
        headers: Headers = {k: self._auth_headers[k] for k in ["pinata_api_key", "pinata_secret_api_key"]}
        dest_folder_name = (
            ipfs_destination_path
            if ipfs_destination_path == "/"
            else self._validate_destination_folder_name(ipfs_destination_path)
        )
        def get_all_files(directory: str) -> tp.List[str]:
            """get a list of absolute paths to every file located in the directory"""
            paths: tp.List[str] = []
            for root, dirs, files_ in os.walk(os.path.abspath(directory)):
                for file in files_:
                    paths.append(os.path.join(root, file))
            return paths

        def get_mutated_filepath(filepath: str, dest_folder_name: str, save_absolute_paths: bool):
            """transform filepath with dest_folder_name and absolute path saving rules"""
            if save_absolute_paths:
                return dest_folder_name + (filepath[:1].replace("/", "") + filepath[1:])  # remove first '/' if exists
            else:
                return dest_folder_name + filepath.split("/")[-1]

        files: tp.List[str, tp.Any]

        # If path_to_file is a directory
        if os.path.isdir(path_to_file):
            all_files: tp.List[str] = get_all_files(path_to_file)
            files = [("file", (get_mutated_filepath(file, dest_folder_name, save_absolute_paths), open(file, "rb"))) for
                     file in all_files]  # type: ignore
        # If path_to_file is a single file
        else:
            files = [("file", (get_mutated_filepath(path_to_file, dest_folder_name, save_absolute_paths),
                               open(path_to_file, "rb")))]  # type: ignore

        if options is not None:
            if "pinataMetadata" in options:
                headers["pinataMetadata"] = options["pinataMetadata"]
            if "pinataOptions" in options:
                headers["pinataOptions"] = options["pinataOptions"]
        response: requests.Response = requests.post(url=url, files=files, headers=headers)
        if response.ok:
            if response.json().get('isDuplicate') == True:
                print("WARNING: Uploaded files already exist on IPFS! Double check Pinata Cloud for correct collection name.")
                self.existing_ipfs_hash_bool = True
            else:
                print(f"INFO: Saved new data to IPFS Hash: {response.json()['IpfsHash']}")
                self.existing_ipfs_hash_bool = False
            
            self.ipfs_hash = response.json()['IpfsHash']
            
        return response.json() if response.ok else self._error(response)  # type: ignore


    def pin_list(self, options: tp.Optional[OptionsDict] = None) -> ResponsePayload:
        """ Returns list of your IPFS files based on certain filters.

        Ex: Filter by only 'pinned' files
            options = ({"status": "pinned"})
        Ex: Filter by 'pinned' files and files that contain a metadata 'name' of 'dogs-nfts'
            options = ({"status": "pinned", "metadata[name]": "dogs-nfts"})
        
        More: https://docs.pinata.cloud/pinata-api/data/query-files
        """
        url: str = API_ENDPOINT + "data/pinList"
        payload: OptionsDict = options if options else {}
        response: requests.Response = requests.get(url=url, params=payload, headers=self._auth_headers)
        return response.json() if response.ok else self._error(response)  # type: ignore

    def remove_pin_from_ipfs(self, hash_to_remove: str) -> ResponsePayload:
        """ Removes specified hash pin

        More: https://docs.pinata.cloud/pinata-api/pinning/remove-files-unpin
        """
        url: str = API_ENDPOINT + f"pinning/unpin/{hash_to_remove}"
        headers: Headers = self._auth_headers
        headers["Content-Type"] = "application/json"
        response: requests.Response = requests.delete(url=url, data={}, headers=headers)
        return self._error(response) if not response.ok else {"message": "Removed"}
    
    def pin_json_to_ipfs(self, json_to_pin: tp.Any, options: tp.Optional[OptionsDict] = None) -> ResponsePayload:
        """ pin provided JSON
        
        More: https://docs.pinata.cloud/pinata-api/pinning/pin-json
        """
        url: str = API_ENDPOINT + "pinning/pinJSONToIPFS"
        headers: Headers = self._auth_headers
        headers["Content-Type"] = "application/json"
        payload: ResponsePayload = {"pinataContent": json_to_pin}
        if options is not None:
            if "pinataMetadata" in options:
                payload["pinataMetadata"] = options["pinataMetadata"]
            if "pinataOptions" in options:
                payload["pinataOptions"] = options["pinataOptions"]
        response: requests.Response = requests.post(url=url, json=payload, headers=headers)
        return response.json() if response.ok else self._error(response)  # type: ignore
    
    def download_ipfs_file_cids(self, ipfs_hash: str = None) -> dict:
        """ 
        
        Scans the inputted IPFS hash for nested folders/files to identify all 
        the associated CIDs in that nested structure and create output JSON file
        with associated details.

        Returns: Dictionary of all File names to their corresponding Hash/CID
        """
        url: str = 'https://dweb.link/api/v0/ls'
        ipfs_hash_arg = ipfs_hash if ipfs_hash else self.ipfs_hash
        params: dict = {'arg': ipfs_hash_arg}
        print("Downloading IPFS file data...")
        try:
            response: requests.Response = requests.get(url=url, params=params)
        except Exception as e:
            print(e)
        time.sleep(2)
        if response.ok:
            resp_ipfs_files = response.json()['Objects'][0]['Links'] if response.ok else self._error(
                response)  # type: ignore
            # TODO: If output files exists, clear the contents before writing to it.
            
            for file in resp_ipfs_files:
                dir: bool = True if file['Size'] == 0 else False  # checks to see if file is a Directory
                
                d: dict = self.ipfs_files
                name: str = file['Name'].split(".")[0]
                d[name]: dict = file
                d[name]["FileType"]: str = 'dir' if file['Size'] == 0 else file['Name'].split(".")[-1]
                if dir:
                    self.download_ipfs_file_cids(d[name]['Hash'])
            
            # Save metadata to JSON file
            cid_pathway: Path = Path(f"./ipfs_cids_summary/")
            cid_pathway.mkdir(parents=True, exist_ok=True)
            with open(f"{cid_pathway}/{self.ipfs_local_filename}", "w") as f:
                json.dump(self.ipfs_files, f, indent=4)
            
            self._print_ipfs_details()
            print(f"Download complete! IPFS file data saved to: '{cid_pathway}/{self.ipfs_local_filename}'")
            return self.ipfs_files
        else:
            return self._error(response)
    
    def _print_ipfs_details(self) -> None:
        """ Prints a summary of the IPFS File details """
        print("FILE CIDS", "="*50)
        length: int = 30
        for k,v in self.ipfs_files.items():
            if v['FileType'] == "dir":
                continue
            filename: str = k
            print(f"{filename}{(length-len(filename))*' '}: {v['Hash']}")
