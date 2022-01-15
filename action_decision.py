from game_message import Tick, Position, Team, TickMap, TileType, Unit
from game_command import CommandAction, CommandType
from spawn import get_spawn_borders

def get_next_action(tick: Tick, unit, actions):
    my_team: Team = tick.get_teams_by_id()[tick.teamId]

    targeted_diamonds = get_targeted_diamonds(actions, tick.map.diamonds)

    closest_diamond = get_closest_diamond(unit, get_available_diamonds(targeted_diamonds, tick.map))

    if tick.tick == tick.totalTick - 1:
        return get_drop_action(unit, tick)

    return CommandType.MOVE, closest_diamond.position


def get_closest_diamond(unit: Unit, diamond_list):
    closest_diamond = None
    shortest_distance = None

    for diamond in diamond_list:
        distance_x = abs(diamond.position.x - unit.position.x)
        distance_y = abs(diamond.position.x - unit.position.x)
        distance = distance_x + distance_y
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            closest_diamond = diamond

    if closest_diamond == None:
        return unit

    return closest_diamond

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

    return closest_spawn, distance

def get_diamond_spawn_pairs(diamonds, spawns):
    pair = []
    for diamond in diamonds:
        pair.append(get_closest_spawn(diamond, spawns))

    pair.sort(key=lambda x:x[1])

    return pair


def get_targeted_diamonds(actions, diamonds):
    targeted_diamonds = []
    for action in actions:
        if action.action == CommandType.MOVE:
            for diamond in diamonds:
                if action.target == diamond.position:
                    targeted_diamonds.append(diamond)

    return targeted_diamonds


def get_available_diamonds(targeted_diamonds, tick_map):
    filtered_diamonds = [diamond for diamond in tick_map.diamonds if diamond not in targeted_diamonds]

    return filtered_diamonds


def get_drop_action(unit: Unit, tick):
    positions = [
        Position(x=unit.position.x, y=unit.position.y - 1),
        Position(x=unit.position.x + 1, y=unit.position.y),
        Position(x=unit.position.x, y=unit.position.y + 1),
        Position(x=unit.position.x - 1, y=unit.position.y),
    ]

    for position in positions:
        # print(position)
        if tick.map.validate_tile_exists(position) and tick.map.get_tile_type_at(position) == TileType.EMPTY:
            return CommandType.DROP, position

    return CommandType.DROP, unit.position

#
# def get_summon_action(unit: Unit, tick):
