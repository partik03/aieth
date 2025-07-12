const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying DIDVerifier contract...");

  // First, deploy the Verifier contract
  console.log("📋 Deploying Verifier contract...");
  const Verifier = await hre.ethers.getContractFactory("Verifier");
  const verifier = await Verifier.deploy();
  await verifier.deployed();
  console.log("✅ Verifier deployed to:", verifier.address);

  // Then, deploy the DIDVerifier contract
  console.log("🔐 Deploying DIDVerifier contract...");
  const DIDVerifier = await hre.ethers.getContractFactory("DIDVerifier");
  const didVerifier = await DIDVerifier.deploy(verifier.address);
  await didVerifier.deployed();
  console.log("✅ DIDVerifier deployed to:", didVerifier.address);

  // Save deployment information
  const fs = require("fs");
  const deploymentInfo = {
    network: hre.network.name,
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
    deployedAt: new Date().toISOString(),
  };

  fs.writeFileSync(
    "deployment_info.json",
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("📄 Deployment info saved to deployment_info.json");
  console.log("🎉 Deployment completed successfully!");
  console.log("");
  console.log("📋 Contract Addresses:");
  console.log("  Verifier:", verifier.address);
  console.log("  DIDVerifier:", didVerifier.address);
  console.log("");
  console.log("🔗 Next steps:");
  console.log("  1. Update your backend configuration with the new addresses");
  console.log("  2. Test the DID verification flow");
  console.log("  3. Update your frontend to use the new contract addresses");
  console.log("  4. Verify contracts on Etherscan");
  console.log("");
  console.log("🔍 To verify contracts on Etherscan:");
  console.log(`  npx hardhat verify --network sepolia ${verifier.address}`);
  console.log(`  npx hardhat verify --network sepolia ${didVerifier.address} "${verifier.address}"`);
}

main().catch((error) => {
  console.error("❌ Deployment failed:", error);
  process.exitCode = 1;
}); 