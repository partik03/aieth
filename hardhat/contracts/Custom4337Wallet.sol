// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

/**
 * Custom ERC-4337 Smart Account Wallet
 * - Works with ERC-4337 EntryPoint
 * - Customizable validateUserOp logic
 * - Supports execute(), batchExecute()
 */

import "@account-abstraction/contracts/interfaces/IAccount.sol";
import "@account-abstraction/contracts/interfaces/IEntryPoint.sol";
import "@account-abstraction/contracts/interfaces/PackedUserOperation.sol";
import "@account-abstraction/contracts/core/Helpers.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "@openzeppelin/contracts/utils/Address.sol";

contract Custom4337Wallet is IAccount {
    using ECDSA for bytes32;
    using Address for address;

    IEntryPoint public immutable entryPoint;
    address public owner;
    uint256 public nonce;

    event Executed(address target, uint256 value, bytes data);
    event BatchExecuted(uint256 calls);

    modifier onlyEntryPoint() {
        require(msg.sender == address(entryPoint), "Not EntryPoint");
        _;
    }

    constructor(address _entryPoint, address _owner) {
        entryPoint = IEntryPoint(_entryPoint);
        owner = _owner;
    }

    receive() external payable {}

    function validateUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 /*missingAccountFunds*/
    ) external override returns (uint256 validationData) {
        bytes32 hash = MessageHashUtils.toEthSignedMessageHash(userOpHash);
        address recovered = hash.recover(userOp.signature);
        require(recovered == owner, "Invalid signature");
        return 0; // valid
    }

    function execute(address dest, uint256 value, bytes calldata func) external onlyEntryPoint {
        (bool success, ) = dest.call{value: value}(func);
        require(success, "Call failed");
        emit Executed(dest, value, func);
    }

    function executeBatch(address[] calldata dests, bytes[] calldata funcs) external onlyEntryPoint {
        require(dests.length == funcs.length, "Length mismatch");
        for (uint256 i = 0; i < dests.length; i++) {
            (bool success, ) = dests[i].call(funcs[i]);
            require(success, "Call failed");
        }
        emit BatchExecuted(dests.length);
    }

    function getNonce() external view returns (uint256) {
        return nonce;
    }

    function incrementNonce() external onlyEntryPoint {
        nonce++;
    }

    function getOwner() external view returns (address) {
        return owner;
    }

    function updateOwner(address newOwner) external {
        require(msg.sender == owner, "Not owner");
        owner = newOwner;
    }
} 