import asyncio
import json
import logging

logger = logging.getLogger("GMGN_Agent")

class GmgnCliClient:
    def __init__(self, cli_path: str = "gmgn-cli"):
        self.cli_path = cli_path

    async def _run_cmd(self, sub_commands: list) -> dict:
        full_args = sub_commands + ["--chain", "sol", "--raw"]
        try:
            logger.info(f"🖥️ Pipeline execution: {self.cli_path} {' '.join(full_args)}")
            process = await asyncio.create_subprocess_exec(
                self.cli_path, *full_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                err_msg = stderr.decode().strip()
                logger.error(f"❌ CLI internal error: {err_msg}")
                return {"error": "CLI_ERROR", "details": err_msg}
                
            raw_output = stdout.decode().strip()
            if not raw_output:
                return {"error": "EMPTY_OUTPUT"}
                
            return json.loads(raw_output)
        except json.JSONDecodeError:
            logger.error(f"❌ JSON decode failed, raw output: {raw_output[:200]}...")
            return {"error": "JSON_DECODE_FAILED", "raw": raw_output}
        except Exception as e:
            logger.error(f"❌ System pipeline exception: {str(e)}")
            return {"error": "SYSTEM_EXCEPTION", "details": str(e)}

    async def query_gmgn_token_metrics(self, address: str) -> dict:
        logger.info(f"🚀 Launching 0.5$ deep report composite on-chain query, target CA: {address}")
        
        tasks = [
            self._run_cmd(["token", "info", "--address", address]),
            self._run_cmd(["token", "security", "--address", address]),
            self._run_cmd(["token", "pool", "--address", address])
        ]
        info_res, security_res, pool_res = await asyncio.gather(*tasks)
        
        return {
            "token_address": address,
            "base_info": info_res,
            "security_risks": security_res,
            "liquidity_pools": pool_res
        }

    async def query_gmgn_token_holders_and_traders(self, address: str, limit: int = 50) -> dict:
        tasks = [
            self._run_cmd(["token", "holders", "--address", address, "--limit", str(limit)]),
            self._run_cmd(["token", "traders", "--address", address, "--limit", str(limit)])
        ]
        holders_res, traders_res = await asyncio.gather(*tasks)
        return {
            "token_address": address,
            "top_holders_with_tags": holders_res,
            "top_traders_pnl": traders_res
        }

    async def query_gmgn_market_radar(self, radar_type: str, limit: int = 30) -> dict:
        limit_str = str(limit)
        
        if radar_type == "trending":
            return await self._run_cmd(["market", "trending", "--limit", limit_str])
        elif radar_type == "trenches":
            return await self._run_cmd(["market", "trenches", "--type", "new_creation", "--limit", limit_str])
        elif radar_type == "signal":
            return await self._run_cmd(["market", "signal"])
        elif radar_type == "hot_searches":
            return await self._run_cmd(["market", "hot-searches"])
        else:
            return {"error": "COMMAND_NOT_SUPPORTED", "hint": f"This skill was not detected on your server: {radar_type}"}

gmgn_agent_client = GmgnCliClient()