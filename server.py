#!/usr/bin/env python

import asyncio
import datetime
import random
from tags import Runner 
from websockets.asyncio.server import broadcast, serve

words = ["summer", "winter", "dark", "sleep"]

CONNECTIONS = set()
async def register(websocket):
    CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CONNECTIONS.remove(websocket)

async def show_time():
    run = Runner()    
    count = 0
    while True:
        message = datetime.datetime.utcnow().isoformat() + "Z"
        broadcast(CONNECTIONS, message)
        print(message)
        run.process_msg(words[count % len(words)])
        count +=1
        await asyncio.sleep(random.random() * 2.0 + 60)

async def main():
    async with serve(register, "localhost", 5678):
        await show_time()

if __name__ == "__main__":
    asyncio.run(main())