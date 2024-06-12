from typing import Sequence, Tuple, List, Dict, NamedTuple

from enum import Enum

## TYPES ##
class Tiles:
    WALL = 0
    FREE = 1
    SPAWN = 2
    MANPAC = 3
    POINT = 4
    POWERUP = 5
    GHOST = 6
    GHOST_PLUS_POINT = 7
    GHOST_PLUS_POWERUP = 8

class GameStatus(Enum):
    GAME_OVER = 0
    GAME_RUNNING = 1

class CoordinatePair(NamedTuple):
    x: int
    y: int

## CONSTANTS ##
EXIT_FAILURE = -1
EXIT_SUCCESS = 0

MAP_FILENAME = "../assets/map_WithSpawn.png"

MAX_GHOSTS = 3
MAX_POWERUPS = 3
MAX_INVINCIBILITY_TICKS = 25

POINT_COVERAGE = 0.75

INIT_MANPAC_POSITION = CoordinatePair(15, 15)
INIT_MANPAC_DIRECTION = CoordinatePair(1, 0)

