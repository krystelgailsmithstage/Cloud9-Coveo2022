import copy
from typing import List
from game_message import Tick, Team
from game_command import CommandAction, CommandType

from u_actions import get_next_action
from u_spawn import get_spawn_position


def get_next_moves(tick: Tick, zones) -> List:
    """
    Here is where the magic happens, for now the moves are random. I bet you can do better ;)

    No path finding is required, you can simply send a destination per unit and the game will move your unit towards
    it in the next turns.
    """
    my_team: Team = tick.get_teams_by_id()[tick.teamId]
    actions: List = []
    index = 0
    for unit in my_team.units:
        tick_copy = copy.deepcopy(tick)
        if not unit.hasSpawned:
            actions.append(
                CommandAction(
                    action=CommandType.SPAWN,
                    unitId=unit.id,
                    target=get_spawn_position(tick.map, index % len(tick.map.diamonds))
                )
            )
            index = index + 1
        else:
            next_action, next_position = get_next_action(tick_copy, unit, zones)
            actions.append(
                CommandAction(
                    action=next_action,
                    unitId=unit.id,
                    target=next_position
                )
            )

    return actions
