import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CIRCLE_API_KEY: str = os.getenv("CIRCLE_API_KEY", "")
    ENTITY_SECRET: str = os.getenv("CIRCLE_ENTITY_SECRET", "")  
    AGENT_WALLET_ID: str = os.getenv("CIRCLE_AGENT_WALLET_ID", "")  

    CONTRACT_ADDRESS: str = os.getenv("PAYWALL_CONTRACT_ADDRESS", "")  
    RPC_URL: str = os.getenv("RPC_URL", "https://rpc.testnet.arc.network")
    BLOCKCHAIN: str = "ARC-TESTNET"
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", 5042002))

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    GMGN_API_KEY: str = os.getenv("GMGN_API_KEY", "")

    def __init__(self):
        if not self.CIRCLE_API_KEY:
            print("⚠️ [WARNING] CIRCLE_API_KEY not detected. Circle cloud-hosted signing features will be restricted!")
        if not self.CONTRACT_ADDRESS:
            print("⚠️ [WARNING] PAYWALL_CONTRACT_ADDRESS not detected. Please verify contract deployment configuration!")
        print("✅ Paywall core configuration initialized successfully!")

settings = Settings()