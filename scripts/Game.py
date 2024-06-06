import math

import os
import os.path 
import cv2
import math
import numpy as np
import random

from defs import *
from ghost import Ghost
from navigable_edge import NavigableEdge    
    
class Game:
    def __init__(self):
        
        map_loaded = self._load_map(MAP_FILENAME)
        if not map_loaded:
            exit(EXIT_FAILURE)

        self._score = 0

        self._edge_dict: Dict[CoordinatePair, NavigableEdge] = {}

        # Create a list of indices that are pathable
        valid_indices = zip(*np.where(self._map != Tiles.WALL))
        for idx_pair in valid_indices:
            navigable_edge = NavigableEdge(idx_pair)
            self._edge_dict[idx_pair] = navigable_edge

        # Set the neighbors of each node for quicker access
        for position, node in self._edge_dict.items():
            neighbor_coords = self._get_neighbors(position)
            neighbor_edges = [self._edge_dict[pos] for pos in neighbor_coords]
            
            node.set_neighbors(neighbor_edges)

        # cell value of 2 = cell where a ghost is allowed but manpac isn't
        ghost_start_indices = list(zip(*np.where(self._map == Tiles.SPAWN)))

        # Initialize dict of ghosts, mapping position of ghost to ghost object
        self._ghosts: Dict[CoordinatePair, Ghost] = { \
            i : Ghost(i) for i in ghost_start_indices[:MAX_GHOSTS] \
        }
    
        self._manpac_position = INIT_MANPAC_POSITION
        self._manpac_direction = INIT_MANPAC_DIRECTION

    '''
        @method play_step()
        @description Main callable method; accepts a direction and first attempts to move player
            in that direction, then processes turn for AI ghosts one by one.

        @return The current running state of the game after the ghost's turn.
    '''     
    def play_step(self, move_vector: CoordinatePair) -> GameStatus:

        game_status = self._process_player_turn(move_vector=move_vector)
        if game_status == False:
            return False
        
        game_status = self._process_ai_turn()

        if game_status == GameStatus.GAME_OVER:
            self.__init__()
        return game_status
    
    '''
        @method _process_ai_turn()
        @description Processes the next move for each ghost.

        @return The current running state of the game after the ghost's turn.
    '''     
    def _process_ai_turn(self) -> GameStatus:

        for ghost in self._ghosts:
            ghost_position = ghost.get_position()
            if ghost_position == self._manpac_position:
                
                self.__init__()
                return GameStatus.GAME_OVER
            elif not ghost.is_busy or ghost.elapsed_ticks > 10:
                path = self._find_path(ghost_position, self._manpac_position)
                ghost.set_path(path)
            new_pos,last_pos,last_value = ghost.move()   
            if new_pos:
                self._map[last_pos[0], last_pos[1]] = last_value
                self._map[new_pos[0], new_pos[1]] = Tiles.GHOST 
        return GameStatus.GAME_RUNNING
    
    '''
        @method _process_player_turn()
        @description Accepts a direction in which to move the player and attempts to move player,
            returning the game's running status on completion.

        @param "move_vector" A CoordinatePair (int tuple) indicating the direction (NOT position)
            in which to move the player.

        @return The current running state of the game after the player's turn.
    '''     
    def _process_player_turn(self,move_vector: CoordinatePair | None) -> GameStatus:

        move_vector = move_vector or self._manpac_direction

        result = GameStatus.GAME_RUNNING

        updated_x = self._manpac_position[0] + move_vector[0]
        updated_y = self._manpac_position[1] + move_vector[1]

        self._manpac_direction = move_vector

        grid_value = self._map[updated_x, updated_y]
        if grid_value == Tiles.FREE:

            self._manpac_position = (updated_x, updated_y)

        elif grid_value == Tiles.GHOST and self._invincible_pac:

            target_position = (updated_x, updated_y)
            target_ghost = self._ghosts[target_position]

            self._manpac_position = target_position

            self._respawn_ghost(target_ghost)
            self._score += 10
        elif grid_value == Tiles.GHOST:

            result = GameStatus.GAME_OVER

        elif grid_value == Tiles.POWERUP:
            self._invincible_pac = True
        
        return result
    '''
        @method _respawn_ghost()
        @description Respawns and reinitializes the argument ghost.

        @param "ghost" The ghost to be respawned
    '''     
    def _respawn_ghost(self, ghost: Ghost) -> None:
        ghost_start_indices = list(zip(*np.where(self._map == Tiles.SPAWN)))
        random_spawn_point = random.choice(ghost_start_indices)

        ghost.set_position(random_spawn_point)
        ghost.reset()

    '''
        @method _load_map()
        @description Loads a numpy array as the game map from an image file.

        @param "filename" The name or path of the image file to use as a map.

        @return True if map loaded successfully else False.
    '''    
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
    
    '''
        @method _find_path()
        @description Uses A* pathfinding algorithm to find a path from point A to point B

        @param "start" A CoordinatePair indicating the initial position.
        @param "dest" A CoordinatePair that is the point to which a path is drawn.

        @return Calls "_backtrack()" to return a list of CoordinatePairs as path from "start" to "dest".
    '''     
    def _find_path(self, start: CoordinatePair, dest: CoordinatePair) -> None:
        
        init_edge = self._edge_dict[start]

        open_list: List[NavigableEdge] = [init_edge]
        closed_list: List[NavigableEdge] = []

        while open_list:

            current_cell = open_list.pop(0)
            if current_cell.position == dest:
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
    
    '''
        @method _backtrack()
        @description Iterates through the parent nodes of a NavigableEdge until None is found.

        @param "n_edge" A NavigableEdge (passed at the end of "_find_path()")

        @return A list of every position along "n_edge" path
    '''     
    def _backtrack(self,n_edge: NavigableEdge) -> List[CoordinatePair]:

        result = []
        next = n_edge
        while next:
            result.append(next.position)
            next = next.get_parent()

            n_edge.reset()
            n_edge = next
    '''
        @method _find_node()
        @description Finds a node with position "position" in an ordered list

        @param "search_list" A list of NavigableEdges on which search is performed
        @param "position" A CoordinatePair (int tuple) that will be searched for in "search_list"

        @return The NavigableEdge whose position is "position" if found, else none.
    '''       
    def _find_node(self, search_list: List[NavigableEdge], position: CoordinatePair) -> None | NavigableEdge:
        
        for edge in search_list:
            if edge.position == position:
                return edge
        return None
    
    '''
        @method _priority_insert()
        @description Inserts a NavigableEdge node into a list based on its f_cost

        @param "src" The NavigableEdge node to insert
        @param "dst" The list in which to insert "src"
    '''     
    def _priority_insert(self, src: NavigableEdge, dst: List[NavigableEdge]) -> None:
        
        # Insert dst at the last position if it has the highest f_cost
        trg_idx = -1
        for idx, edge in enumerate(dst):
            if edge.f_cost > src.f_cost:
                trg_idx = idx
                break
        dst.insert(trg_idx,src)

    '''
        @method _get_neighbors()
        @description Gets a list of adjacent neighbors to a position.

        @param "position" The CoordinatePair (int tuple) whose adjacent neighbors will be retrieved

        @return A list of valid neighbors for "position"
    '''     
    def _get_neighbors(self, position: CoordinatePair) -> List[CoordinatePair]:
        neighbors = [
            (position[0] + 1, position[1]), 
            (position[0] - 1, position[1]),
            (position[0], position[1] + 1),
            (position[0], position[1] - 1)
        ]
        neighbors = [n for n in neighbors \
                     if n[0] > 0 and n[0] < self._map.shape[0]\
                     and n[1] > 0 and n[1] <  self._map.shape[1] 
                     and self._map[n[0], n[1]] != Tiles.WALL]
        return neighbors





