from game_message import Tick


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
