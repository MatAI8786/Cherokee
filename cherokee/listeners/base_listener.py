import asyncio
import random

class BaseListener:
    def __init__(self, queue):
        self.queue = queue

    async def start(self):
        while True:
            # Simulate detection of new token every few seconds
            await asyncio.sleep(5)
            address = hex(random.getrandbits(160))
            token = {
                'address': address,
                'chain': 'ethereum'
            }
            await self.queue.put(token)
