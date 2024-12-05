from typing import Tuple, NamedTuple, List, Dict, Sequence

from path_node import PathNode
from tile_object import TileObject
from ghost import Ghost


## TYPES ##
class TransitionMemory(NamedTuple):
    state: Tuple[bool]
    action: Tuple[bool]
    next_action: Tuple[bool]
    reward: int
    done: bool

class Tiles:
    WALL = 0
    FREE = 1
    SPAWN = 2
    POINT = 3
    POWERUP = 4
    MANPAC = 5
    GHOST = 6
    GHOST_PLUS_POINT = 7
    GHOST_PLUS_POWERUP = 8

class GameStatus:
    GAME_OVER = True
    GAME_RUNNING = False

class CoordinatePair(NamedTuple):
    x: int
    y: int

## CONSTANTS ##
MAP_FILENAME = "assets/map_WithSpawn.png"

MAX_INVINCIBILITY_TICKS = 25

INIT_MANPAC_POSITION = CoordinatePair(15, 15)
INIT_MANPAC_DIRECTION = CoordinatePair(1, 0)

DIRECTIONS = (
    CoordinatePair(1, 0),
    CoordinatePair(-1, 0),
    CoordinatePair(0, 1),
    CoordinatePair(0, -1),
)

## TRAINING ##

MAX_MEMORY = 10000
BATCH_SIZE = 500

## ETC ##

WINDOW_WIDTH = 620  
WINDOW_HEIGHT = 620

BLOCKSIZE = 20

TICKS_PER_SECOND = 60