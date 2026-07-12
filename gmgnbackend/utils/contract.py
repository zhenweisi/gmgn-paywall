import json
from web3 import Web3

from config import settings


w3 = Web3(
    Web3.HTTPProvider(settings.RPC_URL)
)


CONTRACT_ADDRESS = Web3.to_checksum_address(
    settings.CONTRACT_ADDRESS
)


with open("abi/paymentRouter.json", "r") as f:
    ABI = json.load(f)


contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=ABI
)

print("✅ Contract done")