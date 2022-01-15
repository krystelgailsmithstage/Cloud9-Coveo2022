from typing import List

from game_message import Tick, Position, Team, TickMap, TileType, Unit, Diamond
from game_command import CommandAction, CommandType


def get_unowned_diamonds(diamonds: List[Diamond]):
    return [d for d in diamonds if d.ownerId is None]


def get_enemy_diamonds(diamonds: List[Diamond], our_units):
    our_units_ids = [unit.id for unit in our_units]
    return [d for d in diamonds if d.ownerId not in our_units_ids]


def get_closest_diamond(unit: Unit, diamonds: List[Diamond]):
    shortest_distance = None
    closest_diamond = None

    for diamond in diamonds:
        distance_x = abs(diamond.position.x - unit.position.x)
        distance_y = abs(diamond.position.y - unit.position.y)
        distance = distance_x + distance_y
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            closest_diamond = diamond

    return closest_diamond


def get_targeted_diamonds(actions, diamonds):
    targeted_diamonds = []
    for action in actions:
        if action.action == CommandType.MOVE:
            for diamond in diamonds:
                if action.target == diamond.position:
                    targeted_diamonds.append(diamond)

    return targeted_diamonds