// SPDX-License-Identifier: MIT

pragma solidity ^0.8.17;
contract BoxV3 {
    uint256 private value;
    uint256[] internal s_numArray;

    event ValueChanged(uint256 newValue);
    event ArrayTotalBeforeReset(uint256 total);

    function store(uint256 _newValue) public ArrayMaxFive {
        value = _newValue;
        s_numArray.push(value);
        emit ValueChanged(_newValue);
    }

    function retrieve() public view returns (uint256) {
        return value;
    }

    function increment() public ArrayMaxFive {
        value = value + 1;
        s_numArray.push(value);
        emit ValueChanged(value);
    }

    modifier ArrayMaxFive() {
        _;
        if (s_numArray.length == 5){
            uint256 total = _getArrayTotal();
            emit ArrayTotalBeforeReset(total);
            delete s_numArray;
        }   
    }

    function _getArrayTotal() internal view returns(uint256) {
        uint256 i;
        uint256 sum = 0;
            
        for (i = 0; i < s_numArray.length; i++) {
            sum = sum + s_numArray[i];
        }
        
        return sum;
    }

    function getNumArray() public view returns (uint256[] memory) {
        return s_numArray;
    }

    function emptyNumArray() public {
        uint256 total = _getArrayTotal();
        emit ArrayTotalBeforeReset(total);
        delete s_numArray;
    }

}