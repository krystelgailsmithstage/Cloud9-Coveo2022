from game_message import Tick, Position, Team, TickMap, TileType, Unit
from game_command import CommandAction, CommandType

from diamond_management import get_unowned_diamonds, get_closest_diamond, get_enemy_diamonds

from spawn import get_spawn_borders


def get_next_action(tick: Tick, unit, actions):
    my_team: Team = tick.get_teams_by_id()[tick.teamId]

    if not unit.hasDiamond:
        unowned_diamonds = get_unowned_diamonds(tick.map.diamonds)

        # Check if diamond is available and go for it if it is
        if len(unowned_diamonds) > 0:
            closest_diamond = get_closest_diamond(unit, unowned_diamonds)
            return CommandType.MOVE, closest_diamond.position

        # Else go in attack mode towards closest enemy with a diamond
        else:
            enemy_close, enemy_position = is_enemy_close(unit, tick)
            # enemy_in_sight, enemy_grapple_position = is_enemy_lineofsight(unit, tick, my_team)
            # If an enemy is already close, attack it
            if enemy_close:
                print(unit.hasDiamond, enemy_position)
                if tick.map.get_tile_type_at(enemy_position) != TileType.SPAWN\
                        and tick.map.get_tile_type_at(unit.position) != TileType.SPAWN:
                    return CommandType.ATTACK, enemy_position
                else:
                    return CommandType.NONE, None
            # TODO: If enemy is in line of sight, grapple
            # if enemy_in_sight:
            #     return CommandType.VINE, enemy_grapple_position
            # Else move to closest enemy holding diamond
            else:
                enemy_diamonds = get_enemy_diamonds(tick.map.diamonds, my_team.units)
                closest_enemy_diamond = get_closest_diamond(unit, enemy_diamonds)
                empty_tiles_around = get_empty_tiles(closest_enemy_diamond.position, tick)
                if len(empty_tiles_around) > 0:
                    return CommandType.MOVE, empty_tiles_around[0]
                else:
                    return CommandType.NONE, None
    elif tick.tick == tick.totalTick - 1 and unit.hasDiamond:
        return get_drop_action(unit, tick)

    elif unit.hasDiamond:
        closest_enemy = get_closest_enemy(tick, unit)
        if closest_enemy is not None:
            distance = abs(closest_enemy.x - unit.position.x) + abs(closest_enemy.y - unit.position.y)

            # If the unit is kind of far enoff, we summon
            diamond_lvl = get_summon_level_for_unit(unit, tick.map)
            if distance > 2 + diamond_lvl + 1 and diamond_lvl < 5:
                return CommandType.SUMMON, unit.position

            # If the unit is too close from enemy units, move away
            else:
                return CommandType.MOVE, find_escape(tick, unit, my_team)
        # If the unit is too close from enemy units, move away
        else:
            return CommandType.MOVE, find_escape(tick, unit, my_team)
    elif tick.tick == tick.totalTick - 1 and unit.hasDiamond:
        return get_drop_action(unit, tick)
    else:
        return CommandType.NONE, None


def find_escape(tick, unit, my_team):
    closest_enemy_position = get_closest_enemy(tick, unit)
    if abs(unit.position.x - closest_enemy_position.x) < abs(unit.position.y - closest_enemy_position.y):
        # Move Horizontally
        if unit.position.x - closest_enemy_position.x < 0:
            # Move Left
            position = Position(unit.position.x - 1, unit.position.y)
        else:
            # Move Right
            position = Position(unit.position.x + 1, unit.position.y)
    else:
        # Move Vertically
        if unit.position.y - closest_enemy_position.y < 0:
            # Move Up
            position = Position(unit.position.x, unit.position.y - 1)
        else:
            # Move Down
            position = Position(unit.position.x, unit.position.y + 1)
    return position


def get_all_units_positions(tick: Tick):
    all_positions = []
    for team in tick.teams:
        all_positions.extend([unit.position for unit in team.units])

    return all_positions


def get_all_enemies_positions(tick: Tick, my_team):
    all_positions = []
    for team in tick.teams:
        if not team.id == my_team.id:
            all_positions.extend([unit.position for unit in team.units])

    return all_positions


def get_empty_tiles(position: Position, tick: Tick):
    empty_position = []

    positions = [
        Position(x=position.x, y=position.y - 1),
        Position(x=position.x + 1, y=position.y),
        Position(x=position.x, y=position.y + 1),
        Position(x=position.x - 1, y=position.y)
    ]

    for pos in positions:
        if tick.map.validate_tile_exists(pos) \
                and tick.map.get_tile_type_at(pos) == TileType.EMPTY\
                and pos not in get_all_units_positions(tick):
            empty_position.append(pos)
    return empty_position


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


def get_drop_action(unit: Unit, tick):
    positions = get_empty_tiles(unit.position, tick)
    print(f"Dropping: {positions}")
    if len(positions) > 0:
        return CommandType.DROP, positions[0]
    return CommandType.DROP, unit.position


def get_summon_level_for_unit(unit: Unit, tick_map: TickMap):
    for diamond in tick_map.diamonds:
        if diamond.id == unit.diamondId:
            return diamond.summonLevel


def is_enemy_close(unit: Unit, tick: Tick):
    my_team: Team = tick.get_teams_by_id()[tick.teamId]

    positions = [
        Position(x=unit.position.x, y=unit.position.y - 1),
        Position(x=unit.position.x + 1, y=unit.position.y),
        Position(x=unit.position.x, y=unit.position.y + 1),
        Position(x=unit.position.x - 1, y=unit.position.y)
    ]

    for team in tick.teams:
        # only if its not our team so we dont kill ourselves lol
        if team.id != my_team.id:
            for enemy_unit in team.units:
                if enemy_unit.position in positions:
                    return True, enemy_unit.position

    return False, None


def should_attack_close_enemy(unit: Unit, enemy_unit: Unit, tick: Tick):
    enemy_index = 0
    our_index = 0

    for index, team in tick.teamPlayOrderings.items():
        if team == enemy_unit.teamId:
            enemy_index = index
        elif team == unit.teamId:
            our_index = index

    if enemy_index > our_index:
        return True, enemy_unit.position
    else:
        return False, None


def is_enemy_lineofsight(unit: Unit, tick: Tick, my_team):
    enemies_positions = get_all_enemies_positions(tick, my_team)

    pos = unit.position
    i = 1
    x_positive = []
    while tick.map.validate_tile_exists(pos) and \
            (not tick.map.get_tile_type_at(pos) == TileType.WALL\
            or not tick.map.get_tile_type_at(pos) == TileType.SPAWN):
        pos = Position(x= unit.position.x + i, y= unit.position.y)
        x_positive.append(pos)
        i += 1

    pos = unit.position
    i = 1
    x_negative = []
    while tick.map.validate_tile_exists(pos) and \
            (not tick.map.get_tile_type_at(pos) == TileType.WALL\
            or not tick.map.get_tile_type_at(pos) == TileType.SPAWN):
        pos = Position(x= unit.position.x - i, y= unit.position.y)
        x_negative.append(pos)
        i += 1

    pos = unit.position
    i = 1
    y_positive = []
    while tick.map.validate_tile_exists(pos) and \
            (not tick.map.get_tile_type_at(pos) == TileType.WALL\
            or not tick.map.get_tile_type_at(pos) == TileType.SPAWN):
        pos = Position(x= unit.position.x, y= unit.position.y + i)
        y_positive.append(pos)
        i += 1

    pos = unit.position
    i = 1
    y_negative = []
    while tick.map.validate_tile_exists(pos) and \
            (not tick.map.get_tile_type_at(pos) == TileType.WALL\
            or not tick.map.get_tile_type_at(pos) == TileType.SPAWN):
        pos = Position(x= unit.position.x + i, y= unit.position.y - i)
        y_negative.append(pos)
        i += 1

    for enemy_position in enemies_positions:
        if enemy_position in x_positive \
            or enemy_position in x_negative \
                or enemy_position in y_positive \
                    or enemy_position in y_negative:
            return True, enemy_position

    return False, None


def get_closest_enemy(tick: Tick, unit: Unit):
    my_team: Team = tick.get_teams_by_id()[tick.teamId]
    enemy_positions = get_all_enemies_positions(tick, my_team)

    shortest_distance = None
    closest_enemy = None

    if enemy_positions is not None or enemy_positions is not []:
        for pos in filter(None, enemy_positions):
            distance_x = abs(pos.x - unit.position.x)
            distance_y = abs(pos.y - unit.position.y)
            distance = distance_x + distance_y
            if shortest_distance is None or distance < shortest_distance:
                shortest_distance = distance
                closest_enemy = pos
        return closest_enemy
    else:
        return None

# def get_runaway_position(unit_position: Position, enemy_position: Position, tick_map: TickMap):
