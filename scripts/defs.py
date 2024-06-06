from typing import Tuple, List, Dict
import numpy as np
import cv2

import os
import os.path 

from enum import Enum

## TYPES ##
CoordinatePair = Tuple[ int ]


## CONSTANTS ##
EXIT_FAILURE = -1
EXIT_SUCCESS = 0

MAP_FILENAME = "map_WithSpawn.png"

MAX_GHOSTS = 1

INIT_MANPAC_POSITION = (15, 15)


## ENUMS ##
class Tiles(Enum):
    WALL = 0
    FREE = 1
    NOMANPAC = 2
    MANPAC = 3
    GHOST = 4

