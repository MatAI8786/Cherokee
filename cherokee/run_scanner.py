import asyncio
import os
from aiohttp import web
from .listeners import BaseListener
from .analyzer.token_analyzer import TokenAnalyzer
from .database import SessionLocal, init_db
from .models import Token
from .trading import PaperTrader

async def main():
    init_db()
    queue = asyncio.Queue()
    listener = BaseListener(queue)
    session = SessionLocal()
    analyzer = TokenAnalyzer(
        session,
        etherscan_api_key=os.getenv('ETHERSCAN_API_KEY', ''),
        bscscan_api_key=os.getenv('BSC_SCAN_API_KEY', '')
    )
    trader = PaperTrader()

    async def start_health_server():
        async def health(request):
            return web.json_response({'status': 'ok'})

        app = web.Application()
        app.router.add_get('/healthz', health)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 5001)
        await site.start()

    async def consume():
        while True:
            token_info = await queue.get()
            result = await analyzer.analyze(token_info['address'], token_info['chain'])
            existing = session.query(Token).filter_by(address=token_info['address']).first()
            if existing:
                for k, v in result.items():
                    setattr(existing, k, v)
            else:
                existing = Token.from_dict(result)
                session.add(existing)
            session.commit()
            token = existing
            print(f"Detected token {token.address} with risk {token.risk_level}")

            if token.risk_level in ['Low', 'Medium']:
                # buy a minimal amount for paper trading
                await trader.buy(token.address, quantity=1, price=1.0, reasoning=token.risk_level)

    await asyncio.gather(listener.start(), consume(), start_health_server())

if __name__ == '__main__':
    asyncio.run(main())
