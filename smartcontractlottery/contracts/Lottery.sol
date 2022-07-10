// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";




contract Lottery is VRFConsumerBase, Ownable{
    address payable[] public players;
    address payable public recentWinner;
    uint public randomness;
    uint public usdEntryFee;

    AggregatorV3Interface internal ethUsdPricefeed;
    event requestedRandomness(bytes32 requestId);
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE public lottery_state;
    uint public fee;
    bytes32 public keyhash;

    constructor(address _pricefeed, address _vrfCoordinator, address _link, uint _fee, bytes32 _keyhash) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10**18);
        ethUsdPricefeed = AggregatorV3Interface(_pricefeed);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        _keyhash = keyhash;
    } 

    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee(), 'not enough ETH');
        players.push(msg.sender);

    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPricefeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10; // 18 decimals
        // $50, $2,000 / ETH
        // 50/2,000
        // 50 * 100000 / 2000
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSED, "cant start a new lottery yet");
        lottery_state = LOTTERY_STATE.OPEN;

    }

    function endLottery() public {

        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee);
        emit requestedRandomness(requestId);

    }

    function fulfillRandomness(bytes32 _requestId, uint _randomness) internal override {
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "you are not there yet");
        require(_randomness > 0, "randomness not found ");
        uint indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;

    }
}