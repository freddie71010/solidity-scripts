# solidity-scripts

A collection of miscellaneous solidity projects.

### *Reminder:*
Be sure to check out the branches of this repo (besides the 'main' branch) for additional WIP projects.


## Projects:
### Mint a Random NFT from a Collection! (Folder: [nft-ipfs](https://github.com/freddie71010/solidity-scripts/edit/main/nft-ipfs/))
An ERC721 NFT project written in solidity and deployed using brownie (python). A user can mint a random Doggie NFT (where the randomness factor is provided by Chainlink's VRF) from a newly created Doggie NFT Collection consisting of several unique NFTs. The minting rarity of each Doggie is based on a Chance Array that the owner of the deployed smart contract can modify if they so desired using the setChanceArray() function of the contract.

### ERC-20 Token Staking DApp (Folder: [staking-ui](https://github.com/freddie71010/solidity-scripts/edit/main/staking-ui/))
#### DApp Features:
- Stake $RT tokens into contract
  - Once staked, these $RT tokens will automatically earn interest over time
- Withdraw $RT Tokens back into wallet with interest
- Connect to dapp using Moralis's Connect Wallet feature

### Smart Contract Lottery (Folder: [smartcontract-lottery](https://github.com/freddie71010/solidity-scripts/edit/main/smartcontract-lottery/))
1. Users can enter a lottery with ETH by paying a $50 USD equivalent fee.
2. An admin will choose when the lottery is over.
3. The lottery will select a random winner from those who entered and send them all the ETH! This random winner is determined by calling a ChainLink node to determine true randomness.

