const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying all contracts to Sepolia...");

  // Get the deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("📋 Deploying contracts with account:", deployer.address);

  // Step 1: Deploy Verifier contract
  console.log("📋 Deploying Verifier contract...");
  const Verifier = await hre.ethers.getContractFactory("Verifier");
  const verifier = await Verifier.deploy();
  await verifier.deployed();
  console.log("✅ Verifier deployed to:", verifier.address);

  // Step 2: Deploy DIDVerifier contract
  console.log("🔐 Deploying DIDVerifier contract...");
  const DIDVerifier = await hre.ethers.getContractFactory("DIDVerifier");
  const didVerifier = await DIDVerifier.deploy(deployer.address); // deployer as admin
  await didVerifier.deployed();
  console.log("✅ DIDVerifier deployed to:", didVerifier.address);

  // Step 3: Deploy Custom4337Wallet contract
  console.log("💼 Deploying Custom4337Wallet contract...");
  const Custom4337Wallet = await hre.ethers.getContractFactory("Custom4337Wallet");
  
  // EntryPoint address for Sepolia (you may need to update this)
  const entryPointAddress = "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789"; // Sepolia EntryPoint
  
  const customWallet = await Custom4337Wallet.deploy(entryPointAddress, deployer.address);
  await customWallet.deployed();
  console.log("✅ Custom4337Wallet deployed to:", customWallet.address);

  // Save deployment information
  const fs = require("fs");
  const deploymentInfo = {
    network: hre.network.name,
    deployer: deployer.address,
    contracts: {
      verifier: {
        address: verifier.address,
        abi: JSON.parse(
          fs.readFileSync("./artifacts/contracts/Verifier.sol/Verifier.json").toString()
        ).abi,
      },
      didVerifier: {
        address: didVerifier.address,
        abi: JSON.parse(
          fs.readFileSync("./artifacts/contracts/DIDVerifier.sol/DIDVerifier.json").toString()
        ).abi,
      },
      custom4337Wallet: {
        address: customWallet.address,
        abi: JSON.parse(
          fs.readFileSync("./artifacts/contracts/Custom4337Wallet.sol/Custom4337Wallet.json").toString()
        ).abi,
      },
    },
    entryPoint: entryPointAddress,
    deployedAt: new Date().toISOString(),
  };

  fs.writeFileSync(
    "deployment_info.json",
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("📄 Deployment info saved to deployment_info.json");
  console.log("🎉 All contracts deployed successfully!");
  console.log("");
  console.log("📋 Contract Addresses:");
  console.log("  Verifier:", verifier.address);
  console.log("  DIDVerifier:", didVerifier.address);
  console.log("  Custom4337Wallet:", customWallet.address);
  console.log("  EntryPoint:", entryPointAddress);
  console.log("");
  console.log("🔗 Next steps:");
  console.log("  1. Verify contracts on Etherscan:");
  console.log(`     npx hardhat verify --network sepolia ${verifier.address}`);
  console.log(`     npx hardhat verify --network sepolia ${didVerifier.address} "${verifier.address}"`);
  console.log(`     npx hardhat verify --network sepolia ${customWallet.address} "${entryPointAddress}" "${deployer.address}"`);
  console.log("  2. Update your backend configuration with the new addresses");
  console.log("  3. Test the DID verification and wallet functionality");
  console.log("  4. Register the wallet with the EntryPoint contract");
}

main().catch((error) => {
  console.error("❌ Deployment failed:", error);
  process.exitCode = 1;
}); 