from typing import List
from game_message import Tick, Position, Team, TickMap, TileType
from game_command import CommandAction, CommandType
from action_decision import get_next_action

from spawn import get_spawn_borders, get_closest_spawn_positions

import random


class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")

    def get_next_moves(self, tick: Tick) -> List:
        """
        Here is where the magic happens, for now the moves are random. I bet you can do better ;)

        No path finding is required, you can simply send a destination per unit and the game will move your unit towards
        it in the next turns.
        """
        my_team: Team = tick.get_teams_by_id()[tick.teamId]

        actions: List = []

        for unit in my_team.units:
            if not unit.hasSpawned:
                actions.append(
                    CommandAction(
                        action=CommandType.SPAWN, unitId=unit.id, target=self.get_spawn_position(tick.map, actions)
                    )
                )
            else:
                next_action, next_position = get_next_action(tick, unit, actions)
                actions.append(
                    CommandAction(action=next_action, unitId=unit.id, target=next_position)
                )

        return actions


    def get_spawn_position(self, tick_map: TickMap, actions) -> Position:
        spawns: List[Position] = []

        for x in range(tick_map.get_map_size_x()):
            for y in range(tick_map.get_map_size_y()):
                position = Position(x, y)
                if tick_map.get_tile_type_at(position) == TileType.SPAWN:
                    spawns.append(position)

        spawnsBorders = get_spawn_borders(spawns, tick_map)
        nextClosestPosition = get_closest_spawn_positions(spawnsBorders, tick_map, actions)[0][0]

        return nextClosestPosition

