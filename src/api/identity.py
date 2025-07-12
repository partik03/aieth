from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.zk_service import generate_zk_proof
from src.services.contract_service import verify_and_link_onchain
from src.services.db import get_collection
from datetime import datetime

router = APIRouter()

class ProveLinkRequest(BaseModel):
    aadhaar_number: str
    wallet_address: str
    did: str

@router.post("/identity/prove-link")
async def prove_link(request: ProveLinkRequest):
    # 1. Hash Aadhaar number
    from eth_utils import keccak, to_hex
    aadhaar_hash = to_hex(keccak(text=request.aadhaar_number.replace("-", "")))

    # 2. Generate zk proof (calls snarkjs, returns proof dict and public signals)
    zk_proof, public_signals = generate_zk_proof(aadhaar_hash, request.wallet_address, request.did)

    # 3. Format proof for Solidity
    a, b, c, input_arr = zk_proof["a"], zk_proof["b"], zk_proof["c"], public_signals

    # 4. Call smart contract
    tx_hash, event = verify_and_link_onchain(a, b, c, input_arr, request.did, request.wallet_address)

    # 5. Save in MongoDB
    collection = await get_collection("did_registrations")
    await collection.insert_one({
        "did": request.did,
        "wallet_address": request.wallet_address,
        "aadhaar_hash": aadhaar_hash,
        "zk_proof": zk_proof,
        "onchain_verified": True,
        "tx_hash": tx_hash,
        "linked_at": datetime.utcnow().isoformat(),
    })

    return {
        "success": True,
        "tx_hash": tx_hash,
        "zk_proof": zk_proof,
        "event": event
    } 