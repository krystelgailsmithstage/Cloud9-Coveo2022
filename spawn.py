from typing import List
from game_message import Tick, Position, Team, TickMap, TileType, Diamond
from game_command import CommandAction, CommandType
from action_decision import get_closest_diamond, get_targeted_diamonds, get_available_diamonds


def get_spawn_borders(spawnPositions: List[Position], tick_map: TickMap) -> List[Position]:
    spawnsBorder: List[Position] = []

    for position in spawnPositions:
        if has_around(tick_map, position, TileType.EMPTY):
            spawnsBorder.append(position)

    return spawnsBorder


def get_closest_spawn_positions(spawnBorders: List[Position], tick_map, actions) -> List[Position]:
    spawn_closest_diamond_list = []

    targeted_diamonds = get_targeted_diamonds(actions, tick_map.diamonds)

    for spawn in spawnBorders:
        closest_diamond, shortest_distance = get_spawn_diamond(spawn, get_available_diamonds(targeted_diamonds, tick_map))
        spawn_closest_diamond_list.append((spawn, shortest_distance))

    spawn_closest_diamond_list.sort(key=lambda x:x[1])
    spawn_closest_diamond_list = get_available_spawn(get_targeted_spawns(actions, spawn_closest_diamond_list), spawn_closest_diamond_list)
    return spawn_closest_diamond_list




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



def get_spawn_diamond(pos: Position, diamond_list):
    closest_diamond = None
    shortest_distance = None

    for diamond in diamond_list:
        distance_x = abs(diamond.position.x - pos.x)
        distance_y = abs(diamond.position.y - pos.y)
        distance = distance_x + distance_y
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            closest_diamond = diamond

    return closest_diamond, shortest_distance



def get_targeted_spawns(actions, spawns):
    targeted_spawns = []
    for action in actions:
        if action.action == CommandType.SPAWN:
            for spawn in spawns:
                if action.target == spawn[0]:
                    targeted_spawns.append(spawn)

    return targeted_spawns


def get_available_spawn(targeted_spawns, spawns):
    filtered_spans = [spawn for spawn in spawns if spawn not in targeted_spawns]
    return filtered_spans
