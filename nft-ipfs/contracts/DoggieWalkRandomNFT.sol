// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink-brownie-contracts/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink-brownie-contracts/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

error RangeOutOfBounds();
error AlreadyInitialized();
error NeedMoreETHSent();    

contract DoggieWalkNFT is ERC721URIStorage, VRFConsumerBaseV2, Ownable {
    using Counters for Counters.Counter;
    
    // Dog Types
    enum Breed {
        PUG,
        SHIBA_INU,
        ST_BERNARD
    }
    
    // Chainlink VRF Variables
    VRFCoordinatorV2Interface private immutable i_vrfCoordinator;
    // TODO: Privatize variable
    bytes32 public immutable i_gasLane;
    uint32 public immutable i_subscriptionId;
    uint32 public immutable i_callbackGasLimit;
    uint16 private constant REQUEST_CONFIRMATIONS = 3;
    uint32 private constant NUM_WORDS = 2;

    // NFT Variables
    Counters.Counter public tokenIdCounter;
    uint256 public s_mintFee = 0.01 ether;
    uint256 constant MAX_CHANCE_VALUE = 100;
    string[3] internal s_dogTokenURIs;
    bool private s_initialized;

    // VRF Helpers
    mapping(uint256 => address) public s_requestIdToSender;
    
    // Events
    event NftRequested(uint256 indexed requestId, address requester);
    event NftMinted(address minter, uint256 tokenId, Breed breed);

    constructor(
        address _vrfCoordinatorV2,
        bytes32 _gasLane,   // keyhash
        uint32 _callbackGasLimit,
        uint32 _subscriptionId,
        string[3] memory dogTokenURIs
    ) ERC721("Doggie Walk", "DW") VRFConsumerBaseV2(_vrfCoordinatorV2) {
        i_vrfCoordinator = VRFCoordinatorV2Interface(_vrfCoordinatorV2);
        i_gasLane = _gasLane;
        i_callbackGasLimit = _callbackGasLimit;
        i_subscriptionId = _subscriptionId;
        _initializeContract(dogTokenURIs);
    }

    function requestDoggie() public payable returns (uint256 requestId) {
        // if (msg.value <= s_mintFee) {
        //     revert NeedMoreETHSent();
        // }
        requestId = i_vrfCoordinator.requestRandomWords(
            i_gasLane, // price per gas
            i_subscriptionId,
            REQUEST_CONFIRMATIONS,
            i_callbackGasLimit, // max gas amount
            NUM_WORDS
        );
        s_requestIdToSender[requestId] = msg.sender;
        emit NftRequested(requestId, msg.sender);
    }

    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords) internal override {
        // owner of the dog
        address dogOwner = s_requestIdToSender[requestId];
        // assign the NFT a tokenId
        uint256 newTokenId = tokenIdCounter.current();
        tokenIdCounter.increment();
        uint256 moddedRng = randomWords[0] % 100;
        Breed breed = getBreedFromModdedRng(moddedRng);
        _safeMint(dogOwner, newTokenId);
        // set the tokenURI of Dog
        _setTokenURI(newTokenId, s_dogTokenURIs[uint256(breed)]);
        emit NftMinted(dogOwner, newTokenId, breed);
    }

    function getChanceArray() public pure returns (uint256[3] memory) {
        // 0 - 9 = st bernard
        // 10 - 59 = pug
        // 30 - 99 = shiba inu
        return [10, 30, MAX_CHANCE_VALUE];
    }

    function getBreedFromModdedRng(uint256 moddedRng) public pure returns(Breed) {
        uint256 cumulativeSum = 0;
        uint256[3] memory chanceArray = getChanceArray();
        for (uint256 i=0; i < chanceArray.length; i++) {
            if (moddedRng >= cumulativeSum && moddedRng < cumulativeSum + chanceArray[i]) {
                // 0 = st bernard
                // 1 = pug
                // 2 = shiba inu
                return Breed(i);
            }
            cumulativeSum = cumulativeSum + chanceArray[i];
        }
        revert RangeOutOfBounds();
    }

    function _initializeContract(string[3] memory dogTokenUris) private {
        if (s_initialized) {
            revert AlreadyInitialized();
        }
        s_dogTokenURIs = dogTokenUris;
        s_initialized = true;
    }

    // withdraw
    function withdraw() public onlyOwner {
        uint256 amount = address(this).balance;
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    // getter functions
    function getDogTokenUris(uint256 index) public view returns (string memory) {
        return s_dogTokenURIs[index];
    }

    function getTokenCounter() public view returns (uint256) {
        return tokenIdCounter.current();
    }

    function getMintFee() public view returns (uint256) {
        return s_mintFee;
    }

    // setter functions
    function _setMintFee(uint256 _newFee) public onlyOwner {
        s_mintFee = _newFee;
    }

}
