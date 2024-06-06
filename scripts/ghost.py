from defs import *

class Ghost:
    
    def __init__(self, coordinates: CoordinatePair):
        
        self.is_busy: bool = False
        self.is_alive: bool = True

        self._current_position: CoordinatePair = coordinates
        self._path: List[ CoordinatePair ] = None

    def __repr__(self) -> str:
        return str(self._current_position)
    
    def move(self) -> bool:

        if len(self.path) == 0:
            self.is_busy = False
        else:
            self._current_position = self._path.pop(0)
        return self.is_busy
    
    def set_path(self, path: List[ CoordinatePair ]) -> None:
        self._path = path

    def get_position(self) -> CoordinatePair:
        return self._current_position
        


    
    
