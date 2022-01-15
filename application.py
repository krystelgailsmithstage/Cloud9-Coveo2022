#!/usr/bin/env python

import asyncio
import os
import websockets
import json

from typing import List
from bot import get_next_moves
from bot_message import BotMessage, MessageType
from game_message import Tick, Team
from zone import get_zones, print_zones

zones = []

async def run():
    uri = "ws://127.0.0.1:8765"

    async with websockets.connect(uri) as websocket:
        if "TOKEN" in os.environ:
            await websocket.send(json.dumps({"type": "REGISTER", "token": os.environ["TOKEN"]}))
        else:
            await websocket.send(json.dumps({"type": "REGISTER", "teamName": "MyPythonicBot"}))

        await game_loop(websocket=websocket)


async def game_loop(websocket: websockets.WebSocketServerProtocol):
    global zones
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            # Connection is closed, the game is probably over
            print("Websocket was closed.")
            break

        game_message: Tick = Tick.from_dict(json.loads(message))
        # print(f"Playing tick {game_message.tick} of {game_message.totalTick}")
        if game_message.tick == 0:
            zones = get_zones(game_message.map)
            print('global zones get')
            print_zones(zones)
        my_team: Team = game_message.get_teams_by_id()[game_message.teamId]

        if my_team.errors:
            print(f"Bot command errors :  {' '.join(my_team.errors)}")

        next_moves: List = get_next_moves(game_message)
        await websocket.send(BotMessage(type=MessageType.COMMAND, actions=next_moves, tick=game_message.tick).to_json())


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
