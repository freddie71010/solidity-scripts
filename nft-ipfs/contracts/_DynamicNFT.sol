// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract DynamicSvgNft {
    // Mint an NFT based off the price of ETH
    // If ETH > someNumber: smile

    uint256 public s_tokenCounter;
    string public s_lowImageURI;
    string public s_highImageURI;
    AggregatorV3Interface public immutable i_priceFeed;

    constructor(
        address priceFeedAddress,
        string memory lowSvg,
        string memory highSvg
    ) ERC721("Dynamic SVG NFT", "DSN") {
        s_tokenCounter = 0;
        s_lowImageURI = svgToImageURI(lowSvg);
        s_highImageURI = svgToImageURI(highSvg);
        i_priceFeed = AggregatorV3Interface(priceFeedAddress);
        i_highValue = highValue;
    }

    function svgToImageURI(string memory svg)
        public
        pure
        returns (string memory)
    {
        string memory baseImageURL = "data:image/svg+xml;based64,";
        string memory svgBase64Encoded = Base64.encode(
            bytes(string(abi.encodePacked(svg)))
        );
        return string(abi.encodePacked(baseImageURL, svgBase64Encoded));
    }

    function mintNft() external {
        _safeMint(msg.sender, s_tokenCounter);
        s_tokenCounter = s_tokenCounter + 1;
    }

    function _baseURI() internal pure override returns (string memory) {
        return "data:application/json;base64,";
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override
        returns (string memory)
    {
        (, int256 price, , , ) = i_priceFeed.latestRoundData();

        if (price > i_highValue) {
            imageURI = s_highImageURI;
        }

        bytes memory metadataTemplate = abi.encodedPack(
            '{"name": "Dynamic SVG", "description": "A cool NFT", \
         "attributes": [{"trait_type": "coolness", "value": 100}], "image":"',
            imageURI,
            '"}'
        );

        bytes metadataTemplateInBytes = bytes(metadataTemplate);
        string memory encodeMetadata = Base64.encode(metadataTemplateInBytes);
        // Newer version of solidity along string concantenation = string.concat()
        return (string(abi.encodePacked(_baseURI(), encodedMetadata)));
    }
}
