import os
import asyncio
import logging
from json import loads
from web3 import AsyncWeb3
from web3.providers import AsyncHTTPProvider
from eth_utils import to_checksum_address

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PaymentWatcherAgent")

ARC_RPC = os.getenv("ARC_RPC", "https://rpc.testnet.arc.network")
CONTRACT_ADDRESS = to_checksum_address("0x90B56E8302237F2b88216EA6A9ad83e5f7fBcC66")
ORDERS_FILE = "orders.txt"

MINI_ABI = loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":true,"internalType":"bytes32","name":"productId","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"orderId","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"Paid","type":"event"}]')

async def handle_paid_event(event_data):
    try:
        args = event_data['args']
        
        if isinstance(args['orderId'], bytes):
            order_id_hex = "0x" + args['orderId'].hex().lower()
        else:
            order_id_hex = str(args['orderId']).lower().strip()
            if not order_id_hex.startswith("0x"): 
                order_id_hex = "0x" + order_id_hex
        
        logger.warning(f"🎉 [On-Chain Captured] Successfully detected payment event! Order ID: {order_id_hex}")

        with open(ORDERS_FILE, "a") as f:
            f.write(order_id_hex + "\n")
        logger.info(f"💾 [Storage Synchronized] Order {order_id_hex} has been successfully secured in the local ledger!")

    except Exception as e:
        logger.error(f"❌ Failed to append order to local ledger: {str(e)}")

async def main():
    logger.info("Midnight Arc Paywall Watcher Agent started successfully!")
    w3 = AsyncWeb3(AsyncHTTPProvider(ARC_RPC))
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=MINI_ABI)
    
    try:
        current_block = await w3.eth.block_number
        logger.info(f"📡 Real-time monitoring for Paid events started from block {current_block}...")
    except Exception as e:
        logger.error(f"RPC connection failed: {e}")
        return

    while True:
        try:
            latest_block = await w3.eth.block_number
            if latest_block > current_block:
                events = await contract.events.Paid.get_logs(
                    argument_filters={},
                    fromBlock=current_block + 1, 
                    toBlock=latest_block
                )
                for event in events:
                    await handle_paid_event(event)
                current_block = latest_block
            await asyncio.sleep(2)
        except Exception as loop_err:
            logger.error(f"⚠️ Monitoring loop encountered jitters: {loop_err}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())