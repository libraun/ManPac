import math

import os
import os.path 
import cv2
import math
import numpy as np
import random

import heapq

from defs import *
from ghost import Ghost
from path_node import PathNode  

import time

## TODO: Make ManPac his own class.

## TODO: rewrite all this code so it isnt hanging together by patch tape and bits of string
class Game:
    def __init__(self):

        self.reset()

    def reset(self) -> None:
        map_loaded = self._load_ghost_layer(MAP_FILENAME)
        assert map_loaded, exit(EXIT_CODES.EXIT_FAILURE)
        
        # Keep a copy of playable map for easy reassignment after moves
        self._default_layer = np.copy(self._ghost_layer)
        # Grab available spawn coordinates
        ghost_spawn_coords = list(zip(*np.where(self._ghost_layer == Tiles.SPAWN)))
        ghost_spawn_coords = [CoordinatePair(i[0], i[1]) for i in ghost_spawn_coords[:MAX_GHOSTS]]
        
        # Initialize list of ghosts, mapping position of ghost to ghost object
        self._ghosts: Sequence[Ghost] = np.array([None for i in range(MAX_GHOSTS)],dtype=Ghost)
        for i, g_spawn_coord in enumerate(ghost_spawn_coords):
            self._ghost_layer[g_spawn_coord.x,g_spawn_coord.y] = Tiles.GHOST
            self._ghosts[i] = Ghost(g_spawn_coord) 
        
        self._object_layer = np.copy(self._ghost_layer)

        self.score = 0

        # Set the neighbors of each node for quicker access
       # for coords, node in self._edge_dict.items():
         #   neighbor_coords = self._get_neighbors(coords)
        #    neighbor_tiles = tuple([self._edge_dict[coords] for coords in neighbor_coords])
         #   node.set_neighbors(neighbor_tiles)

        powerup_spawn_coords = list(zip(*np.where(self._ghost_layer == Tiles.FREE)))
        for powerup_spawn_coord in random.sample(powerup_spawn_coords, MAX_POWERUPS):
            self._ghost_layer[powerup_spawn_coord[0], powerup_spawn_coord[1]] = Tiles.POWERUP
        
        point_spawn_coords = list(zip(*np.where(self._ghost_layer == Tiles.FREE)))
        
        # Multiply number of potential spawn coords by ratio of points to free area
        # to get initial number of points
        number_points = math.floor(len(point_spawn_coords) * POINT_COVERAGE)
        for point_spawn_coord in random.sample(point_spawn_coords, number_points):
            self._ghost_layer[point_spawn_coord[0], point_spawn_coord[1]] = Tiles.POINT

        self._manpac_position: CoordinatePair = INIT_MANPAC_POSITION 
        self._manpac_direction: CoordinatePair = INIT_MANPAC_DIRECTION # Last ManPac direction
        
        self._invincible_pac: bool = False # Whether or not player is invincible
        self._invincible_ticks: int = 0

        self._object_layer[INIT_MANPAC_POSITION.x,INIT_MANPAC_POSITION.y] = Tiles.MANPAC

        for ghost in self._ghosts:
            init_path = self._find_path(ghost.get_position())
            ghost.set_path(init_path)

    def get_map(self) -> np.ndarray:
        return self._ghost_layer
    
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
        if game_status == GameStatus.GAME_OVER:
            return GameStatus.GAME_OVER, -10
        
        ghost_positions = set([ghost.get_position() for ghost in self._ghosts])
        
        old_ghost_positions = set([CoordinatePair(coord[0],coord[1]) for coord in zip(*np.where(self._ghost_layer >= Tiles.GHOST))])
        freed_coords = ghost_positions.difference(old_ghost_positions)

        for position in freed_coords:
            self._ghost_layer[position.x, position.y] = self._object_layer[position.x,position.y]

        for position in ghost_positions:
            if position == self._manpac_position:
                return GameStatus.GAME_OVER, -10
            #self._update_ghost_coordinates(position)

        if game_status == GameStatus.GAME_OVER:
            return game_status, -10
        
        reward, game_status = self._process_player_turn(player_move)
        if reward > 0:
            self.score += reward

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

                    if math.dist(new_pos, self._manpac_position) < 1.5:
                        moves = self._get_neighbors(new_pos.x,new_pos.y)
                        moves = sorted(moves, key=lambda x: math.dist(x,self._manpac_position))

                        new_pos = moves[0]
                        ghost.set_position(new_pos)
                    else:
                        start = time.time()
                        path = self._find_path(last_pos)
                    
                    
                        ghost.set_path(path)
                        end = time.time()
                        elapsed_time = end - start
                    
                        
                        print(elapsed_time)
                        new_pos = ghost.move_along_path()

                    self._update_ghost_coordinates(last_pos, new_pos)

                else:

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

        ## TODO: Adjust ManPac's direction to be more... manpac-ey
        self._manpac_direction = direction if direction else self._manpac_direction
        
        updated_x = self._manpac_position.x + direction.x
        updated_y = self._manpac_position.y + direction.y
        
        grid_value = self._ghost_layer[updated_x, updated_y]
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
            self._default_layer[updated_x, updated_y] = Tiles.FREE
            reward = 1
        # Update coordinates
        self._object_layer[self._manpac_position.x, self._manpac_position.y] = \
            self._default_layer[self._manpac_position.x,self._manpac_position.y]
        self._ghost_layer[self._manpac_position.x, self._manpac_position.y] = \
            self._default_layer[self._manpac_position.x,self._manpac_position.y]
        self._manpac_position = position

        self._object_layer[position.x, position.y] = Tiles.MANPAC
        return reward, GameStatus.GAME_RUNNING
    
    '''
        @method _get_panic_move()
        @description Gets the neighbors of a coordinates furthest away from pacman

        @param "position" The coordinates to retrieve furthest neighbors from pacman
    '''     
    def _get_panic_move(self, position: CoordinatePair) -> None | CoordinatePair:
       
        moves = self._get_neighbors(position.x, position.y)
        moves = sorted(moves,
                       key=lambda x: math.dist(x,self._manpac_position),
                       reverse=True)
        if not moves:
            return None
        return moves[0] 

    '''
        @method _respawn_ghost()
        @description Respawns and reinitializes the argument ghost.

        @param "ghost" The ghost to be respawned
    '''     
    def _respawn_ghost(self, ghost: Ghost) -> None:
        ghost_spawn_coords = list(zip(*np.where(self._ghost_layer == Tiles.SPAWN)))
        spawn_coord = random.choice(ghost_spawn_coords)

        ghost.set_position(CoordinatePair(spawn_coord[0],spawn_coord[1]))
        ghost.reset()
    

    ## TODO: Rewrite this to use new 
    def _update_ghost_coordinates(self, last_pos: CoordinatePair, new_pos: CoordinatePair):
        last_cell_value = self._ghost_layer[last_pos.x,last_pos.y]
        new_cell_value = self._ghost_layer[new_pos.x, new_pos.y]

        if new_cell_value == Tiles.POINT:
            self._ghost_layer[new_pos.x, new_pos.y] = Tiles.GHOST_PLUS_POINT
        elif new_cell_value == Tiles.POWERUP:
            self._ghost_layer[new_pos.x, new_pos.y] = Tiles.GHOST_PLUS_POWERUP
        else:   
            self._ghost_layer[new_pos.x, new_pos.y] = Tiles.GHOST
        
        if last_cell_value == Tiles.GHOST_PLUS_POINT:
            self._ghost_layer[last_pos.x, last_pos.y] = Tiles.POINT
        elif last_cell_value == Tiles.GHOST_PLUS_POWERUP:
            self._ghost_layer[last_pos.x, last_pos.y] = Tiles.POWERUP
        else:
            self._ghost_layer[last_pos.x, last_pos.y] = self._default_layer[last_pos.x, last_pos.y]

    '''
        @method _load_ghost_layer()
        @description Loads a numpy array as the game map from an image file.

        @param "filename" The name or path of the image file to use as a map.

        @return True if map loaded successfully else False.
    '''    
    def _load_ghost_layer(self, filename: str) -> bool:
        
        if not os.path.isfile(filename):
            return False
    
        bitmap = cv2.imread(filename,cv2.IMREAD_GRAYSCALE)
        if bitmap is None:
            return False

        self._ghost_layer = np.array(bitmap,dtype=int)

        # Reassign arbitrary color values
        self._ghost_layer[self._ghost_layer == 127] = Tiles.SPAWN
        self._ghost_layer[self._ghost_layer == 255] = Tiles.FREE

        return self._ghost_layer is not None
    
    '''
        @method _find_path()
        @description Uses A* pathfinding algorithm to find a path from point A to point B

        @param "start" A CoordinatePair indicating the initial position.

        @return Calls "_backtrack()" to return a list of CoordinatePairs as path from "start" to ManPac.
    '''   
    ## TODO: Reimplement using dynamic programming  
    def _find_path(self, start: CoordinatePair) -> List[CoordinatePair]:

        node_data = np.array([[PathNode() for _ in row]
                               for row in self._ghost_layer],
                               dtype=PathNode)
        closed_list = np.array([[False for _ in row] 
                                for row in self._ghost_layer],
                                dtype=bool)
        open_list = []

        node_data[start.x, start.y].f_cost = 0
        node_data[start.x,start.y].g_cost = 0
        node_data[start.x, start.y].h_cost = 0
        
        heapq.heappush(open_list, (float('inf'), start.x, start.y))
        while open_list:

            _, current_x, current_y = heapq.heappop(open_list)
            closed_list[current_x, current_y] = True

            neighbors = self._get_neighbors(current_x, current_y)
            
            for neighbor_pos in neighbors:

                if closed_list[neighbor_pos.x, neighbor_pos.y] is True:
                    continue

                elif neighbor_pos == self._manpac_position:

                    node_data[neighbor_pos.x, neighbor_pos.y].parent_x = current_x
                    node_data[neighbor_pos.x, neighbor_pos.y].parent_y = current_y

                    return self._backtrack(node_data[neighbor_pos.x,neighbor_pos.y],start,node_data)
             
                
                temp_g_cost = node_data[neighbor_pos.x, neighbor_pos.y].g_cost + 1.0
                temp_h_cost = math.dist(neighbor_pos,self._manpac_position)
                temp_f_cost = temp_g_cost + temp_h_cost
                
                open_list_equivalent_cost = node_data[neighbor_pos.x,neighbor_pos.y].f_cost

                if open_list_equivalent_cost == float('inf') or open_list_equivalent_cost > temp_f_cost:
                    
                    heapq.heappush(open_list, (temp_f_cost, neighbor_pos.x, neighbor_pos.y))
                    
                    node_data[neighbor_pos.x, neighbor_pos.y].g_cost = temp_g_cost
                    node_data[neighbor_pos.x, neighbor_pos.y].h_cost = temp_h_cost
                    node_data[neighbor_pos.x, neighbor_pos.y].f_cost = temp_f_cost

                    node_data[neighbor_pos.x, neighbor_pos.y].parent_x = current_x
                    node_data[neighbor_pos.x, neighbor_pos.y].parent_y = current_y

                


    
    '''
        @method _backtrack()
        @description Iterates through the parent nodes of a PathNode until None is found.

        @param "n_edge" A PathNode (passed at the end of "_find_path()")

        @return A list of every position along "n_edge" path
    '''     
    def _backtrack(self, n_edge, start, node_data) -> List[CoordinatePair]:
        result = []
        next = n_edge
        
        while CoordinatePair(next.parent_x,next.parent_y) != start:
            
            result.append(CoordinatePair(next.parent_x, next.parent_y))
            next = node_data[next.parent_x, next.parent_y]
            
            n_edge = next
        result.reverse()
        return result
    '''
        @method _find_node()
        @description Finds a node with position "position" in an ordered list

        @param "search_list" A list of PathNodes on which search is performed
        @param "position" A CoordinatePair (int tuple) that will be searched for in "search_list"

        @return The PathNode whose position is "position" if found, else none.
    '''       
    def _find_node(self, search_list: List[PathNode], position: CoordinatePair) -> None | PathNode:
        for edge in search_list:
            if edge.position == position:
                return edge
        return None
    
    '''
        @method _priority_insert()
        @description Inserts a PathNode node into a list based on its f_cost

        @param "src" The PathNode node to insert
        @param "dst" The list in which to insert "src"
    '''     
    def _priority_insert(self, dst: List[PathNode], src: PathNode) -> None:
        
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
    def _get_adjacent_cells(self, x: int, y: int) -> Tuple[CoordinatePair]:

        adjacent_cells = [
            CoordinatePair(x + 1, y), 
            CoordinatePair(x - 1, y),
            CoordinatePair(x, y + 1),
            CoordinatePair(x, y - 1)
        ]
        adjacent_cells = tuple([(pos, self._ghost_layer[pos.x,pos.y]) for pos in adjacent_cells \
                          if pos.x >= 0 and pos.x < self._ghost_layer.shape[0] \
                          and pos.y >= 0 and pos.y < self._ghost_layer.shape[1]])
        return adjacent_cells

    def _get_neighbors(self, x: int, y: int) -> List[CoordinatePair]:
        adjacent_coords = self._get_adjacent_cells(x,y)
        neighbors = (n for n, val in adjacent_coords if val != Tiles.WALL)
        return neighbors