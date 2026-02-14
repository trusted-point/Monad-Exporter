from typing import Tuple
from web3 import Web3
from eth_abi import encode, decode

# From staking-sdk-cli constants.py :contentReference[oaicite:2]{index=2}
GET_DELEGATOR_SELECTOR = "573c1ce0"
GET_DELEGATOR_ABI = ["uint256", "uint256", "uint256", "uint256", "uint256", "uint64", "uint64"]

def strip_0x(s: str) -> str:
    return s[2:] if s.startswith("0x") else s

def build_get_delegator_calldata(val_id: int, delegator: str) -> str:
    # Same encoding scheme as staking-sdk-cli generateCalldata.get_delegator :contentReference[oaicite:3]{index=3}
    delegator_hex = strip_0x(delegator)
    return "0x" + GET_DELEGATOR_SELECTOR + encode(["uint64", "address"], [val_id, delegator_hex]).hex()

def get_delegator(w3: Web3, contract_address: str, val_id: int, delegator: str) -> Tuple:
    calldata = build_get_delegator_calldata(val_id, delegator)
    tx = {
        "to": Web3.to_checksum_address(contract_address),
        "data": calldata,
    }
    raw = w3.eth.call(tx)  # same pattern as callGetters.call_contract :contentReference[oaicite:4]{index=4}
    return decode(GET_DELEGATOR_ABI, raw)
