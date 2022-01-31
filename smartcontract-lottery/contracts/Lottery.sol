// SPDX-License-Identifier: MIT

// pragma solidity ^0.6.6;
// import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";

pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Lottery {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;

    // 0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419

    constructor(address _priceFeed) public {
        usdEntryFee = 50 * (10**18); // converts to wei
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeed);
    }

    function enter() public payable {
        // $50 USD mininum
        // require();
        // players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * (10**10); // convert to 18 decimals
        // int price = ethUsdPriceFeed.getLatestPrice();
        // $50 / $2700 ETH
        // 50 * (10**18) / 2700
        uint256 costToEnter = ((usdEntryFee * (10**18)) / adjustedPrice);
        return costToEnter;
    }

    function startLottery() public {}

    function endLottery() public {}
}
