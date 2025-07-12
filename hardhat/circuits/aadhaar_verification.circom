pragma circom 2.1.4;

include "node_modules/circomlib/circuits/poseidon.circom";
include "node_modules/circomlib/circuits/comparators.circom";

template AadhaarVerification() {
    // Public inputs
    signal input aadhaar_hash;
    signal input wallet_address;
    signal input did_hash;
    
    // Private inputs
    signal input aadhaar_number;
    signal input wallet_private_key;
    signal input did_string;
    
    // Output
    signal output verification_hash;
    
    // Components
    component hasher = Poseidon(3);
    component aadhaarChecker = IsEqual();
    component walletChecker = IsEqual();
    component didChecker = IsEqual();
    
    // Hash the private inputs
    hasher.inputs[0] <== aadhaar_number;
    hasher.inputs[1] <== wallet_private_key;
    hasher.inputs[2] <== did_string;
    
    // Verify aadhaar hash matches
    aadhaarChecker.in[0] <== aadhaar_hash;
    aadhaarChecker.in[1] <== hasher.out;
    
    // Verify wallet address (simplified - in real circuit you'd derive from private key)
    walletChecker.in[0] <== wallet_address;
    walletChecker.in[1] <== wallet_private_key;
    
    // Verify DID hash
    didChecker.in[0] <== did_hash;
    didChecker.in[1] <== did_string;
    
    // All checks must pass
    aadhaarChecker.out === 1;
    walletChecker.out === 1;
    didChecker.out === 1;
    
    // Output the verification hash
    verification_hash <== hasher.out;
}

component main { public [aadhaar_hash, wallet_address, did_hash] } = AadhaarVerification(); 