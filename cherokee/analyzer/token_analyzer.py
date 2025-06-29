import aiohttp
import json
import logging

logger = logging.getLogger(__name__)

from .risk_engine import RiskEngine
from .llm_risk import evaluate_risk

class TokenAnalyzer:
    def __init__(self, session, etherscan_api_key: str = '', bscscan_api_key: str = ''):
        self.session = session
        self.etherscan_api_key = etherscan_api_key
        self.bscscan_api_key = bscscan_api_key
        self.risk_engine = RiskEngine()

    async def fetch_token_details(self, address: str, chain: str):
        if chain == 'bsc':
            key = self.bscscan_api_key
            base = 'https://api.bscscan.com'
        else:
            key = self.etherscan_api_key
            base = 'https://api.etherscan.io'
        url = f'{base}/api?module=token&action=tokeninfo&contractaddress={address}&apikey={key}'
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as resp:
                try:
                    data = await resp.json(content_type=None)
                except Exception:
                    text = await resp.text()
                    logger.error("Unexpected response from etherscan: %s", text[:200])
                    return text
                return data

    async def analyze(self, address: str, chain: str = 'ethereum'):
        """Return token information enriched with heuristic and LLM risk."""
        details = await self.fetch_token_details(address, chain)
        logger.debug("Token details type=%s content=%s", type(details), str(details)[:200])

        # Handle string responses (e.g. errors or HTML)
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except json.JSONDecodeError:
                logger.error("Could not decode token details JSON: %s", details[:200])
                details = {}

        name = 'Unknown'
        symbol = 'UNK'
        if isinstance(details, dict):
            result = details.get('result')
            if isinstance(result, list) and result:
                first = result[0] if isinstance(result[0], dict) else {}
                name = first.get('tokenName', 'Unknown')
                symbol = first.get('symbol', 'UNK')

        risk_score, risk_level = self.risk_engine.score(details)
        llm = await evaluate_risk({
            'address': address,
            'name': name,
            'symbol': symbol,
            'chain': chain,
        })
        combined_score = (risk_score + llm['score']) / 2
        combined_level = self.risk_engine._to_level(combined_score)
        return {
            'address': address,
            'chain': chain,
            'name': name,
            'symbol': symbol,
            'risk_score': combined_score,
            'risk_level': combined_level,
            'llm_reasoning': llm['reasoning'],
        }
