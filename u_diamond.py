from typing import List

from game_message import Unit, Diamond, Tick
from game_command import CommandType


def get_unowned_diamonds(diamonds: List[Diamond]):
    return [d for d in diamonds if d.ownerId is None]


def get_enemy_diamonds(diamonds: List[Diamond], our_units):
    our_units_ids = [unit.id for unit in our_units]
    return [d for d in diamonds if d.ownerId not in our_units_ids]


def get_all_diamonds_positions(diamonds: List[Diamond]):
    return [d.position for d in diamonds]


def distance_between_unit_and_diamond(diamond, unit):
    distance_x = abs(diamond.position.x - unit.position.x)
    distance_y = abs(diamond.position.y - unit.position.y)
    distance = distance_x + distance_y
    return distance


def get_closest_diamond(unit: Unit, diamonds: List[Diamond]):
    shortest_distance = None
    closest_diamond = None

    for diamond in filter(None, diamonds):
        distance = distance_between_unit_and_diamond(diamond, unit)
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


def get_diamonds_by_priority(tick: Tick, unit: Unit):
    sorted_diamonds = []
    for d in tick.map.diamonds:
        dist = distance_between_unit_and_diamond(d, unit)
        priority = 0.3 * d.points + 50 / dist
        sorted_diamonds.append((d, priority))

    sorted_diamonds.sort(key=lambda x: x[1], reverse=True)
    diamond_list = [d[0] for d in sorted_diamonds]
    return diamond_list
