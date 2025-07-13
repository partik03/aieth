const hre = require("hardhat");
const { generateAadhaarHash } = require("../utils/generateHash");

async function main() {
    console.log("🔐 Aadhaar Verification zkProof Workflow");
    console.log("========================================");

    // Step 1: Generate Aadhaar hash commitment
    const aadhaarNumber = "123412341234";
    console.log("\n1️⃣ Generating Aadhaar hash commitment...");
    const hashCommitment = await generateAadhaarHash(aadhaarNumber);
    console.log(`   Aadhaar: ${aadhaarNumber}`);
    console.log(`   Hash: ${hashCommitment}`);

    // Step 2: Simulate OTP verification (off-chain)
    console.log("\n2️⃣ Simulating OTP verification...");
    const otpVerified = 1; // 1 = verified, 0 = not verified
    console.log(`   OTP Status: ${otpVerified === 1 ? "✅ Verified" : "❌ Not Verified"}`);

    // Step 3: Generate zkProof (this would be done with snarkjs)
    console.log("\n3️⃣ Generating zkProof...");
    console.log("   📝 This step requires:");
    console.log("   - Compiled circuit (.r1cs)");
    console.log("   - Proving key (.zkey)");
    console.log("   - Input file (input.json)");
    console.log("   - snarkjs groth16 fullprove command");

    // Step 4: Deploy contracts (if not already deployed)
    console.log("\n4️⃣ Deploying contracts...");
    
    const [deployer] = await hre.ethers.getSigners();
    console.log(`   Deployer: ${deployer.address}`);

    // Deploy Verifier
    const Verifier = await hre.ethers.getContractFactory("Verifier");
    const verifier = await Verifier.deploy();
    await verifier.deployed();
    console.log(`   ✅ Verifier: ${verifier.address}`);

    // Deploy DIDVerifier
    const DIDVerifier = await hre.ethers.getContractFactory("DIDVerifier");
    const didVerifier = await DIDVerifier.deploy(deployer.address);
    await didVerifier.deployed();
    console.log(`   ✅ DIDVerifier: ${didVerifier.address}`);

    // Step 5: Pre-approve hash commitment
    console.log("\n5️⃣ Pre-approving hash commitment...");
    await didVerifier.approveHashCommitment(hashCommitment);
    console.log(`   ✅ Hash ${hashCommitment} approved`);

    // Step 6: Verify Aadhaar proof (simulated)
    console.log("\n6️⃣ Verifying Aadhaar proof...");
    
    // Mock proof data (in real scenario, this comes from snarkjs)
    const mockProof = {
        a: ["0x1234567890123456789012345678901234567890123456789012345678901234", "0x1234567890123456789012345678901234567890123456789012345678901234"],
        b: [
            ["0x1234567890123456789012345678901234567890123456789012345678901234", "0x1234567890123456789012345678901234567890123456789012345678901234"],
            ["0x1234567890123456789012345678901234567890123456789012345678901234", "0x1234567890123456789012345678901234567890123456789012345678901234"]
        ],
        c: ["0x1234567890123456789012345678901234567890123456789012345678901234", "0x1234567890123456789012345678901234567890123456789012345678901234"]
    };

    try {
        // This will fail with mock data, but shows the flow
        await didVerifier.verifyAadhaarAndLink(
            mockProof.a,
            mockProof.b,
            mockProof.c,
            otpVerified,
            hashCommitment,
            deployer.address
        );
        console.log("   ✅ Aadhaar verification successful!");
    } catch (error) {
        console.log("   ⚠️  Verification failed (expected with mock data)");
        console.log(`   Error: ${error.message}`);
    }

    // Step 7: Check verification status
    console.log("\n7️⃣ Checking verification status...");
    const isVerified = await didVerifier.isAadhaarVerified(deployer.address);
    console.log(`   User verified: ${isVerified ? "✅ Yes" : "❌ No"}`);

    // Step 8: Link DID (if Aadhaar is verified)
    console.log("\n8️⃣ Linking DID with wallet...");
    const did = "did:example:123456789";
    const wallet = deployer.address;
    
    if (isVerified) {
        try {
            await didVerifier.verifyAndLink(
                mockProof.a,
                mockProof.b,
                mockProof.c,
                [otpVerified, hashCommitment],
                did,
                wallet
            );
            console.log("   ✅ DID linked successfully!");
        } catch (error) {
            console.log("   ⚠️  DID linking failed (expected with mock data)");
        }
    } else {
        console.log("   ❌ Cannot link DID - Aadhaar not verified");
    }

    console.log("\n🎉 Workflow completed!");
    console.log("\n📋 Next Steps:");
    console.log("1. Install circom and snarkjs globally");
    console.log("2. Compile the circuit: circom circuits/aadhaar_verification.circom --r1cs --wasm");
    console.log("3. Generate proving key: snarkjs groth16 setup aadhaar_verification.r1cs pot12_final.ptau aadhaar_verification_0000.zkey");
    console.log("4. Generate proof: snarkjs groth16 fullprove input.json aadhaar_verification_final.zkey proof.json public.json");
    console.log("5. Use real proof data in the verification calls");
}

main().catch((error) => {
    console.error("❌ Workflow failed:", error);
    process.exitCode = 1;
}); 