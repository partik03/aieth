pragma circom 2.1.4;

include "node_modules/circomlib/circuits/poseidon.circom";
include "node_modules/circomlib/circuits/comparators.circom";

template AadhaarVerification() {
    // Private inputs
    signal input aadhar_secret;  // 12-digit Aadhaar number (private)
    
    // Public inputs
    signal input otp_verified;   // Boolean: 1 if OTP was verified
    signal input hash_commitment; // Pre-computed hash of Aadhaar number
    
    // Components
    component hasher = Poseidon(1);  // Hash the Aadhaar secret
    component hashChecker = IsEqual(); // Check if hash matches commitment
    component otpChecker = IsEqual();  // Check if OTP is verified
    
    // Hash the Aadhaar secret
    hasher.inputs[0] <== aadhar_secret;
    
    // Verify the hash matches the commitment
    hashChecker.in[0] <== hasher.out;
    hashChecker.in[1] <== hash_commitment;
    
    // Verify OTP was successful
    otpChecker.in[0] <== otp_verified;
    otpChecker.in[1] <== 1;  // 1 means verified
    
    // All constraints must be satisfied
    hashChecker.out === 1;  // Hash must match commitment
    otpChecker.out === 1;   // OTP must be verified
}

component main { public [otp_verified, hash_commitment] } = AadhaarVerification(); 