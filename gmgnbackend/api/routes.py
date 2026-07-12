# import os
# import time
# import json
# import logging
# import subprocess
# import httpx
# import asyncio
# import re
# import shutil
# from fastapi import APIRouter, HTTPException, Body
# from pydantic import BaseModel
# from eth_utils import keccak, to_checksum_address

# from config import settings
# from circle.web3 import utils, developer_controlled_wallets

# logger = logging.getLogger("GMGNPaywall")
# router = APIRouter()


# try:
#     circle_client = utils.init_developer_controlled_wallets_client(
#         api_key=settings.CIRCLE_API_KEY, entity_secret=settings.ENTITY_SECRET
#     )
#     sign_api = developer_controlled_wallets.SigningApi(circle_client)
# except Exception as e:
#     logger.error(f"⚠️ Circle 签名服务初始化失败: {e}")


# def extract_address(text: str) -> str | None:
#     """精准提取 EVM (0x) 或 Solana (Base58) 地址，严禁在此执行大小写转换"""
#     if not text: return None
#     text = text.strip()
#     evm_match = re.search(r'0x[a-fA-F0-9]{40}', text)
#     if evm_match: return evm_match.group(0)
    
#     sol_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', text)
#     if sol_match:
#         addr = sol_match.group(0)
#         if 32 <= len(addr) <= 44: return addr
#     return None


# class GMGNToolKit:
#     @staticmethod
#     def run_cli(args: list) -> dict:
#         """物理隐式直出命令，完美兼容 Windows (.cmd) 与 Linux VPS"""
#         cli_executable = shutil.which("gmgn-cli")
#         if not cli_executable:
#             return {"error": "gmgn-cli not found in PATH. Please install globally."}

#         cmd = [cli_executable] + args + ["--raw"]
        
#         is_windows_cmd = os.name == 'nt' and (
#             cli_executable.lower().endswith('.cmd') or 
#             cli_executable.lower().endswith('.bat')
#         )

#         try:
#             logger.info(f"🎬 隐式激活物理工具链 (shell={is_windows_cmd}): {' '.join(cmd)}")
#             res = subprocess.run(
#                 cmd, 
#                 capture_output=True, 
#                 text=True, 
#                 check=True,
#                 shell=is_windows_cmd,
#                 encoding="utf-8", 
#                 errors="ignore"
#             )
#             output = res.stdout.strip()
#             return json.loads(output) if output else {"error": "CLI returned empty result"}
#         except subprocess.CalledProcessError as cpe:
#             logger.error(f"❌ CLI 内部报错返回码 {cpe.returncode}: {cpe.stderr.strip()}")
#             return {"error": f"CLI execution failed: {cpe.stderr.strip()}"}
#         except Exception as e:
#             logger.error(f"❌ 物理工具调用发生非预期故障 [{' '.join(cmd)}]: {str(e)}")
#             return {"error": str(e)}

#     @classmethod
#     def get_token_package(cls, ca: str, chain: str) -> dict:
#         """/token: 基础信息 + 流动性池 + K线数据"""
#         return {
#             "info": cls.run_cli(["token", "info", "--chain", chain, "--address", ca]),
#             "pool": cls.run_cli(["token", "pool", "--chain", chain, "--address", ca]),
#             "kline": cls.run_cli(["market", "kline", "--chain", chain, "--address", ca, "--resolution", "5m"])
#         }

#     @classmethod
#     def get_security_package(cls, ca: str, chain: str) -> dict:
#         """/security: 安全性/老鼠仓 + 前N持仓 + 顶级交易者"""
#         return {
#             "security": cls.run_cli(["token", "security", "--chain", chain, "--address", ca]),
#             "holders": cls.run_cli(["token", "holders", "--chain", chain, "--address", ca, "--limit", "30"]),
#             "traders": cls.run_cli(["token", "traders", "--chain", chain, "--address", ca, "--limit", "20"])
#         }

#     @classmethod
#     def get_portfolio_package(cls, wallet: str, chain: str) -> dict:
#         """/wallet: 当前持仓PnL + 交易流水 + 胜率战绩统计"""
#         return {
#             "holdings": cls.run_cli(["portfolio", "holdings", "--chain", chain, "--wallet", wallet, "--limit", "20"]),
#             "activity": cls.run_cli(["portfolio", "activity", "--chain", chain, "--wallet", wallet, "--limit", "30"]),
#             "stats": cls.run_cli(["portfolio", "stats", "--chain", chain, "--wallet", wallet])
#         }

#     @classmethod
#     def get_market_package(cls, chain: str) -> dict:
#         """/market: 5m趋势榜 + 新币内盘发射池"""
#         return {
#             "trending": cls.run_cli(["market", "trending", "--chain", chain, "--interval", "5m", "--limit", "20", "--filter", "not_risk"]),
#             "trenches": cls.run_cli(["market", "trenches", "--chain", chain, "--type", "new_creation"])
#         }

#     @classmethod
#     def get_track_package(cls) -> dict:
#         """/track: KOL 喊单流 + Smart Money 流向 + 关注钱包流水 (解决缺失 --chain 报错)"""
       
#         return {
#             "kol": cls.run_cli(["track", "kol", "--chain", "sol", "--limit", "10", "--side", "buy"]),
#             "smartmoney": cls.run_cli(["track", "smartmoney", "--chain", "sol", "--limit", "10", "--side", "buy"]),
#             "follow": cls.run_cli(["track", "follow-wallet", "--chain", "sol", "--limit", "15"])
#         }


# class AlphaRiskEngine:
#     def __init__(self):
#         self.api_key = os.getenv("DEEPSEEK_API_KEY")
#         self.api_url = "https://api.deepseek.com/v1/chat/completions"

#     async def generate_institutional_report(self, command_mode: str, raw_data: dict) -> str:
#         if not self.api_key:
#             raise HTTPException(status_code=500, detail="后端未配置 DEEPSEEK_API_KEY")

#         system_prompt = (
#             f"You are Alpha Risk Engine (ARE), a deterministic on-chain quantitative risk control engine for institutions. "
#             f"Your current parsing mode is: [{command_mode}]. "
#             f"Your output must be strictly objective, mathematical, and data-driven, completely free of narrative or emotional terms. "
#             f"The output will be rendered directly on the client UI. You must NEVER append any source data tags (e.g., , etc.) or raw JSON variables. "
#             f"Output using concise Markdown bullet points and bold formatting. Keep tokens dense, omit filler words, and output in Chinese/English technical terms."
#         )

#         async with httpx.AsyncClient(timeout=60.0) as client:
#             response = await client.post(
#                 self.api_url,
#                 headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
#                 json={
#                     "model": "deepseek-chat",
#                     "messages": [
#                         {"role": "system", "content": system_prompt},
#                         {"role": "user", "content": f"Execute mapping analysis on this JSON payload:\n{json.dumps(raw_data)}"}
#                     ],
#                     "temperature": 0.3
#                 }
#             )
#             return response.json()["choices"][0]["message"]["content"]

# risk_engine = AlphaRiskEngine()


# @router.post("/v1/payment/signature")
# async def get_payment_signature(payload: dict = Body(...)):
#     user_wallet = payload.get("userWallet")
#     product_type = payload.get("productType")
#     if not user_wallet or not product_type:
#         raise HTTPException(status_code=400, detail="Missing parameters")
        
#     try:
#         amount = 5000000 if product_type == "deep_report" else 500000
#         product_id_hex = "0x" + keccak(text=product_type).hex()
#         order_str = f"GMGN-{int(time.time())}-{user_wallet[-6:]}"
#         order_id_hex = "0x" + keccak(text=order_str).hex()
#         expiry = int(time.time()) + 600
#         ARC_CHAIN_ID = 5042002
        
#         contract_address = to_checksum_address(settings.CONTRACT_ADDRESS)
#         user_address = to_checksum_address(user_wallet)

#         eip712_structured_data = {
#             "types": {
#                 "EIP712Domain": [
#                     {"name": "name", "type": "string"}, {"name": "version", "type": "string"},
#                     {"name": "chainId", "type": "uint256"}, {"name": "verifyingContract", "type": "address"}
#                 ],
#                 "Payment": [
#                     {"name": "chainId", "type": "uint256"}, {"name": "contractAddress", "type": "address"},
#                     {"name": "user", "type": "address"}, {"name": "productId", "type": "bytes32"},
#                     {"name": "amount", "type": "uint256"}, {"name": "expiry", "type": "uint256"},
#                     {"name": "orderId", "type": "bytes32"}
#                 ]
#             },
#             "primaryType": "Payment",
#             "domain": {"name": "PaymentRouter", "version": "1", "chainId": ARC_CHAIN_ID, "verifyingContract": contract_address},
#             "message": {"chainId": ARC_CHAIN_ID, "contractAddress": contract_address, "user": user_address, "productId": product_id_hex, "amount": amount, "expiry": expiry, "orderId": order_id_hex}
#         }
        
#         request_body = developer_controlled_wallets.SignTypedDataRequest(
#             wallet_id=settings.AGENT_WALLET_ID, data=json.dumps(eip712_structured_data, separators=(",", ":"))
#         )
#         sdk_response = sign_api.sign_typed_data(request_body)
#         signature = sdk_response.data.signature if sdk_response.data.signature.startswith("0x") else "0x" + sdk_response.data.signature
        
#         return {
#             "success": True, 
#             "data": {
#                 "productId": product_id_hex, 
#                 "orderId": order_id_hex, 
#                 "amount": amount, 
#                 "expiry": expiry, 
#                 "signature": signature, 
#                 "chainId": ARC_CHAIN_ID
#             }
#         }
#     except Exception as e:
#         logger.error(f"Circle Signing Flow Exception: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# class GenerateReportRequest(BaseModel):
#     productType: str = ""
#     userWallet: str = ""
#     targetToken: str = "" 
#     orderId: str = ""

# @router.post("/v1/report/generate")
# async def generate_report(payload: GenerateReportRequest):
#     raw_input_original = payload.targetToken.strip()
#     extracted_addr = extract_address(raw_input_original)
    
#     cmd_match_text = raw_input_original.lower()
    
#     chain = "sol"  
#     if extracted_addr and extracted_addr.startswith("0x"):
#         if "base" in cmd_match_text:
#             chain = "base"
#         elif "eth" in cmd_match_text or "ethereum" in cmd_match_text:
#             chain = "eth"
#         elif "bsc" in cmd_match_text or "bnb" in cmd_match_text:
#             chain = "bsc"
#         else:
#             chain = "base"  
#     elif extracted_addr:
#         chain = "sol"

#     try:
#         if cmd_match_text.startswith("/token"):
#             if not extracted_addr: raise HTTPException(status_code=400, detail="缺少合法的合约地址 CA")
#             mode = f"Token-Audit-Package ({chain.upper()})"
#             data_package = GMGNToolKit.get_token_package(extracted_addr, chain)
            
#         elif cmd_match_text.startswith("/security"):
#             if not extracted_addr: raise HTTPException(status_code=400, detail="缺少合法的合约地址 CA")
#             mode = f"Security-Risk-Package ({chain.upper()})"
#             data_package = GMGNToolKit.get_security_package(extracted_addr, chain)
            
#         elif cmd_match_text.startswith("/wallet"):
#             if not extracted_addr: raise HTTPException(status_code=400, detail="缺少合法的钱包地址")
#             mode = f"Portfolio-PnL-Package ({chain.upper()})"
#             data_package = GMGNToolKit.get_portfolio_package(extracted_addr, chain)
            
#         elif cmd_match_text.startswith("/market"):
#             mode = f"Market-Trending-Package ({chain.upper()})"
#             data_package = GMGNToolKit.get_market_package(chain)
            
#         elif cmd_match_text.startswith("/track"):
#             mode = "SmartMoney-KOL-Track-Package"
#             data_package = GMGNToolKit.get_track_package()
            
#         else:
#             if extracted_addr:
#                 mode = f"Default-Security-Risk ({chain.upper()})"
#                 data_package = GMGNToolKit.get_security_package(extracted_addr, chain)
#             else:
#                 raise HTTPException(status_code=400, detail="无法识别的快捷指令或链上地址格式")

#         report_content = await risk_engine.generate_institutional_report(mode, data_package)
#         return {"success": True, "data": {"report": report_content}}

#     except Exception as e:
#         logger.exception("Error routing the specific gmgn-cli tasks")
#         raise HTTPException(status_code=500, detail=str(e))



import os
import time
import json
import logging
import subprocess
import httpx
import asyncio
import re
import shutil
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from eth_utils import keccak, to_checksum_address

from config import settings
from circle.web3 import utils, developer_controlled_wallets

logger = logging.getLogger("GMGNPaywall")
router = APIRouter()


try:
    circle_client = utils.init_developer_controlled_wallets_client(
        api_key=settings.CIRCLE_API_KEY, entity_secret=settings.ENTITY_SECRET
    )
    sign_api = developer_controlled_wallets.SigningApi(circle_client)
except Exception as e:
    logger.error(f"⚠️ Circle signing service initialization failed: {e}")


def extract_address(text: str) -> str | None:
    if not text: return None
    text = text.strip()
    evm_match = re.search(r'0x[a-fA-F0-9]{40}', text)
    if evm_match: return evm_match.group(0)
    
    sol_match = re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', text)
    if sol_match:
        addr = sol_match.group(0)
        if 32 <= len(addr) <= 44: return addr
    return None


class GMGNToolKit:
    @staticmethod
    def run_cli(args: list) -> dict:
        cli_executable = shutil.which("gmgn-cli")
        if not cli_executable:
            return {"error": "gmgn-cli not found in PATH. Please install globally."}

        cmd = [cli_executable] + args + ["--raw"]
        
        is_windows_cmd = os.name == 'nt' and (
            cli_executable.lower().endswith('.cmd') or 
            cli_executable.lower().endswith('.bat')
        )

        try:
            logger.info(f"🎬 Activating physical tools (shell={is_windows_cmd}): {' '.join(cmd)}")
            res = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                shell=is_windows_cmd,
                encoding="utf-8", 
                errors="ignore"
            )
            output = res.stdout.strip()
            return json.loads(output) if output else {"error": "CLI returned empty result"}
        except subprocess.CalledProcessError as cpe:
            logger.error(f"❌ CLI internal error with return code {cpe.returncode}: {cpe.stderr.strip()}")
            return {"error": f"CLI execution failed: {cpe.stderr.strip()}"}
        except Exception as e:
            logger.error(f"❌ Unexpected failure in physical tool execution [{' '.join(cmd)}]: {str(e)}")
            return {"error": str(e)}

    @classmethod
    def get_token_package(cls, ca: str, chain: str) -> dict:
        return {
            "info": cls.run_cli(["token", "info", "--chain", chain, "--address", ca]),
            "pool": cls.run_cli(["token", "pool", "--chain", chain, "--address", ca]),
            "kline": cls.run_cli(["market", "kline", "--chain", chain, "--address", ca, "--resolution", "5m"])
        }

    @classmethod
    def get_security_package(cls, ca: str, chain: str) -> dict:
        return {
            "security": cls.run_cli(["token", "security", "--chain", chain, "--address", ca]),
            "holders": cls.run_cli(["token", "holders", "--chain", chain, "--address", ca, "--limit", "30"]),
            "traders": cls.run_cli(["token", "traders", "--chain", chain, "--address", ca, "--limit", "20"])
        }

    @classmethod
    def get_portfolio_package(cls, wallet: str, chain: str) -> dict:
        return {
            "holdings": cls.run_cli(["portfolio", "holdings", "--chain", chain, "--wallet", wallet, "--limit", "20"]),
            "activity": cls.run_cli(["portfolio", "activity", "--chain", chain, "--wallet", wallet, "--limit", "30"]),
            "stats": cls.run_cli(["portfolio", "stats", "--chain", chain, "--wallet", wallet])
        }

    @classmethod
    def get_market_package(cls, chain: str) -> dict:
        return {
            "trending": cls.run_cli(["market", "trending", "--chain", chain, "--interval", "5m", "--limit", "20", "--filter", "not_risk"]),
            "trenches": cls.run_cli(["market", "trenches", "--chain", chain, "--type", "new_creation"])
        }

    @classmethod
    def get_track_package(cls) -> dict:
        return {
            "kol": cls.run_cli(["track", "kol", "--chain", "sol", "--limit", "10", "--side", "buy"]),
            "smartmoney": cls.run_cli(["track", "smartmoney", "--chain", "sol", "--limit", "10", "--side", "buy"]),
            "follow": cls.run_cli(["track", "follow-wallet", "--chain", "sol", "--limit", "15"])
        }


class AlphaRiskEngine:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    async def generate_institutional_report(self, command_mode: str, raw_data: dict) -> str:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="Backend DEEPSEEK_API_KEY is not configured")

        system_prompt = (
            f"You are Alpha Risk Engine (ARE), a deterministic on-chain quantitative risk control engine for institutions. "
            f"Your current parsing mode is: [{command_mode}]. "
            f"Your output must be strictly objective, mathematical, and data-driven, completely free of narrative or emotional terms. "
            f"The output will be rendered directly on the client UI. You must NEVER append any source data tags (e.g., , etc.) or raw JSON variables. "
            f"Output using concise Markdown bullet points and bold formatting. Keep tokens dense, omit filler words, and output in Chinese/English technical terms."
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Execute mapping analysis on this JSON payload:\n{json.dumps(raw_data)}"}
                    ],
                    "temperature": 0.3
                }
            )
            return response.json()["choices"][0]["message"]["content"]

risk_engine = AlphaRiskEngine()


@router.post("/v1/payment/signature")
async def get_payment_signature(payload: dict = Body(...)):
    user_wallet = payload.get("userWallet")
    product_type = payload.get("productType")
    if not user_wallet or not product_type:
        raise HTTPException(status_code=400, detail="Missing parameters")
        
    try:
        amount = 5000000 if product_type == "deep_report" else 500000
        product_id_hex = "0x" + keccak(text=product_type).hex()
        order_str = f"GMGN-{int(time.time())}-{user_wallet[-6:]}"
        order_id_hex = "0x" + keccak(text=order_str).hex()
        expiry = int(time.time()) + 600
        ARC_CHAIN_ID = 5042002
        
        contract_address = to_checksum_address(settings.CONTRACT_ADDRESS)
        user_address = to_checksum_address(user_wallet)

        eip712_structured_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"}, {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"}, {"name": "verifyingContract", "type": "address"}
                ],
                "Payment": [
                    {"name": "chainId", "type": "uint256"}, {"name": "contractAddress", "type": "address"},
                    {"name": "user", "type": "address"}, {"name": "productId", "type": "bytes32"},
                    {"name": "amount", "type": "uint256"}, {"name": "expiry", "type": "uint256"},
                    {"name": "orderId", "type": "bytes32"}
                ]
            },
            "primaryType": "Payment",
            "domain": {"name": "PaymentRouter", "version": "1", "chainId": ARC_CHAIN_ID, "verifyingContract": contract_address},
            "message": {"chainId": ARC_CHAIN_ID, "contractAddress": contract_address, "user": user_address, "productId": product_id_hex, "amount": amount, "expiry": expiry, "orderId": order_id_hex}
        }
        
        request_body = developer_controlled_wallets.SignTypedDataRequest(
            wallet_id=settings.AGENT_WALLET_ID, data=json.dumps(eip712_structured_data, separators=(",", ":"))
        )
        sdk_response = sign_api.sign_typed_data(request_body)
        signature = sdk_response.data.signature if sdk_response.data.signature.startswith("0x") else "0x" + sdk_response.data.signature
        
        return {
            "success": True, 
            "data": {
                "productId": product_id_hex, 
                "orderId": order_id_hex, 
                "amount": amount, 
                "expiry": expiry, 
                "signature": signature, 
                "chainId": ARC_CHAIN_ID
            }
        }
    except Exception as e:
        logger.error(f"Circle Signing Flow Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class GenerateReportRequest(BaseModel):
    productType: str = ""
    userWallet: str = ""
    targetToken: str = "" 
    orderId: str = ""

@router.post("/v1/report/generate")
async def generate_report(payload: GenerateReportRequest):
    raw_input_original = payload.targetToken.strip()
    extracted_addr = extract_address(raw_input_original)
    
    cmd_match_text = raw_input_original.lower()
    
    chain = "sol"  
    if extracted_addr and extracted_addr.startswith("0x"):
        if "base" in cmd_match_text:
            chain = "base"
        elif "eth" in cmd_match_text or "ethereum" in cmd_match_text:
            chain = "eth"
        elif "bsc" in cmd_match_text or "bnb" in cmd_match_text:
            chain = "bsc"
        else:
            chain = "base"  
    elif extracted_addr:
        chain = "sol"

    try:
        if cmd_match_text.startswith("/token"):
            if not extracted_addr: raise HTTPException(status_code=400, detail="Missing valid Contract Address (CA)")
            mode = f"Token-Audit-Package ({chain.upper()})"
            data_package = GMGNToolKit.get_token_package(extracted_addr, chain)
            
        elif cmd_match_text.startswith("/security"):
            if not extracted_addr: raise HTTPException(status_code=400, detail="Missing valid Contract Address (CA)")
            mode = f"Security-Risk-Package ({chain.upper()})"
            data_package = GMGNToolKit.get_security_package(extracted_addr, chain)
            
        elif cmd_match_text.startswith("/wallet"):
            if not extracted_addr: raise HTTPException(status_code=400, detail="Missing valid Wallet Address")
            mode = f"Portfolio-PnL-Package ({chain.upper()})"
            data_package = GMGNToolKit.get_portfolio_package(extracted_addr, chain)
            
        elif cmd_match_text.startswith("/market"):
            mode = f"Market-Trending-Package ({chain.upper()})"
            data_package = GMGNToolKit.get_market_package(chain)
            
        elif cmd_match_text.startswith("/track"):
            mode = "SmartMoney-KOL-Track-Package"
            data_package = GMGNToolKit.get_track_package()
            
        else:
            if extracted_addr:
                mode = f"Default-Security-Risk ({chain.upper()})"
                data_package = GMGNToolKit.get_security_package(extracted_addr, chain)
            else:
                raise HTTPException(status_code=400, detail="Unrecognized shortcut command or invalid on-chain address format")

        report_content = await risk_engine.generate_institutional_report(mode, data_package)
        return {"success": True, "data": {"report": report_content}}

    except Exception as e:
        logger.exception("Error routing the specific gmgn-cli tasks")
        raise HTTPException(status_code=500, detail=str(e))