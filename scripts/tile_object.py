from defs import *

class TileObject:
    def __init__(self, is_wall: bool=False,
                 has_coin: bool=False,
                 has_powerup: bool=False):

        self.is_wall: bool = is_wall

        self.has_manpac: bool = False
        self.has_ghost: bool = False

        self.has_coin: bool = has_coin
        self.has_powerup: bool = has_powerup

    def get_repr(self) -> Tuple[bool]:

        return (
            self.is_wall,
            self.has_manpac,
            self.has_ghost,
            self.has_coin,
            self.has_powerup,        
        )
    