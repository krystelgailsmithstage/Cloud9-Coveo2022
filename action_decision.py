from game_message import Tick, Position, Team, TickMap, TileType, Unit
from game_command import CommandAction, CommandType


def get_next_action(tick: Tick, unit_id):
    my_team: Team = tick.get_teams_by_id()[tick.teamId]

    closest_diamond_position = get_closest_diamond(next(unit for unit in my_team.units if unit.id == unit_id), tick.map)

    return CommandType.MOVE, closest_diamond_position


def get_closest_diamond(unit: Unit, game_map: TickMap):
    closest_diamond = None
    shortest_distance = None

    for diamond in game_map.diamonds:
        distance_x = abs(diamond.position.x - unit.position.x)
        distance_y = abs(diamond.position.x - unit.position.x)
        distance = distance_x + distance_y
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            closest_diamond = diamond

    return closest_diamond.position

def get_shortest_distance(pos: Position, game_map: TickMap):
    closest_diamond = None
    shortest_distance = None

    for diamond in game_map.diamonds:
        distance_x = abs(pos.x - pos.x)
        distance_y = abs(pos.x - pos.x)
        distance = distance_x + distance_y
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            closest_diamond = diamond

    return shortest_distance
