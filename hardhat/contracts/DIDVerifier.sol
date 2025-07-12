// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Verifier.sol";

contract DIDVerifier is Verifier {
    event DIDLinked(string did, address wallet, bytes32 aadhaarHash);

    mapping(string => bytes32) public didToAadhaar;
    mapping(address => string) public walletToDID;

    function verifyAndLink(
        uint256[2] memory a,
        uint256[2][2] memory b,
        uint256[2] memory c,
        uint256[] memory input,
        string memory did,
        address wallet
    ) public returns (bool) {
        require(verifyProof(a, b, c, input), "Invalid proof");

        bytes32 aadhaarHash = bytes32(input[0]);
        didToAadhaar[did] = aadhaarHash;
        walletToDID[wallet] = did;

        emit DIDLinked(did, wallet, aadhaarHash);
        return true;
    }
} 