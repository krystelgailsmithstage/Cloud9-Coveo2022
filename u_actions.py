from game_message import Tick, Position, Team, TickMap, TileType, Unit

from u_diamond import *
from u_position import *
zones = []


def check_lineOfSight(enemy_position, unit, tick):
        isInSight = -1
        vine_position = unit.position
        if enemy_position.y == unit.position.y:
            if enemy_position.x - unit.position.x > 0:
                # verify right
                while vine_position != enemy_position:
                    if not tick.map.validate_tile_exists(vine_position) or tick.map.get_tile_type_at(vine_position) == TileType.WALL or tick.map.get_tile_type_at(vine_position) == TileType.SPAWN:
                        break
                    else:
                        vine_position = Position(vine_position.x + 1, vine_position.y)
                if vine_position == enemy_position:
                    isInSight = 0
            else:
                # verify left
                while vine_position != enemy_position:
                    if not tick.map.validate_tile_exists(vine_position) or tick.map.get_tile_type_at(vine_position) == TileType.WALL or tick.map.get_tile_type_at(vine_position) == TileType.SPAWN:
                        break
                    else:
                        vine_position = Position(vine_position.x - 1, vine_position.y)
                if vine_position == enemy_position:
                    isInSight = 1
        elif enemy_position.x == unit.position.x:
            if enemy_position.y - unit.position.y > 0:
                # verify down
                while vine_position != enemy_position:
                    if not tick.map.validate_tile_exists(vine_position) or tick.map.get_tile_type_at(vine_position) == TileType.WALL or tick.map.get_tile_type_at(vine_position) == TileType.SPAWN:
                        break
                    else:
                        vine_position = Position(vine_position.x, vine_position.y + 1)
                if vine_position == enemy_position:
                    isInSight = 2
            else:
                # verify up
                while vine_position != enemy_position:
                    if not tick.map.validate_tile_exists(vine_position) or tick.map.get_tile_type_at(vine_position) == TileType.WALL or tick.map.get_tile_type_at(vine_position) == TileType.SPAWN:
                        break
                    else:
                        vine_position = Position(vine_position.x, vine_position.y - 1)
                if vine_position == enemy_position:
                    isInSight = 3
        return isInSight, enemy_position


def get_next_action(tick: Tick, unit, all_zones):
    """
    The big papa decision maker

    :param tick:
    :param unit:

    :return: The action to be taken for the given Unit
    """
    global zones
    zones = all_zones
    my_team: Team = tick.get_teams_by_id()[tick.teamId]

    clear_unavailable_diamonds(tick, tick.map.diamonds, unit)
    filter_diamonds_in_same_zone(tick, unit, tick.map.diamonds)

    command_type_to_return = CommandType.NONE
    position_to_return = None

    # if tick.map.get_tile_type_at(unit.position) == TileType.SPAWN:
    #     print(f"UNIT {unit.id} is in spawn at ({unit.position.x}, {unit.position.y})")


    # Make sure to drop the owned diamonds on the last tick at all times
    if tick.tick == tick.totalTick - 1 and unit.hasDiamond:
        return get_drop_action(unit, tick)
        # return command_type_to_return, position_to_return

    # First major use case is if the diamond does not have a diamond
    if not unit.hasDiamond:
        # print(f"Tick diamonds: {tick.map.diamonds} for unit {unit.position}")
        ordered_diamonds = get_diamonds_by_priority(tick, unit)

        for diamond in ordered_diamonds:
            # If diamond is owned by our team, test with the next diamond in the priority list
            if diamond.ownerId in [owner.id for owner in my_team.units]:
                pass

            # Else if an enemy has it, go in attack mode towards this diamond (and enemy)
            elif diamond.ownerId in [owner.id for owner in get_all_enemy_ids(tick, my_team)]:
                # print(f"Unit {unit.id} ({unit.position.x}, {unit.position.y}) is targeting ane enemy diamond!")
                enemy_adjacent, enemy_position = is_enemy_adjacent(unit, tick)
                # If the enemy is close, attack it
                if enemy_adjacent:
                    if tick.map.get_tile_type_at(enemy_position) != TileType.SPAWN\
                            and tick.map.get_tile_type_at(unit.position) != TileType.SPAWN:
                        return CommandType.ATTACK, enemy_position
                # Walk towards the closest empty tile around the diamond
                else:
                    vine_array = []
                    for enemy_diamond in get_enemy_diamonds_not_null(tick.map.diamonds, my_team.units):
                        vine_array.append(check_lineOfSight(enemy_diamond.position, unit, tick))

                    for vine_orientation, vine_position in vine_array:
                        if vine_orientation > -1 and tick.map.get_tile_type_at(unit.position) != TileType.SPAWN:
                            return CommandType.VINE, vine_position
                    empty_tiles_around = get_empty_tiles(diamond.position, tick)
                    if len(empty_tiles_around) > 0:
                        return CommandType.MOVE, empty_tiles_around[0]
                    else:
                        return CommandType.MOVE, diamond.position
            # Else, just move to the diamond
            else:
                return CommandType.MOVE, diamond.position

        enemy_adjacent, enemy_position = is_enemy_adjacent(unit, tick)
        if enemy_adjacent:
            if tick.map.get_tile_type_at(enemy_position) != TileType.SPAWN \
                    and tick.map.get_tile_type_at(unit.position) != TileType.SPAWN:
                return CommandType.ATTACK, enemy_position
        return CommandType.NONE, None

    # Second major use case is if the diamond does not have a diamond
    elif unit.hasDiamond:
        vine_array = []

        enemy_diamonds_not_null = get_enemy_diamonds_not_null(tick.map.diamonds, my_team.units)
        enemies_positions = get_all_enemies_positions(tick, my_team)
        enemies_without_diamond = [enemy for enemy in enemies_positions if enemy not in enemy_diamonds_not_null]
        for enemy_without_diamond in filter(None, enemies_without_diamond):
            vine_array.append(check_lineOfSight(enemy_without_diamond, unit, tick))

        for vine_orientation, vine_position in vine_array:
            if vine_orientation > -1:
                return get_drop_action(unit, tick)

        closest_enemy = get_closest_enemy(tick, unit)
        if closest_enemy is not None:
            distance = abs(closest_enemy.x - unit.position.x) + abs(closest_enemy.y - unit.position.y)

            # If the unit is kind of far enoff, we summon
            diamond_lvl = get_summon_level_for_unit(unit, tick.map)
            # print(f"Unit {unit.id} ({unit.position.x}, {unit.position.y}) is verifying if it should summon")
            ticks_left = tick.totalTick - tick.tick
            if distance > (3 + diamond_lvl) and diamond_lvl < 5 and ticks_left > (diamond_lvl + 1):
                return CommandType.SUMMON, unit.position

            # When enemy is too close, dop ton gun
            if distance < 2:
                return get_drop_action(unit, tick)

            # If the unit is too close from enemy units, move away
            else:
                return CommandType.MOVE, escape_from_enemy_action(tick, unit)
        else:
            return CommandType.SUMMON, unit.position

    # Return a None command for this unit to make sure the code does not crash
    else:
        return CommandType.NONE, None


def try_vine(unit, tick, my_team):
    vine_array = []
    x = get_enemy_diamonds(tick.map.diamonds, my_team.units)
    for enemy_diamond in get_enemy_diamonds(tick.map.diamonds, my_team.units):
        vine_array.append(check_lineOfSight(enemy_diamond.position, unit, tick));

    for vine_orientation, vine_position  in vine_array:
        if vine_orientation > -1:
            return CommandType.VINE, vine_position


def clear_unavailable_diamonds(tick: Tick, diamonds: List[Diamond], unit):
    diamonds_copy = diamonds.copy()
    for di in diamonds_copy:
        if not validate_position_availability(tick, di.position) and unit.diamondId != di.id:
            # print(f"REMOVING diamond at position {di.position} from available diamonds! {di.id}")
            diamonds.remove(di)


def filter_diamonds_in_same_zone(tick: Tick, unit: Unit, diamonds: List[Diamond]):
    diamonds_copy = diamonds.copy()

    if tick.map.get_tile_type_at(unit.position) == TileType.EMPTY:
        my_zone = get_my_zone(unit.position)
        for di in diamonds_copy:
            if di.position not in my_zone:
                # print(f"REMOVING diamond at position {di.position}, not in same zone!")
                diamonds.remove(di)


def get_my_zone(position: Position):
    for z in zones:
        if position in z:
            return z


def escape_from_enemy_action(tick, unit):
    closest_enemy_position = get_closest_enemy(tick, unit)
    if closest_enemy_position is not None:
        if abs(unit.position.x - closest_enemy_position.x) < abs(unit.position.y - closest_enemy_position.y):
            moved_away, position = try_move_x(tick, unit, closest_enemy_position)
            if not moved_away:
                moved_away, position = try_move_y(tick, unit, closest_enemy_position)
        else:
            moved_away, position = try_move_y(tick, unit, closest_enemy_position)
            if not moved_away:
                moved_away, position = try_move_x(tick, unit, closest_enemy_position)
        return position
    return unit.position


def try_move_x(tick, unit, closest_enemy_position):
    # Move Horizontally
    moved_away = False

    if unit.position.x - closest_enemy_position.x <= 0:
        # Move Left
        position = Position(unit.position.x - 1, unit.position.y)
        if position in get_empty_non_player_tiles(position, tick):
            moved_away = True
    else:
        # Move Right
        position = Position(unit.position.x + 1, unit.position.y)
        if position in get_empty_non_player_tiles(position, tick):
            moved_away = True
    return moved_away, position


def try_move_y(tick, unit, closest_enemy_position):
    # Move Vertically
    moved_away = False
    if unit.position.y - closest_enemy_position.y <= 0:
        # Move Up
        position = Position(unit.position.x, unit.position.y - 1)
        if position in get_empty_non_player_tiles(position, tick):
            moved_away = True
    else:
        # Move Down
        position = Position(unit.position.x, unit.position.y + 1)
        if position in get_empty_non_player_tiles(position, tick):
            moved_away = True
    return moved_away, position


def get_empty_non_player_tiles(position: Position, tick: Tick):
    empty_surroundings = get_empty_tiles(position, tick)
    empty_surroundings_copy = empty_surroundings.copy()
    for tile in empty_surroundings_copy:
        if tile in get_all_units_positions(tick):
            empty_surroundings.remove(tile)
    return empty_surroundings


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
    positions = get_empty_non_player_tiles(unit.position, tick)
    print(f"Dropping: {positions}")
    if len(positions) > 0:
        return CommandType.DROP, positions[0]
    return CommandType.DROP, unit.position


def get_summon_level_for_unit(unit: Unit, tick_map: TickMap):
    for diamond in tick_map.diamonds:
        if diamond.id == unit.diamondId:
            return diamond.summonLevel


def is_enemy_adjacent(unit: Unit, tick: Tick):
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
            (not tick.map.get_tile_type_at(pos) == TileType.WALL \
             or not tick.map.get_tile_type_at(pos) == TileType.SPAWN):
        pos = Position(x=unit.position.x + i, y=unit.position.y - i)
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
            if shortest_distance is None or distance < shortest_distance and \
                    tick.map.get_tile_type_at(pos) != TileType.SPAWN:
                shortest_distance = distance
                closest_enemy = pos
        return closest_enemy
    else:
        return None


def get_all_enemy_ids(tick, my_team):
    all_enemy_units = []
    for team in tick.teams:
        # only if its not our team so we dont kill ourselves lol
        if team.id != my_team.id:
            all_enemy_units.extend(team.units)

    return all_enemy_units