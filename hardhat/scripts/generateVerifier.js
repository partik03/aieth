const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔧 Generating Verifier.sol from Circom circuit...');

// Create circuits directory if it doesn't exist
const circuitsDir = path.join(__dirname, '..', 'circuits');
if (!fs.existsSync(circuitsDir)) {
    fs.mkdirSync(circuitsDir, { recursive: true });
}

// Step 1: Compile the circuit
console.log('📝 Compiling circuit...');
try {
    execSync('circom circuits/aadhaar_verification.circom --r1cs --wasm --sym --c', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
    });
    console.log('✅ Circuit compiled successfully');
} catch (error) {
    console.error('❌ Circuit compilation failed:', error.message);
    process.exit(1);
}

// Step 2: Start a new powers of tau ceremony
console.log('🔐 Starting powers of tau ceremony...');
try {
    execSync('snarkjs powersoftau new bn128 12 pot12_0000.ptau -v', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
    });
    console.log('✅ Powers of tau ceremony started');
} catch (error) {
    console.error('❌ Powers of tau failed:', error.message);
    process.exit(1);
}

// Step 3: Contribute to the ceremony
console.log('🎯 Contributing to ceremony...');
try {
    execSync('snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="First contribution" -v', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
    });
    console.log('✅ Contribution completed');
} catch (error) {
    console.error('❌ Contribution failed:', error.message);
    process.exit(1);
}

// Step 4: Phase 2 of the ceremony
console.log('🔄 Starting phase 2...');
try {
    execSync('snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
    });
    console.log('✅ Phase 2 completed');
} catch (error) {
    console.error('❌ Phase 2 failed:', error.message);
    process.exit(1);
}

// Step 5: Generate zKey
console.log('🔑 Generating zKey...');
try {
    execSync('snarkjs groth16 setup aadhaar_verification.r1cs pot12_final.ptau aadhaar_verification_0000.zkey', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
    });
    console.log('✅ zKey generated');
} catch (error) {
    console.error('❌ zKey generation failed:', error.message);
    process.exit(1);
}

// Step 6: Contribute to zKey
console.log('🎯 Contributing to zKey...');
try {
    execSync('snarkjs zkey contribute aadhaar_verification_0000.zkey aadhaar_verification_final.zkey --name="1st Contributor" -v', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
    });
    console.log('✅ zKey contribution completed');
} catch (error) {
    console.error('❌ zKey contribution failed:', error.message);
    process.exit(1);
}

// Step 7: Export verification key
console.log('📋 Exporting verification key...');
try {
    execSync('snarkjs zkey export verificationkey aadhaar_verification_final.zkey verification_key.json', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
    });
    console.log('✅ Verification key exported');
} catch (error) {
    console.error('❌ Verification key export failed:', error.message);
    process.exit(1);
}

// Step 8: Generate Verifier.sol
console.log('📄 Generating Verifier.sol...');
try {
    execSync('snarkjs zkey export solidityverifier aadhaar_verification_final.zkey contracts/Verifier.sol', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
    });
    console.log('✅ Verifier.sol generated successfully!');
} catch (error) {
    console.error('❌ Verifier.sol generation failed:', error.message);
    process.exit(1);
}

// Step 9: Test the circuit
console.log('🧪 Testing the circuit...');
try {
    execSync('snarkjs groth16 fullprove circuits/input.json aadhaar_verification_final.zkey proof.json public.json', { 
        stdio: 'inherit',
        cwd: path.join(__dirname, '..')
    });
    console.log('✅ Circuit test completed');
} catch (error) {
    console.error('❌ Circuit test failed:', error.message);
    process.exit(1);
}

console.log('🎉 Verifier.sol generation completed successfully!');
console.log('📁 Files generated:');
console.log('  - contracts/Verifier.sol');
console.log('  - aadhaar_verification_final.zkey');
console.log('  - verification_key.json');
console.log('  - proof.json');
console.log('  - public.json'); 