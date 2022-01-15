from game_message import Tick, Position, Team, TickMap, TileType, Unit
from game_command import CommandAction, CommandType

from diamond_management import get_unowned_diamonds, get_closest_diamond, get_enemy_diamonds


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

            # If an enemy is already close, attack it
            if enemy_close:
                print(unit.hasDiamond, enemy_position)
                return CommandType.ATTACK, enemy_position
            # TODO: If enemy is in line of sight, grapple

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
    else:
        return CommandType.NONE, unit.position
        # targeted_diamonds = get_targeted_diamonds(actions, tick.map.diamonds)
    #
    # enemy_close, enemy_unit = is_enemy_close(unit, tick)
    #
    # # Grosse logique sa mere
    # if unit.hasDiamond and get_summon_level_for_unit(unit, tick.map) < 5:
    #     return CommandType.SUMMON, unit.position
    #
    # elif enemy_close:
    #     should_attack_enemy, enemy_position = should_attack_close_enemy(unit, enemy_unit, tick)
    #     if should_attack_enemy:
    #         return CommandType.ATTACK, enemy_position
    #     else:
    #
    #         return CommandType.MOVE, closest_diamond.position
    #
    # elif not unit.hasDiamond:
    #     closest_diamond = get_closest_diamond(unit, get_available_diamonds(targeted_diamonds, tick.map))
    #     return CommandType.MOVE, closest_diamond.position
    #
    # elif tick.tick == tick.totalTick - 1 and unit.hasDiamond:
    #     return get_drop_action(unit, tick)
    #
    # else:
    #     return CommandType.NONE, unit.position


def get_all_units_positions(tick: Tick):
    all_positions = []
    for team in tick.teams:
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


# def get_runaway_position(unit_position: Position, enemy_position: Position, tick_map: TickMap):
