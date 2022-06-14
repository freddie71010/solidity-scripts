"""
Code modified from: https://github.com/Vourhey/pinatapy
"""
import requests
import os
import typing as tp
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

    def __init__(self, pinata_api_key: str, pinata_secret_api_key: str) -> None:
        self._auth_headers: Headers = {
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_secret_api_key,
        }

    @staticmethod
    def _error(response: requests.Response) -> ResponsePayload:
        """Construct dict from response if an error has occurred"""
        return {
            "status": response.status_code,
            "reason": response.reason,
            "text": response.text,
        }

    @staticmethod
    def _validate_destination_folder_name(path: str) -> str:
        """Validates the IPFS destination folder name is valid"""
        path = path.replace(" ", "")
        if not path.endswith("/"):
            path = path + "/"
        return path

    def pin_file_to_ipfs(
        self,
        path_to_file: str,
        ipfs_destination_path: str = "/",
        options: tp.Optional[OptionsDict] = None,
    ) -> ResponsePayload:
        """
        Pin any file, or directory, to Pinata's IPFS nodes
        More: https://docs.pinata.cloud/api-pinning/pin-file
        """
        dest_folder_name = (
            ipfs_destination_path
            if ipfs_destination_path == "/"
            else self._validate_destination_folder_name(ipfs_destination_path)
        )

        url: str = API_ENDPOINT + "pinning/pinFileToIPFS"
        headers: Headers = {
            k: self._auth_headers[k]
            for k in ["pinata_api_key", "pinata_secret_api_key"]
        }

        def get_all_files(directory: str) -> tp.List[str]:
            """get a list of absolute paths to every file located in the directory"""
            paths: tp.List[str] = []
            for root, dirs, files_ in os.walk(os.path.abspath(directory)):
                for file in files_:
                    paths.append(os.path.join(root, file))
            return paths

        files: tp.List[str, tp.Any]

        if os.path.isdir(path_to_file):
            all_files: tp.List[str] = get_all_files(path_to_file)
            files = [("file", (dest_folder_name + file.split("/")[-1], open(file, "rb"))) for file in all_files]
        else:
            files = [("file", (dest_folder_name + path_to_file.split("/")[-1], open(path_to_file, "rb")))]
        for i in files:
            print(i)

        if options is not None:
            if "pinataMetadata" in options:
                headers["pinataMetadata"] = options["pinataMetadata"]
            if "pinataOptions" in options:
                headers["pinataOptions"] = options["pinataOptions"]
        response: requests.Response = requests.post(
            url=url, files=files, headers=headers
        )
        return response.json() if response.ok else self._error(response)  # type: ignore


# IMAGE_FOLDER_PATHWAY = "./images/"
# PinataUploader = PinataPy(os.getenv("PINATA_API_KEY"), os.getenv("PINATA_API_SECRET"))
# resp = PinataUploader.pin_file_to_ipfs(
#     IMAGE_FOLDER_PATHWAY, ipfs_destination_path="doggie-walk-nfts"
# )
# resp2 = PinataUploader.pin_file_to_ipfs(
#     "/home/fvs/solidity-scripts/nft-ipfs/images/shiba-inu.png"
# )
# print(resp2)
