from game_message import Tick, Position, Team, TickMap, TileType, Unit
from u_diamond import get_all_diamonds_positions


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


def validate_position_availability(tick: Tick, target_position: Position):
    """
    This function should be called everytime before taking a movement decision and should
    :return:
    """
    surrounding_positions = get_surrounding_tiles(tick, target_position)

    surrounded = EMPTY not in [pos[1] for pos in surrounding_positions]

    # If the tile is completely surrounded
    if surrounded:
        # If the tile is completely covered by terrain, deem the tile as unreachable
        return False
        # If one of the adjacent tile has an enemy on it, try to get the closest available tile to it

        # If one of the adjacent tile is a diamond
    else:
        return True


def get_surrounding_tiles(tick: Tick, position: Position):
    surrounding_positions = [
        Position(x=position.x, y=position.y - 1),
        Position(x=position.x + 1, y=position.y),
        Position(x=position.x, y=position.y + 1),
        Position(x=position.x - 1, y=position.y)
    ]

    surrounding_types = []

    # Loop for all initial positions given one
    for pos in surrounding_positions:
        # If the tile is out of bound, add it as a None type of tile
        if not tick.map.validate_tile_exists(pos):
            surrounding_types.append((pos, NONE))
        else:
            # If the tile is a terrain, add it as such
            t_type = tick.map.get_tile_type_at(pos)
            if t_type != TileType.EMPTY:
                surrounding_types.append((pos, TERRAIN))
            # Else, verify there is not already a
            else:
                # Verify there isn't ane enemy or one of our bot at the given surrounding position
                all_units_pos = get_all_units_positions(tick)
                all_diamonds_pos = get_all_diamonds_positions(tick.map.diamonds)
                if pos in all_units_pos:
                    surrounding_types.append((pos, OCCUPIED))
                elif pos in all_diamonds_pos:
                    surrounding_types.append((pos, DIAMOND))
                else:
                    surrounding_types.append((pos, EMPTY))

    return surrounding_types


OCCUPIED = "Occupied"
DIAMOND = "Diamond"
TERRAIN = "Terrain"
EMPTY = "Empty"
NONE = None
