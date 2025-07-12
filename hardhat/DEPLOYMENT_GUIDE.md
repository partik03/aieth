# 🚀 Sepolia Deployment Guide

## 📋 Prerequisites

1. **Node.js and npm** installed
2. **Sepolia ETH** for gas fees (get from [Sepolia Faucet](https://sepoliafaucet.com/))
3. **Infura/Alchemy** account for RPC endpoint
4. **Etherscan** account for contract verification

## 🔧 Environment Setup

Create a `.env` file in your project root with the following variables:

```bash
# Sepolia Network Configuration
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
PRIVATE_KEY=your_private_key_here_without_0x_prefix

# Etherscan API Key (for contract verification)
ETHERSCAN_API_KEY=your_etherscan_api_key_here

# Biconomy Configuration (for your backend)
BICONOMY_API_KEY=your_biconomy_api_key
BICONOMY_RELAYER_KEY=your_biconomy_relayer_private_key
WEB3_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
CHAIN_ID=11155111
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

## 📦 Installation

```bash
# Install dependencies
npm install

# Install additional dependencies for zkProof generation
npm install -g circom snarkjs
```

## 🔐 Generate Verifier.sol

```bash
# Generate the Verifier contract from your Circom circuit
npm run generate-verifier
```

This will create:
- `contracts/Verifier.sol`
- `aadhaar_verification_final.zkey`
- `verification_key.json`

## 🚀 Deploy to Sepolia

```bash
# Deploy both Verifier and DIDVerifier contracts
npm run deploy
```

## ✅ Verify Contracts on Etherscan

After deployment, verify your contracts:

```bash
# Verify Verifier contract
npx hardhat verify --network sepolia <VERIFIER_ADDRESS>

# Verify DIDVerifier contract (replace with actual addresses)
npx hardhat verify --network sepolia <DIDVERIFIER_ADDRESS> "<VERIFIER_ADDRESS>"
```

## 📄 Update Backend Configuration

After deployment, update your backend configuration with the new contract addresses from `deployment_info.json`:

```python
# In your backend settings or environment variables
DID_VERIFIER_ADDRESS = "deployed_didverifier_address"
VERIFIER_ADDRESS = "deployed_verifier_address"
```

## 🧪 Test the Deployment

1. **Test zkProof generation** with your circuit
2. **Test DID verification** using the deployed contracts
3. **Test Biconomy integration** with the new addresses

## 🔍 Useful Commands

```bash
# Check contract deployment status
npx hardhat run scripts/deployDIDVerifier.js --network sepolia

# Verify contracts
npm run verify

# Deploy locally for testing
npm run deploy:local

# Generate new Verifier (if circuit changes)
npm run generate-verifier
```

## 📊 Sepolia Network Info

- **Chain ID**: 11155111
- **RPC URL**: https://sepolia.infura.io/v3/YOUR_PROJECT_ID
- **Block Explorer**: https://sepolia.etherscan.io
- **Faucet**: https://sepoliafaucet.com/

## 🆘 Troubleshooting

### Common Issues:

1. **Insufficient Sepolia ETH**: Get more from the faucet
2. **RPC Rate Limits**: Use a paid Infura/Alchemy plan
3. **Contract Verification Fails**: Check constructor parameters
4. **zkProof Generation Fails**: Ensure circom and snarkjs are installed globally

### Support:
- Check Hardhat documentation
- Verify your .env file is properly configured
- Ensure all dependencies are installed 