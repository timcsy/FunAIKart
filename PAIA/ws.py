import asyncio
import websockets

async def hello():
    async with websockets.connect("ws://localhost:8765/data/id") as ws:
        await ws.send("Hello world!")
        res = await ws.recv()
        print(res)

asyncio.run(hello())