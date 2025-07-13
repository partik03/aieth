const { buildPoseidon } = require("circomlibjs");
const fs = require("fs");

async function generateAadhaarHash(aadhaarNumber) {
    try {
        // Build Poseidon hash function
        const poseidon = await buildPoseidon();
        
        // Convert Aadhaar number to BigInt
        const aadhaarBigInt = BigInt(aadhaarNumber);
        
        // Hash the Aadhaar number
        const hash = poseidon([aadhaarBigInt]);
        
        // Convert to hex string
        const hashHex = "0x" + hash.toString(16);
        
        console.log(`Aadhaar Number: ${aadhaarNumber}`);
        console.log(`Hash Commitment: ${hashHex}`);
        
        return hashHex;
    } catch (error) {
        console.error("Error generating hash:", error);
        throw error;
    }
}

async function updateInputFile(aadhaarNumber) {
    try {
        const hashCommitment = await generateAadhaarHash(aadhaarNumber);
        
        // Read current input file
        const inputPath = "./circuits/input.json";
        const inputData = JSON.parse(fs.readFileSync(inputPath, "utf8"));
        
        // Update with real values
        inputData.aadhar_secret = aadhaarNumber;
        inputData.hash_commitment = hashCommitment;
        inputData.otp_verified = 1;
        
        // Write back to file
        fs.writeFileSync(inputPath, JSON.stringify(inputData, null, 2));
        
        console.log("✅ Input file updated successfully!");
        console.log(`📁 Updated: ${inputPath}`);
        
        return hashCommitment;
    } catch (error) {
        console.error("Error updating input file:", error);
        throw error;
    }
}

// Example usage
async function main() {
    const aadhaarNumber = "123412341234"; // Replace with actual Aadhaar number
    
    console.log("🔐 Generating Aadhaar hash commitment...");
    const hashCommitment = await updateInputFile(aadhaarNumber);
    
    console.log("\n📋 Generated Input:");
    console.log(JSON.stringify({
        aadhar_secret: aadhaarNumber,
        otp_verified: 1,
        hash_commitment: hashCommitment
    }, null, 2));
}

// Export functions for use in other scripts
module.exports = {
    generateAadhaarHash,
    updateInputFile
};

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
} 