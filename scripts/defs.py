from typing import Tuple, List, Dict

from enum import Enum

## TYPES ##
CoordinatePair = Tuple[ int ]


## CONSTANTS ##
EXIT_FAILURE = -1
EXIT_SUCCESS = 0

MAP_FILENAME = "../assets/map_WithSpawn.png"

MAX_GHOSTS = 1

INIT_MANPAC_POSITION = (15, 15)
INIT_MANPAC_DIRECTION = (1, 0)


## ENUMS ##
class Tiles(Enum):
    WALL = 0
    FREE = 1
    SPAWN = 2
    MANPAC = 3
    GHOST = 4
    COIN = 5
    POWERUP = 6

class GameStatus(Enum):
    GAME_OVER = 0
    GAME_RUNNING = 1


