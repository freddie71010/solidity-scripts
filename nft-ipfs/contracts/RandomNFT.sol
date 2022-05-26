// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink-brownie-contracts/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink-brownie-contracts/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

error RangeOutOfBounds();
error AlreadyInitialized();

contract DoggieWalkNFTs is ERC721URIStorage, VRFConsumerBaseV2 {
    using Counters for Counters.Counter;
    
    // Dog Types
    enum Breed {
        PUG,
        SHIBA_INU,
        ST_BERNARD
    }
    
    // Chainlink VRF Variables
    VRFCoordinatorV2Interface private immutable i_vrfCoordinator;
    bytes32 private immutable i_gasLane;
    uint32 private immutable i_subscriptionId;
    uint32 private immutable i_callbackGasLimit;
    uint16 private constant REQUEST_CONFIRMATIONS = 3;
    uint32 private constant NUM_WORDS = 2;

    // NFT Variables
    Counters.Counter public tokenIdCounter;
    uint256 constant MAX_CHANCE_VALUE = 100;
    string[3] internal s_dogTokenURIs;
    bool private s_initialized;

    // VRF Helpers
    mapping(uint256 => address) s_requestIdToSender;
    
    // Events
    event NftRequested(uint256 indexed requestId, address requester);
    event NftMinted(Breed breed, address minter);
    
    constructor(
        address _vrfCoordinatorV2,
        bytes32 _gasLane,
        uint32 _subscriptionId,
        uint32 _callbackGasLimit,
        string[3] memory dogTokenURIs
    ) ERC721("Doggie Walk", "DW") VRFConsumerBaseV2(_vrfCoordinatorV2) {
        i_vrfCoordinator = VRFCoordinatorV2Interface(_vrfCoordinatorV2);
        i_gasLane = _gasLane;
        i_subscriptionId = _subscriptionId;
        i_callbackGasLimit = _callbackGasLimit;
        _initializeContract(dogTokenURIs);
    }

    function requestDoggie() public returns (uint256 requestId) {
        requestId = i_vrfCoordinator.requestRandomWords(
            i_gasLane, // price per gas
            i_subscriptionId,
            REQUEST_CONFIRMATIONS,
            i_callbackGasLimit, // max gas amount
            NUM_WORDS
        );
        s_requestIdToSender[requestId] = msg.sender;
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
        emit NftMinted(breed, dogOwner);

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

    // getter functions
    function getDogTokenUris(uint256 index) public view returns (string memory) {
        return s_dogTokenURIs[index];
    }

    function getTokenCounter() public view returns (uint256) {
        return tokenIdCounter.current();
    }


}
