// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Verifier.sol";

contract DIDVerifier is Verifier {
    event DIDLinked(string did, address wallet, bytes32 aadhaarHash);
    event AadhaarVerified(address user, bytes32 aadhaarHash, bool verified);

    mapping(string => bytes32) public didToAadhaar;
    mapping(address => string) public walletToDID;
    mapping(bytes32 => bool) public verifiedAadhaarHashes;
    mapping(address => bytes32) public userToAadhaarHash;

    // Admin can pre-approve Aadhaar hash commitments
    mapping(bytes32 => bool) public approvedHashCommitments;
    address public admin;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    constructor(address _admin) {
        admin = _admin;
    }

    // Pre-approve Aadhaar hash commitments (off-chain verification)
    function approveHashCommitment(bytes32 hashCommitment) external onlyAdmin {
        approvedHashCommitments[hashCommitment] = true;
    }

    // Verify Aadhaar proof and link to user
    function verifyAadhaarAndLink(
        uint256[2] memory a,
        uint256[2][2] memory b,
        uint256[2] memory c,
        uint256 otpVerified,
        uint256 hashCommitment,
        address user
    ) public returns (bool) {
        // Verify the zkProof
        require(verifyAadhaarProof(a, b, c, otpVerified, hashCommitment), "Invalid proof");
        
        // Check if hash commitment is pre-approved
        require(approvedHashCommitments[bytes32(hashCommitment)], "Hash not pre-approved");
        
        // Check if OTP was verified
        require(otpVerified == 1, "OTP not verified");
        
        // Link user to Aadhaar hash
        userToAadhaarHash[user] = bytes32(hashCommitment);
        verifiedAadhaarHashes[bytes32(hashCommitment)] = true;
        
        emit AadhaarVerified(user, bytes32(hashCommitment), true);
        
        return true;
    }

    // Link DID with wallet (requires Aadhaar verification)
    function verifyAndLink(
        uint256[2] memory a,
        uint256[2][2] memory b,
        uint256[2] memory c,
        uint256[] memory input,
        string memory did,
        address wallet
    ) public returns (bool) {
        require(verifyProof(a, b, c, input), "Invalid proof");

        bytes32 aadhaarHash = bytes32(input[1]); // hash_commitment is second input
        
        // Ensure user has verified Aadhaar
        require(verifiedAadhaarHashes[aadhaarHash], "Aadhaar not verified");
        
        didToAadhaar[did] = aadhaarHash;
        walletToDID[wallet] = did;

        emit DIDLinked(did, wallet, aadhaarHash);
        return true;
    }

    // Check if user has verified Aadhaar
    function isAadhaarVerified(address user) public view returns (bool) {
        bytes32 aadhaarHash = userToAadhaarHash[user];
        return verifiedAadhaarHashes[aadhaarHash];
    }

    // Get Aadhaar hash for user
    function getAadhaarHash(address user) public view returns (bytes32) {
        return userToAadhaarHash[user];
    }

    // Update admin
    function updateAdmin(address newAdmin) external onlyAdmin {
        admin = newAdmin;
    }
} 