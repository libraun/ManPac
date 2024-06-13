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

        self.reset()

    def reset(self) -> None:
        map_loaded = self._load_map(MAP_FILENAME)
        assert map_loaded, exit(EXIT_CODES.EXIT_FAILURE)
        
        # Keep a copy of playable map for easy reassignment after moves
        self._init_map = np.copy(self._map)
        # cell value of 2 = cell where a ghost is allowed but manpac isn't
        ghost_spawn_coords = list(zip(*np.where(self._map == Tiles.SPAWN)))
        ghost_spawn_coords = [CoordinatePair(i[0],i[1]) for i in ghost_spawn_coords[:MAX_GHOSTS]]
        
        # Initialize list of ghosts, mapping position of ghost to ghost object
        self._ghosts: Sequence[Ghost] = np.array([None for i in range(MAX_GHOSTS)],dtype=Ghost)
        for i, g_spawn_coord in enumerate(ghost_spawn_coords):
            self._map[g_spawn_coord.x,g_spawn_coord.y] = Tiles.GHOST
            self._ghosts[i] = Ghost(g_spawn_coord) 
        
        self._actor_map = np.copy(self._map)

        self.score = 0
        self._edge_dict: Dict[CoordinatePair, NavigableEdge] = {}

        # Create a list of indices that are pathable
        x_set, y_set = np.where(self._map != Tiles.WALL)
        for i in range(len(x_set)):
            valid_coords = CoordinatePair(x_set[i],y_set[i])

            path_tile = NavigableEdge(valid_coords)
            self._edge_dict[valid_coords] = path_tile

        # Set the neighbors of each node for quicker access
        for coords, node in self._edge_dict.items():
            neighbor_coords = self._get_neighbors(coords)
            neighbor_tiles = [self._edge_dict[coords] for coords in neighbor_coords]
            
            node.set_neighbors(neighbor_tiles)

        powerup_spawn_coords = list(zip(*np.where(self._map == Tiles.FREE)))
        for powerup_spawn_coord in random.sample(powerup_spawn_coords, MAX_POWERUPS):
            self._map[powerup_spawn_coord[0], powerup_spawn_coord[1]] = Tiles.POWERUP
        
        point_spawn_coords = list(zip(*np.where(self._map == Tiles.FREE)))
        
        # Multiply number of potential spawn coords by ratio of points to free area
        # to get initial number of points
        number_points = math.floor(len(point_spawn_coords) * POINT_COVERAGE)
        for point_spawn_coord in random.sample(point_spawn_coords, number_points):
            self._map[point_spawn_coord[0], point_spawn_coord[1]] = Tiles.POINT

        self._manpac_position: CoordinatePair = INIT_MANPAC_POSITION 
        self._manpac_direction: CoordinatePair = INIT_MANPAC_DIRECTION # Last ManPac direction
        
        self._invincible_pac: bool = False # Whether or not player is invincible
        self._invincible_ticks: int = 0

        self._actor_map[INIT_MANPAC_POSITION.x,INIT_MANPAC_POSITION.y] = Tiles.MANPAC

        for ghost in self._ghosts:
            init_path = self._find_path(ghost.get_position())
            ghost.set_path(init_path)

    def get_map(self) -> np.ndarray:
        return self._map
    
    def get_manpac_position(self) -> CoordinatePair:
        return self._manpac_position

    '''
        @method play_step()
        @description Main callable method; accepts a direction and first attempts to move player
            in that direction, then processes turn for AI ghosts one by one.

        @return The current running state of the game after the ghost's turn.
    '''     
    def play_step(self, player_move: CoordinatePair, replay: bool=False) -> GameStatus:

        # Update the tick counter if ManPac is invincible
        if self._invincible_pac and self._invincible_ticks < MAX_INVINCIBILITY_TICKS:
            self._invincible_ticks += 1
        # Invincible ticks has exceeded max, make manpac vincible and reset ghost paths
        elif self._invincible_pac:

            self._invincible_pac = False
            self._invincible_ticks = 0

            for ghost in self._ghosts:
                new_path = self._find_path(ghost.get_position())
                ghost.set_path(new_path)

        game_status = self._process_ai_turn()
        
        ghost_positions = set([ghost.get_position() for ghost in self._ghosts])
        
        old_ghost_positions = set([CoordinatePair(coord[0],coord[1]) for coord in zip(*np.where(self._map >= Tiles.GHOST))])
        freed_coords = ghost_positions.difference(old_ghost_positions)

        for position in freed_coords:
            self._map[position.x, position.y] = self._actor_map[position.x,position.y]

        for position in ghost_positions:
            if position == self._manpac_position:
                return GameStatus.GAME_OVER, -10
            #self._update_ghost_coordinates(position)

        if game_status == GameStatus.GAME_OVER:
            return game_status, -10
            
        reward, game_status = self._process_player_turn(player_move)
        return game_status, reward
    

    
    '''
        @method _process_ai_turn()
        @description Processes the next move for each ghost.

        @return The current running state of the game after the ghost's turn.
    '''     
    def _process_ai_turn(self) -> GameStatus:
 
        for ghost in self._ghosts:
            last_pos = ghost.get_position()
            # Player is NOT invincible, find path to it
            if not self._invincible_pac:
                
                new_pos = ghost.move_along_path()
                if last_pos == self._manpac_position:
                    
                    return GameStatus.GAME_OVER
                
                if new_pos == last_pos or not ghost.is_busy:

                    path = self._find_path(last_pos)
                    ghost.set_path(path)
                    
                    new_pos = ghost.move_along_path()
                    self._update_ghost_coordinates(last_pos, new_pos)

                elif new_pos != last_pos:

                    self._update_ghost_coordinates(last_pos, new_pos)

            # manpac is invincible; get furthest position from it and set manaully
            else: 
                new_pos = self._get_panic_move(last_pos)
                if new_pos != last_pos:   
                    ghost.set_position(new_pos)
                    self._update_ghost_coordinates(last_pos,new_pos)

        return GameStatus.GAME_RUNNING
    
    '''
        @method _process_player_turn()
        @description Accepts a direction in which to move the player and attempts to move player,
            returning the game's running status on completion.

        @param "move_vector" A CoordinatePair (int tuple) indicating the direction (NOT position)
            in which to move the player.

        @return The current running state of the game after the player's turn.
    '''     
    def _process_player_turn(self, direction: CoordinatePair | None) -> GameStatus:

        self._manpac_direction = direction if direction else self._manpac_direction
        
        updated_x = self._manpac_position.x + direction.x
        updated_y = self._manpac_position.y + direction.y
        
        grid_value = self._actor_map[updated_x, updated_y]
        position = CoordinatePair(updated_x, updated_y)

        reward = 0
        if grid_value == Tiles.WALL:
            return reward, GameStatus.GAME_RUNNING
            
        elif grid_value >= Tiles.GHOST and self._invincible_pac:
            target_ghost = None
            for ghost in self._ghosts:  
                if ghost.get_position() == position:
                    target_ghost = ghost
                    break

            assert target_ghost != None 
            self._respawn_ghost(target_ghost)
            reward = 10

        elif grid_value >= Tiles.GHOST:
            return -10, GameStatus.GAME_OVER

        elif grid_value == Tiles.POWERUP:
            self._invincible_pac = True
            self._invincible_ticks = 0

            reward = 5

        elif grid_value == Tiles.POINT:
            self._actor_map[updated_x, updated_y] = Tiles.FREE
            reward = 1
        # Update coordinates
        self._map[self._manpac_position.x, self._manpac_position.y] = \
            self._init_map[self._manpac_position.x,self._manpac_position.y]
        self._manpac_position = position

        self._actor_map[position.x, position.y] = Tiles.MANPAC
        return reward, GameStatus.GAME_RUNNING
    
    '''
        @method _get_panic_move()
        @description Gets the neighbors of a coordinates furthest away from pacman

        @param "position" The coordinates to retrieve furthest neighbors from pacman
    '''     
    def _get_panic_move(self, position: CoordinatePair) -> None | CoordinatePair:
       
        moves = self._get_neighbors(position)
        moves = sorted(moves,key=lambda x: math.dist(x,self._manpac_position),reverse=True)
        if not moves:
            return None
        return moves[0] 

    '''
        @method _respawn_ghost()
        @description Respawns and reinitializes the argument ghost.

        @param "ghost" The ghost to be respawned
    '''     
    def _respawn_ghost(self, ghost: Ghost) -> None:
        ghost_spawn_coords = list(zip(*np.where(self._map == Tiles.SPAWN)))
        spawn_coord = random.choice(ghost_spawn_coords)

        ghost.set_position(CoordinatePair(spawn_coord[0],spawn_coord[1]))
        ghost.reset()
    
    def _update_ghost_coordinates(self, last_pos: CoordinatePair, new_pos: CoordinatePair):
        last_cell_value = self._map[last_pos.x,last_pos.y]
        new_cell_value = self._map[new_pos.x, new_pos.y]

        if new_cell_value == Tiles.POINT:
            self._map[new_pos.x, new_pos.y] = Tiles.GHOST_PLUS_POINT
        elif new_cell_value == Tiles.POWERUP:
            self._map[new_pos.x, new_pos.y] = Tiles.GHOST_PLUS_POWERUP
        else:   
            self._map[new_pos.x, new_pos.y] = Tiles.GHOST
        
        if last_cell_value == Tiles.GHOST_PLUS_POINT:
            self._map[last_pos.x, last_pos.y] = Tiles.POINT
        elif last_cell_value == Tiles.GHOST_PLUS_POWERUP:
            self._map[last_pos.x, last_pos.y] = Tiles.POWERUP
        else:
            self._map[last_pos.x, last_pos.y] = self._init_map[last_pos.x, last_pos.y]

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

        # Reassign arbitrary color values
        self._map[self._map == 127] = Tiles.SPAWN
        self._map[self._map == 255] = Tiles.FREE

        return self._map is not None
    
    '''
        @method _find_path()
        @description Uses A* pathfinding algorithm to find a path from point A to point B

        @param "start" A CoordinatePair indicating the initial position.

        @return Calls "_backtrack()" to return a list of CoordinatePairs as path from "start" to ManPac.
    '''     
    def _find_path(self, start: CoordinatePair) -> List[CoordinatePair]:

        init_edge = self._edge_dict[start]

        open_list: List[NavigableEdge] = [init_edge]
        closed_list: List[NavigableEdge] = []
        while open_list:

            current = open_list.pop(0)
            if current.position == self._manpac_position:
                return self._backtrack(current)
            
            closed_list.append(current)
            neighbors: List[NavigableEdge] = [
                n for n in current.get_neighbors() \
                if n not in closed_list]
            
            for neighbor in neighbors:
                temp_g_cost = current.g_cost + 1
                temp_h_cost = math.dist(neighbor.position, self._manpac_position)
                temp_f_cost = temp_g_cost + temp_h_cost
                
                ol_found_node = self._find_node(open_list,neighbor.position)
                if ol_found_node and ol_found_node.f_cost < temp_f_cost:
                    continue

                neighbor.g_cost = temp_g_cost
                neighbor.h_cost = temp_h_cost
                neighbor.f_cost = temp_f_cost

                neighbor.set_parent(current)
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
            result.insert(0,next.position)
            next = next.get_parent()

            n_edge.reset()
            n_edge = next
            
        result.pop(0)
        return result
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
    def _get_adjacent_cells(self, position: CoordinatePair) -> List[CoordinatePair]:

        adjacent_cells = [
            CoordinatePair(position.x + 1, position.y), 
            CoordinatePair(position.x - 1, position.y),
            CoordinatePair(position.x, position.y + 1),
            CoordinatePair(position.x, position.y - 1)
        ]
        adjacent_cells = [(pos, self._actor_map[pos.x,pos.y]) for pos in adjacent_cells \
                          if pos.x > 0 and pos.x < self._map.shape[0] \
                          and pos.y > 0 and pos.y < self._map.shape[1]]
        return adjacent_cells

    def _get_neighbors(self, position: CoordinatePair) -> List[CoordinatePair]:
        adjacent_coords = self._get_adjacent_cells(position)
        neighbors = [n for n, val in adjacent_coords if val != Tiles.WALL]
        return neighbors