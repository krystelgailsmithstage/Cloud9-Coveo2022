from typing import List
from game_message import Tick, Position, Team, TickMap, TileType
from game_command import CommandAction, CommandType

import random


def get_spawn_borders(spawnPositions: List[Position], tick_map: TickMap) -> List[Position]:
    spawnsBorder: List[Position] = []

    for position in spawnPositions:
        if has_around(tick_map, position, TileType.EMPTY):
            spawnsBorder.append(position)

    return spawnsBorder


def has_around(tick_map: TickMap, position: Position, tileType: TileType)  -> bool:
    maxIndexX = tick_map.get_map_size_x() - 1;
    maxIndexY = tick_map.get_map_size_y() - 1;
    if position.x - 1 >= 0:
        if tick_map.get_tile_type_at(Position(position.x - 1, position.y)) == tileType:
            return True
    if position.y - 1 >= 0:
        if tick_map.get_tile_type_at(Position(position.x, position.y - 1)) == tileType:
            return True
    if position.x + 1 <= maxIndexX:
        if tick_map.get_tile_type_at(Position(position.x + 1, position.y)) == tileType:
            return True
    if position.y + 1 <= maxIndexY:
        if tick_map.get_tile_type_at(Position(position.x, position.y + 1)) == tileType:
            return True
