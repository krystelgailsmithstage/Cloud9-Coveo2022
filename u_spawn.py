from typing import List
from game_message import Position, TickMap, TileType
import random


def get_spawn_position(tick_map: TickMap, index) -> Position:
    spawns: List[Position] = []

    for x in range(tick_map.get_map_size_x()):
        for y in range(tick_map.get_map_size_y()):
            position = Position(x, y)
            if tick_map.get_tile_type_at(position) == TileType.SPAWN:
                spawns.append(position)

    spawnsBorders = get_spawn_borders(spawns, tick_map)
    diamond_spawn_pairs = get_diamond_spawn_pairs(tick_map.diamonds, spawnsBorders)

    if diamond_spawn_pairs[index][0] in spawnsBorders :
        return diamond_spawn_pairs[index][0]

    return spawnsBorders[random.randint(0, len(spawns) - 1)]

def get_closest_spawn(diamond, spawns):
    closest_spawn = None
    shortest_distance = None

    for spawn in spawns:
        distance_x = abs(diamond.position.x - spawn.x)
        distance_y = abs(diamond.position.y - spawn.y)
        distance = distance_x + distance_y
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            closest_spawn = spawn

    if shortest_distance > 0:
        weight = diamond.points / shortest_distance
    else:
        weight = diamond.points

    return closest_spawn, weight


def get_diamond_spawn_pairs(diamonds, spawns):
    pair = []
    for diamond in diamonds:
        pair.append(get_closest_spawn(diamond, spawns))

    pair.sort(key=lambda x: x[1], reverse=True)
    return pair


def get_spawn_borders(spawnPositions: List[Position], tick_map: TickMap) -> List[Position]:
    spawnsBorder: List[Position] = []

    for position in spawnPositions:
        if has_around(tick_map, position, TileType.EMPTY):
            spawnsBorder.append(position)

    return spawnsBorder


def has_around(tick_map: TickMap, position: Position, tileType: TileType)  -> bool:
    maxIndexX = tick_map.get_map_size_x() - 1
    maxIndexY = tick_map.get_map_size_y() - 1
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
