from defs import *

class Ghost:
    
    def __init__(self, coordinates: CoordinatePair):
        
        self.is_busy: bool = True
        self.is_alive: bool = True

        self.elapsed_ticks = 0

        self._current_position: CoordinatePair = coordinates
        self._path: List[ CoordinatePair ] = []

    def __repr__(self) -> str:
        return str(self._current_position)
    
    def move_along_path(self) -> None | CoordinatePair:
        
        self.is_busy = self._path and self.elapsed_ticks <= 25
        
        if not self.is_busy:
            return self._current_position

        self._current_position = self._path.pop(0)

        self.elapsed_ticks += 1
        return self._current_position
    
    def set_path(self, path: List[ CoordinatePair ]) -> None:
        
        self.is_busy = True
        self.elapsed_ticks = 0

        self._path = path

    def get_position(self) -> CoordinatePair:

        return self._current_position
    
    def set_position(self, position: CoordinatePair) -> None:
        
        self._current_position = position
    
    def reset(self) -> None:

        self.elapsed_ticks = 0
        self.is_busy = False

        self._path = []
        


    
    
