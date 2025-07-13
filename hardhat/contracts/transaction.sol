// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;
/**
 * @title TransactionWallet
 * @dev A simple smart contract for managing user transactions and balance tracking
 */
contract TransactionWallet {
    struct Transaction {
        address from;
        address to;
        uint256 amount;
        uint256 timestamp;
        string message;
    }

    mapping(address => uint256) public balances;
    mapping(address => Transaction[]) public transactions;

    event Deposited(address indexed user, uint256 amount);
    event Sent(address indexed from, address indexed to, uint256 amount, string message);
    event Withdrawn(address indexed user, uint256 amount);

    /**
     * @dev Deposit ETH into the contract.
     */
    function deposit() external payable {
        require(msg.value > 0, "Amount must be greater than zero");

        balances[msg.sender] += msg.value;

        emit Deposited(msg.sender, msg.value);
    }

    /**
     * @dev Send ETH to another address and store transaction history.
     * @param recipient The recipient address.
     * @param amount The amount of ETH to send (in wei).
     * @param message Optional message string.
     */
    function send(address payable recipient, uint256 amount, string calldata message) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        require(recipient != address(0), "Invalid recipient");

        balances[msg.sender] -= amount;
        recipient.transfer(amount);

        transactions[msg.sender].push(Transaction({
            from: msg.sender,
            to: recipient,
            amount: amount,
            timestamp: block.timestamp,
            message: message
        }));

        emit Sent(msg.sender, recipient, amount, message);
    }

    /**
     * @dev Withdraw ETH from the contract to the user's wallet.
     * @param amount The amount to withdraw (in wei).
     */
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        balances[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);

        emit Withdrawn(msg.sender, amount);
    }

    /**
     * @dev Get user's transaction history.
     * @return An array of Transaction structs.
     */
    function getTransactions(address user) external view returns (Transaction[] memory) {
        return transactions[user];
    }

    // fallback/receive to handle direct transfers
    receive() external payable {
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }
}
