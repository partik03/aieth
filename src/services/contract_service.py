from web3 import Web3
import json
import os

def verify_and_link_onchain(a, b, c, input_arr, did, wallet_address):
    # Load contract ABI and address
    with open("deployed_didverifier.json") as f:
        data = json.load(f)
    abi = data["abi"]
    address = data["address"]

    w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_RPC_URL")))
    acct = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
    contract = w3.eth.contract(address=address, abi=abi)

    tx = contract.functions.verifyAndLink(a, b, c, input_arr, did, wallet_address).build_transaction({
        "from": acct.address,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 500000,
        "gasPrice": w3.toWei("10", "gwei"),
    })
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Parse event
    event = contract.events.DIDLinked().processReceipt(receipt)[0]["args"]
    return tx_hash.hex(), {
        "did": event["did"],
        "wallet": event["wallet"],
        "aadhaar_hash": event["aadhaarHash"]
    } 