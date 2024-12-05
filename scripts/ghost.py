from defs import *
from typing import List

class Ghost:
    
    # Coordinates: A tuple of positive integers representing the ghost's initial
    # location on the grid.
    def __init__(self, coordinates: Tuple[int]):
        
        # Records whether or not this ghost is active (it should always be)
        self.is_busy: bool = True
        self.is_alive: bool = True

        # Can be used to reset a ghosts path (or monitor how long it's been on a path)
        self.elapsed_ticks: int = 0
        
        self.position: Tuple[int] = coordinates
        self.path: List[ CoordinatePair ] = []

    def peek(self) -> None | Tuple[int]:
        
        return None if not self.path else self.path[0]

    def move_along_path(self) -> Tuple[int]:
        
        # If path is empty (or ghost has been following the same path for too long), 
        # reset this ghost's path.
        if not self.path or self.elapsed_ticks > 25:
            self.reset()
        # Else, set this ghost's new position to the coordinates at the top of their path.
        else:
            self.position = self.path.pop(0)
            self.elapsed_ticks += 1
        return self.position
    
    # Can be used to manually change the ghost's position, 
    # instead of having it follow its current path to the player
    def set_position(self, position: Tuple[int]) -> None:
        self.elapsed_ticks = 0
        self.position = position
    
    def reset(self) -> None:

        self.elapsed_ticks = 0
        self.is_busy = False

        self.path.clear()
        


    
    
