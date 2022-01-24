import asyncio
import websockets

async def router(ws, path):
    if path == '/':
        async for data in ws:
            print(data)
            await ws.send(data) # change to yours

async def main():
    async with websockets.serve(router, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())