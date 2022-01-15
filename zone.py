from typing import List
from game_message import Tick, Position, Team, TickMap, TileType
from game_command import CommandAction, CommandType

import random

def get_zones(tick_map: TickMap) -> List[Position]:
    zones: List[List[Position]] = []
    zones.append(get_zone(tick_map, Position(0,0)))

    for x in range(tick_map.get_map_size_x()):
        for y in range(tick_map.get_map_size_y()):
            position = Position(x, y)
            positionInAZone = False
            if tick_map.get_tile_type_at(position) == TileType.EMPTY:
                for zone in zones:
                    if positionInAZone:
                        break
                    if position in zone:
                        positionInAZone = True
                if not positionInAZone:
                    zones.append(get_zone(tick_map, position))
    return zones

def get_zone(tick_map: TickMap, start_position: Position) -> List[Position]:
    inZone: List[Position] = []

    for x in range(start_position.x, tick_map.get_map_size_x()):
        if len(inZone) > 0:
            break
        for y in range(start_position.y, tick_map.get_map_size_y()):
            position = Position(x, y)
            if tick_map.get_tile_type_at(position) == TileType.EMPTY:
                inZone.append(position)
                break

    for position in inZone:
        is_around_in_my_zone(tick_map, position, inZone)

    return inZone


def is_around_in_my_zone(tick_map: TickMap, position: Position, inZone: List[Position]):
    maxIndexX = tick_map.get_map_size_x() - 1;
    maxIndexY = tick_map.get_map_size_y() - 1;
    if position.x - 1 >= 0:
        if tick_map.get_tile_type_at(Position(position.x - 1, position.y)) == TileType.EMPTY:
            if Position(position.x - 1, position.y) not in inZone:
                inZone.append(Position(position.x - 1, position.y))
    if position.y - 1 >= 0:
        if tick_map.get_tile_type_at(Position(position.x, position.y - 1)) == TileType.EMPTY:
            if Position(position.x, position.y - 1) not in inZone:
                inZone.append(Position(position.x, position.y - 1))
    if position.x + 1 <= maxIndexX:
        if tick_map.get_tile_type_at(Position(position.x + 1, position.y)) == TileType.EMPTY:
            if Position(position.x + 1, position.y) not in inZone:
                inZone.append(Position(position.x + 1, position.y))
    if position.y + 1 <= maxIndexY:
        if tick_map.get_tile_type_at(Position(position.x, position.y + 1)) == TileType.EMPTY:
            if Position(position.x, position.y + 1) not in inZone:
                inZone.append(Position(position.x, position.y + 1))



def print_zones(zones: List[List[Position]]):
    print('nb of zones', len(zones))
    for idx, zone in enumerate(zones):
        print('zone #',idx, 'len', len(zone) ,'->>>>>> ', zone)

# zoneBorders : List[Position] = []
#     for x in range(tick_map.get_map_size_x()):
#         for y in range(tick_map.get_map_size_y()):
#             position = Position(x, y)
#             if is_border(tick_map, position):
#                 zoneBorders.append(position)
# def is_border(tick_map: TickMap, position: Position) -> bool:
#     maxIndexX = tick_map.get_map_size_x() - 1;
#     maxIndexY = tick_map.get_map_size_y() - 1;
#     nb_borders = 0
#     if tick_map.get_tile_type_at(position) != TileType.EMPTY:
#         return False
#
#     if position.x - 1 >= 0:
#         if tick_map.get_tile_type_at(Position(position.x - 1, position.y)) != TileType.EMPTY:
#             nb_borders = nb_borders + 1
#     else:
#         nb_borders = nb_borders + 1
#
#     if position.y - 1 >= 0:
#         if tick_map.get_tile_type_at(Position(position.x, position.y - 1)) != TileType.EMPTY:
#             nb_borders = nb_borders + 1
#     else:
#         nb_borders = nb_borders + 1
#
#     if position.x + 1 <= maxIndexX:
#         if tick_map.get_tile_type_at(Position(position.x + 1, position.y)) != TileType.EMPTY:
#             nb_borders = nb_borders + 1
#     else:
#         nb_borders = nb_borders + 1
#
#     if position.y + 1 <= maxIndexY:
#         if tick_map.get_tile_type_at(Position(position.x, position.y + 1)) != TileType.EMPTY:
#             nb_borders = nb_borders + 1
#     else:
#         nb_borders = nb_borders + 1
#
#
#     if nb_borders > 0:
#         return True
#     else:
#         return False


# works
# def get_zone(tick_map: TickMap, start_position: Position) -> List[Position]:
#     inZone: List[Position] = []
#
#     for x in range(tick_map.get_map_size_x()):
#         if len(inZone) > 0:
#             break
#         for y in range(tick_map.get_map_size_y()):
#             position = Position(x, y)
#             if tick_map.get_tile_type_at(position) == TileType.EMPTY:
#                 inZone.append(position)
#                 break
#
#     for position in inZone:
#         is_around_in_my_zone(tick_map, position, inZone)
#
#     return inZone