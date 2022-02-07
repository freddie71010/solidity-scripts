// SPDX-License-Identifier: MIT


pragma solidity ^0.7.0;

import "@chainlink/contracts/src/v0.7/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.7/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyHash;
    address payable public recentWinner;
    uint256 public randomNum;

    // 0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyHash
    ) VRFConsumerBase(_vrfCoordinator, _link) {
        // $50 USD mininum
        usdEntryFee = 50 * (10**18); // converts to wei
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee(), "Not enough ETH!");
        players.push(payable(msg.sender));
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

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't start a new lottery yet!"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        // pseudo random number
        // uint256(
        //     keccak256(
        //         abi.encodePacked(
        //             nonce,               // nonce is predicable (aka transaction number)
        //             msg.sender,          // msg.sender is predictable
        //             block.difficulty,    // can be manipulated by miners
        //             block.timestamp      // timestamp is predictable
        //         )
        //     )
        // ) % players.length;
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        // Random number generated via Chainlink VRF
        bytes32 requestId = requestRandomness(keyHash, fee);
    }

    function fulfillRandomness(bytes32 requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there yet!"
        );
        require(_randomness > 0, "random-not-found");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        // Reset lottery
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomNum = _randomness;
    }
}
