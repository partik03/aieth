const hre = require("hardhat");

async function main() {
  const DIDVerifier = await hre.ethers.getContractFactory("DIDVerifier");
  const didVerifier = await DIDVerifier.deploy();
  await didVerifier.deployed();

  console.log("DIDVerifier deployed to:", didVerifier.address);

  // Save ABI and address for backend use
  const fs = require("fs");
  fs.writeFileSync(
    "deployed_didverifier.json",
    JSON.stringify({
      address: didVerifier.address,
      abi: JSON.parse(
        fs.readFileSync("./artifacts/contracts/DIDVerifier.sol/DIDVerifier.json").toString()
      ).abi,
    }, null, 2)
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
}); 