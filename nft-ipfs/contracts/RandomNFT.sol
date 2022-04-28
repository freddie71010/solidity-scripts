pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract RandomIpfsNft is ERC721URIStorage, VRFConsumerBaseV2 {
    VRFCoordinatorV2Interface immutable i_vrfCoordinator;
    bytes immutable i_gasLane;
    bytes immutable i_subscriptionId;
    uint32 immutable i_callbackGasLimit;

    uint16 constant REQUEST_CONFIRMATIONS = 3;
    uint32 constant NUM_WORDS = 2;
    uint32 constant MAX_CHANCE_VALUE = 99;

    mapping(uint256 => address) s_requestIdToSender;

    constructor(
        address vrfCoordinatorV2,
        bytes32 gasLane,
        bytes32 s_subscriptionId,
        uint16 s_requestConfirmations,
        uint32 s_callbackGasLimit,
        uint32 numWords
    ) ERC721("Doggie Walk", "DW") {
        i_vrfCoordinator = VRFCoordinatorV2Interface(vrfCoordinatorV2);
        i_gasLane = gasLane;
        i_subscriptionId = s_subscriptionId;
        REQUEST_CONFIRMATIONS = s_requestConfirmations;
        i_callbackGasLimit = s_callbackGasLimit;
        NUM_WORDS = numWords;
    }

    function requestDoggie() public returns (uint256 requestId) {
        requestId = i_vrfCoordinator.requestRandomWords(
            i_gasLane, // price per gas
            i_subscriptionId,
            REQUEST_CONFIRMATIONS,
            i_callbackGasLimit, // max gas amount
            NUM_WORDS
        );
    }

    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords)
        internal
        override
    {
        // owner of the dog
        address dogOwner = s_requestIdToSender[requestId];
        // assign the NFT a tokenId
        uint256 newTokenId = s_tokenCounter;
        s_tokenCounter = s_tokenCounter + 1;

        _safeMint(dogOwner, newTokenId);
    }

    function getChanceArray() public pure returns (uint256[3] memory) {}

    function getBreedFromModdedRng(uint256 moddedRng) {
        uint256 cumulativeSum = 0;
        uint256[3] memory chanceArray = getChanceArray();
    }
}
