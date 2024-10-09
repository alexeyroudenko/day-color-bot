import asyncio
import websockets
from websockets import ConnectionClosed


CLIENTS = set()
async def handler(websocket):
    CLIENTS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CLIENTS.remove(websocket)

async def broadcast(message):
    print("broadcast", message)
    for websocket in CLIENTS.copy():
        try:
            await websocket.send(message)
        except ConnectionClosed:
            pass

async def broadcast_messages():
    while True:
        await asyncio.sleep(1)
        message = "hello"  # your application logic goes here
        await broadcast(message)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        #await asyncio.Future()  # run forever
        await broadcast_messages()

if __name__ == "__main__":
    asyncio.run(main())
