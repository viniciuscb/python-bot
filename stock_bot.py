#!/usr/bin/env python

# WS client example

import asyncio
import websockets
import json

async def hello():
    host = "localhost:8000"
    room_name = input("Connect to which room?")
    async with websockets.connect(f"ws://{host}/ws/chat/{room_name}/") as websocket:

        connection_message = "stocks bot connected";

        await websocket.send(json.dumps({'message': connection_message}))
        print(f"> {connection_message}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())