<br/>
<p align="center">
<img src="https://raw.githubusercontent.com/freddie71010/solidity-scripts/main/images/pug.png" width="200" alt="NFT Pug">
<img src="https://raw.githubusercontent.com/freddie71010/solidity-scripts/main/images/st-bernard.png" width="200" alt="NFT St.Bernard">
<img src="https://raw.githubusercontent.com/freddie71010/solidity-scripts/main/images/shiba-inu.png" width="200" alt="NFT Shiba Inu">
<img src="https://raw.githubusercontent.com/freddie71010/solidity-scripts/main/images/shiba-inu-hat.png" width="200" alt="NFT Shiba Inu Hat">
</p>
<br/>

# Create an NFT collection!
An ERC721 NFT project written in solidity and deployed using brownie (python). A user can mint a truly random Doggie NFT (a truly random number is provided by Chainlink's VRF which is then used with the rarity of each Doggie of appearing). The owner of the smart contract can modify the Minting Rarity numbers (using the *setChanceArray()* function on the contract).

## Doggie Minting Rarity
- Pug = 30%
- St Bernard = 20%
- Shiba Inu = 45%
- Shiba Inu Hat = 5%

# Prerequistes
- Ensure `images/` folder contains 4 Doggie image files.
- Fill out `.env` file with necessary environment variables.
# There are four steps that need to be followed in order:
- `s01_upload_nft_images.py` - Uploads all images in 'images/' folder to IPFS via Pinata Cloud and downloads a CID Summary JSON file of results.
- `s02_upload_nft_metadata.py` - Creates metadata JSON files based on uploaded image CIDs and then uploads all metadata files to IPFS via Pinata Cloud. Also downloads a CID Summary JSON file of results.
- `s03_deploy_nft_collection.py` - Deploys "Doggie Walk" NFT Collection to the desired network.
- `s04_mint_doggie_nft.py` - Interacts with the deployed NFT contract and mints X number of NFTs.
    - You can deploy the contract AND mint NFTs all in one go from this script.