from defs import *

class Ghost:
    
    def __init__(self, coordinates: CoordinatePair):
        
        self.is_busy: bool = False
        self.is_alive: bool = True

        self.elapsed_ticks = 0

        self._current_position: CoordinatePair = coordinates
        self._path: List[ CoordinatePair ] = None

        self._current_position_last_value = Tiles.SPAWN

    def __repr__(self) -> str:
        return str(self._current_position)
    
    def move(self, position) -> bool:

        if len(self._path) == 0:
            self.is_busy = False

            return None
        else:
            last_position = self._current_position

            self._current_position = self._path.pop(0)
            self.elapsed_ticks += 1
        return last_position, self._current_position_last_value
    
    def set_path(self, path: List[ CoordinatePair ]) -> None:
        self._path = path
        self.elapsed_ticks = 0

    def get_position(self) -> CoordinatePair:
        return self._current_position
    
    def set_position(self, position: CoordinatePair) -> None:
        self._current_position = position
    
    def reset(self) -> None:
        self.elapsed_ticks = 0
        self.is_busy = False

        self._path = None
        


    
    
