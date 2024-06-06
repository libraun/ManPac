import math

from defs import *
from ghost import Ghost

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
    
class Game:
    def __init__(self, map_filename: str):
        
        map_loaded = self._load_map(map_filename)
        print(self.__repr__())
        if not map_loaded:
            exit(EXIT_FAILURE)
        valid_path_positions = zip(*np.where(self._map != 0))
        self._edge_dict: Dict[CoordinatePair, NavigableEdge] = {}
        for idx_pair in valid_path_positions:
            print(idx_pair)
            navigable_edge = NavigableEdge(idx_pair)
            self._edge_dict[idx_pair] = navigable_edge

        for key, edge in self._edge_dict.items():
            print(self._map[edge.position[0],edge.position[1]])
            neighbor_coords = self._get_neighbors(edge.position)
            neighbor_edges = [self._edge_dict[pos] for pos in neighbor_coords]
            print(neighbor_coords)
            edge.set_neighbors(neighbor_edges)

        # cell value of 2 = cell where a ghost is allowed but manpac isn't
        ghost_start_indices = list(zip(*np.where(self._map == 2)))

        self._ghosts = [Ghost(i) for i in ghost_start_indices[:MAX_GHOSTS]]
        self._manpac_position = INIT_MANPAC_POSITION

        self.find_path(self._ghosts[0].get_position(),self._manpac_position)

    def process_ai_turn(self) -> None:

        for ghost in self._ghosts:

            pass


    def _load_map(self, filename: str) -> bool:
        
        if not os.path.isfile(filename):
            return False
    
        bitmap = cv2.imread(filename,cv2.IMREAD_GRAYSCALE)
        if bitmap is None:
            return False

        self._map = np.array(bitmap,dtype=int)

        self._map[self._map == 127] = 2
        self._map[self._map == 255] = 1

        return self._map is not None
    
    def __repr__(self) -> str:
        return str(self._map)
    
    def find_path(self, start: CoordinatePair, dest: CoordinatePair) -> None:
        init_edge = self._edge_dict[start]
        print(init_edge)

        open_list: List[NavigableEdge] = [init_edge]
        closed_list: List[NavigableEdge] = []

        while open_list:

            current_cell = open_list.pop(0)
            if current_cell.position == dest:
                print("Found!")
                return self._backtrack(neighbor)
            
            closed_list.append(current_cell)

            neighbors = current_cell.get_neighbors()
            for neighbor in neighbors:
                if neighbor in closed_list:
                    continue
                
                neighbor.set_parent(current_cell)

                neighbor.h_cost = current_cell.h_cost + 1
                neighbor.g_cost = math.dist(neighbor.position, dest)

                neighbor.f_cost = neighbor.h_cost + neighbor.g_cost

                found_node = self._find_node(open_list,neighbor.position)
                if found_node:

                    cmp1 = math.dist(neighbor.position,start)
                    cmp2 = math.dist(neighbor.position, found_node.position)

                    if cmp1 > cmp2:
                        continue
                self._priority_insert(neighbor, open_list)
                print(len(open_list))
    
    def _backtrack(self,n_edge: NavigableEdge) -> List[CoordinatePair]:

        result = []
        next = n_edge
        while next:
            result.append(next.position)
            next = next.get_parent()

            n_edge.reset()
            n_edge = next
                    
    def _find_node(self, search_list: List[NavigableEdge], position: CoordinatePair) -> None | NavigableEdge:
        for edge in search_list:
            if edge.position == position:
                return edge
        return None
    def _priority_insert(self, src: NavigableEdge, dst: List[NavigableEdge]) -> None:
        
        trg_idx = -1
        for idx, edge in enumerate(dst):

            if edge.f_cost > src.f_cost:
                trg_idx = idx
                break
        dst.insert(trg_idx,src)
        
        


                

                    



    def _get_neighbors(self, position: CoordinatePair) -> List[CoordinatePair]:
        neighbors = [
            (position[0] + 1, position[1]), 
            (position[0] - 1, position[1]),
            (position[0], position[1] + 1),
            (position[0], position[1] - 1)
        ]
        neighbors = [n for n in neighbors \
                     if self._map[n[0], n[1]] != 0 ]
        return neighbors





