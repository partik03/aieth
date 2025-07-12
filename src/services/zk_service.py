import subprocess
import json
import tempfile

def generate_zk_proof(aadhaar_hash, wallet_address, did):
    # 1. Prepare input.json for circuit
    input_data = {
        "aadhaar_hash": int(aadhaar_hash, 16),
        "wallet_address": int(wallet_address, 16),
        "did": did  # or hash of DID if circuit expects it
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = f"{tmpdir}/input.json"
        proof_path = f"{tmpdir}/proof.json"
        public_path = f"{tmpdir}/public.json"
        with open(input_path, "w") as f:
            json.dump(input_data, f)
        # 2. Run snarkjs
        subprocess.run([
            "snarkjs", "groth16", "fullprove",
            input_path, "circuit_final.zkey", proof_path, public_path
        ], check=True)
        # 3. Parse proof and public
        with open(proof_path) as f:
            proof = json.load(f)
        with open(public_path) as f:
            public = json.load(f)
    # 4. Format for Solidity
    a = [int(proof["pi_a"][0], 16), int(proof["pi_a"][1], 16)]
    b = [
        [int(proof["pi_b"][0][0], 16), int(proof["pi_b"][0][1], 16)],
        [int(proof["pi_b"][1][0], 16), int(proof["pi_b"][1][1], 16)]
    ]
    c = [int(proof["pi_c"][0], 16), int(proof["pi_c"][1], 16)]
    input_arr = [int(x, 16) for x in public]
    return {"a": a, "b": b, "c": c}, input_arr 