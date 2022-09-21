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
        ST_BERNARD,
        SHIBA_INU_HAT
    }
    
    // Chainlink VRF Variables
    VRFCoordinatorV2Interface private immutable i_vrfCoordinator;
    bytes32 private immutable i_gasLane;
    uint32 private immutable i_subscriptionId;
    uint32 private immutable i_callbackGasLimit;
    uint16 private constant REQUEST_CONFIRMATIONS = 3;
    uint32 private constant NUM_WORDS = 2;

    // NFT Variables
    Counters.Counter internal tokenIdCounter;
    uint256 internal s_mintFee = 0.01 ether;
    string[4] internal s_dogTokenURIs;
    bool private s_initialized;
    // Default chance array based on dog order of 'Breed' enum
    uint8[4] internal s_chanceArray = [10, 30, 95, 100];

    // VRF Helpers
    mapping(uint256 => address) public s_requestIdToSender;
    
    // Events
    event NftRequested(uint256 indexed requestId, address requester);
    event NftMinted(address minter, uint256 tokenId, Breed breed);
    event MintFeeChanged(uint256 oldFee, uint256 newFee);
    event ChanceArrayChanged(uint8[4] oldChanceArray, uint8[4] newChanceArray);

    constructor(
        address _vrfCoordinatorV2,
        bytes32 _gasLane,   // keyhash
        uint32 _callbackGasLimit,
        uint32 _subscriptionId,
        string[4] memory dogTokenURIs
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
        uint256 moddedRng = randomWords[0] % s_chanceArray[s_chanceArray.length-1];
        Breed breed = getBreedFromModdedRng(moddedRng);
        _safeMint(dogOwner, newTokenId);
        // set the tokenURI of Dog
        _setTokenURI(newTokenId, s_dogTokenURIs[uint256(breed)]);
        emit NftMinted(dogOwner, newTokenId, breed);
    }

    function getBreedFromModdedRng(uint256 moddedRng) public view returns(Breed) {
        for (uint256 i=0; i < s_chanceArray.length; i++) {
            if (moddedRng < s_chanceArray[i]) {
                return Breed(i);
            }
        }
        revert RangeOutOfBounds();
    }

    function _initializeContract(string[4] memory dogTokenUris) private {
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
    function getAllDogTokenUris() external view returns (string[4] memory) {
        return s_dogTokenURIs;
    }

    function getTokenCounter() external view returns (uint256) {
        return tokenIdCounter.current();
    }

    function getChanceArray() public view returns (uint8[4] memory) {
        return s_chanceArray;
    }

    function getMintFee() external view returns (uint256) {
        return s_mintFee;
    }

    // setter functions
    function setMintFee(uint256 _newFee) public onlyOwner {
        require(_newFee > 0, "new mint fee must be > 0");
        require(_newFee != s_mintFee, "new mint fee must be different than the previous mint fee");
        uint256 oldFee = s_mintFee; 
        s_mintFee = _newFee;
        emit MintFeeChanged(oldFee, _newFee);
    }

    function setChanceArray(uint8[4] memory _newChanceArray) public onlyOwner {
        uint8[4] memory oldChanceArray = getChanceArray();
        s_chanceArray = _newChanceArray;
        emit ChanceArrayChanged(oldChanceArray, _newChanceArray);
    }

    function setToOriginalChanceArray() public onlyOwner {
        uint8[4] memory oldChanceArray = getChanceArray();
        s_chanceArray = [10, 30, 95, 100];
        emit ChanceArrayChanged(oldChanceArray, s_chanceArray);
    }

}
