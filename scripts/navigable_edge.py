class NavigableEdge:
    def __init__(self,idx_pair, neighbors=None):
        
        self.position = idx_pair
        
        self.g_cost = 0.0
        self.h_cost = 0.0
        self.f_cost = 0.0

        self._neighbors = neighbors
        self._parent = None

    def get_neighbors(self) -> list:

        return self._neighbors

    def set_neighbors(self, neighbors: list) -> None:
        
        self._neighbors = neighbors

    def get_parent(self):
        return self._parent

    def set_parent(self, parent) -> None:
        self._parent = parent
    
    def reset(self) -> None:
        self.g_cost = 0.0
        self.h_cost = 0.0
        self.f_cost = 0.0

        self._parent = None
    