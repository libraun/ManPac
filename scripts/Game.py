import math

import cv2
import math
import numpy as np
import random

import heapq

from defs import *
MAX_INVINCIBILITY_TICKS = 25
class Game:

    def __init__(self, max_ghosts: int=4,
                 max_powerups: int=3,
                 coin_coverage: float=0.5):

        self.max_ghosts = max_ghosts
        self.max_powerups = max_powerups

        # The percentage of coins that should (ideally) cover free tiles
        # at the start of the game
        self.coin_coverage = coin_coverage

        bitmap = cv2.imread(MAP_FILENAME,cv2.IMREAD_GRAYSCALE)
        self.init_map = np.array(bitmap,dtype=np.short)

        self.reset()

    def reset(self) -> None:

        self.total_ticks = 1

        self.ticks_since_coin_respawn = 0

        self.map = [[TileObject(True) if val == 0 else TileObject(False) for val in _]
                    for _ in self.init_map]
        
        self.node_data = np.array([[PathNode((x,row)) for x in row]
                               for row in self.map],dtype=PathNode)

        # Keep a copy of playable map for easy reassignment after moves
        # Grab available spawn coordinates
        ghost_spawn_coords = list(zip(*np.where(self.init_map == 127)))
        ghost_spawn_coords = [CoordinatePair(*c) for c in ghost_spawn_coords[:self.max_ghosts]]
        
        # Initialize list of ghosts, mapping position of ghost to ghost object
        self.ghosts = [Ghost(spawn_coord) for spawn_coord in ghost_spawn_coords]
        for spawn_x, spawn_y in ghost_spawn_coords:
            self.map[spawn_x][spawn_y].has_ghost = True

        powerup_spawn_coords = list(zip(*np.where(self.init_map == 255)))
        for x_coord, y_coord in random.sample(powerup_spawn_coords, self.max_powerups):
            self.map[x_coord][y_coord].has_powerup = True
        
        point_spawn_coords = list(zip(*np.where(self.init_map == 255)))
        # Multiply number of potential spawn coords by ratio of points to free area
        # to get initial number of points
        num_coins = math.floor(len(point_spawn_coords) * self.coin_coverage)
        for x_coord, y_coord in random.sample(point_spawn_coords, num_coins):
            if not self.map[x_coord][y_coord].has_powerup:
                self.map[x_coord][y_coord].has_coin = True

        self.manpac_pos = INIT_MANPAC_POSITION 
        self._manpac_direction = INIT_MANPAC_DIRECTION # Last ManPac direction

        self.map[self.manpac_pos.x][self.manpac_pos.y].has_manpac = True
        
        self._invincible_pac: bool = False # Whether or not player is invincible
        self._invincible_ticks: int = 0

        for ghost in self.ghosts:
            ghost.path = self._find_path(ghost.position)
    
    def get_manpac_position(self) -> CoordinatePair:
        return self.manpac_pos

    '''
        @method play_step()
        @description Main callable method; accepts a direction and first attempts to move player
            in that direction, then processes turn for AI ghosts one by one.

        @return The current running state of the game after the ghost's turn.
    '''     
    def play_step(self, player_move: CoordinatePair) -> GameStatus:

        self.ticks_since_coin_respawn += 1
        self.total_ticks += 1

        if self.ticks_since_coin_respawn >= 8:

            self.ticks_since_coin_respawn = 0
            coin_spawn_coords = list(zip(*np.where(self.init_map == 255)))
            random.shuffle(coin_spawn_coords)
            for x_coord, y_coord in coin_spawn_coords:
                if not self.map[x_coord][y_coord].has_coin and not self.map[x_coord][y_coord].has_powerup:
                    self.map[x_coord][y_coord].has_coin = True
                    break

        # Update the tick counter if ManPac is invincible
        if self._invincible_pac and self._invincible_ticks < MAX_INVINCIBILITY_TICKS:
            self._invincible_ticks += 1
        # Invincible ticks has exceeded max, make manpac vincible and reset ghost paths
        elif self._invincible_pac:

            self._invincible_pac = False
            self._invincible_ticks = 0

            for ghost in self.ghosts:
                ghost.path = self._find_path(ghost.position)
            

        game_status = self._process_ai_turn()
        if game_status == GameStatus.GAME_OVER:
            return GameStatus.GAME_OVER, -1000 + self.total_ticks
        
        game_status, reward = self._process_player_turn(player_move)

        return game_status, reward
    

    
    '''
        @method _process_ai_turn()
        @description Processes the next move for each ghost.

        @return The current running state of the game after the ghost's turn.
    '''     
    def _process_ai_turn(self) -> GameStatus:
 
        for ghost in self.ghosts:
            last_pos = ghost.position
            # Player is NOT invincible, find path to it
            if not self._invincible_pac:
                
                new_pos = ghost.move_along_path()
                if last_pos == self.manpac_pos:
                    
                    return GameStatus.GAME_OVER
                elif new_pos == last_pos or not ghost.is_busy:

                    if math.dist(new_pos, self.manpac_pos) < 1.5:
                        moves = self._get_neighbors(new_pos.x,new_pos.y)
                        moves = sorted(moves, key=lambda x: math.dist(x,self.manpac_pos))
                        if not moves:
                            continue
                        new_pos = moves[0]
                        ghost.set_position(new_pos)
                    else:
        
                        ghost.path = self._find_path(last_pos)
                        new_pos = ghost.move_along_path()

                self.map[last_pos.x][ last_pos.y].has_ghost = False
                self.map[new_pos.x][new_pos.y].has_ghost = True

            # manpac is invincible; get furthest position from it and set manaully
            else: 
                new_pos = self._get_panic_move(last_pos)
                if new_pos and new_pos != last_pos:   
                    ghost.set_position(new_pos)
    
                    self.map[last_pos.x] [last_pos.y].has_ghost = False
    
                    if self.map[new_pos.x][new_pos.y].has_manpac:
                        self._respawn_ghost(ghost)
                    else:
                        self.map[new_pos.x] [new_pos.y].has_ghost = True

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
        
        updated_x = self.manpac_pos.x + direction.x
        updated_y = self.manpac_pos.y + direction.y
        
        grid_value = self.map[updated_x][updated_y]
        position = CoordinatePair(updated_x, updated_y)

        reward = 0
        # Player has struck a wall; nothing happens.
        if grid_value.is_wall is True:
            return GameStatus.GAME_RUNNING, 0
            
        # Player is invincible and has struck a ghost; kills ghost.
        if grid_value.has_ghost and self._invincible_pac:
            target_ghost = None
            for ghost in self.ghosts:  
                if ghost.position == position:
                    target_ghost = ghost
                    break

            assert target_ghost != None 
            self._respawn_ghost(target_ghost)
            reward = 5

        # Player is NOT invincible and has struck a ghost; return gameover
        elif grid_value.has_ghost:
            return GameStatus.GAME_OVER, -1000 + self.total_ticks

        elif grid_value.has_powerup:
            self._invincible_pac = True
            self._invincible_ticks = 0

            reward = 5

        elif grid_value.has_coin:
            self.map[updated_x][updated_y].has_coin = False
            reward = 1
        # Update coordinates, removing ManPac from last position and setting him to new position
        self.map[self.manpac_pos.x][self.manpac_pos.y].has_manpac = False
        self.manpac_pos = position

        self.map[position.x][position.y].has_manpac = True
        return GameStatus.GAME_RUNNING, reward
    
    '''
        @method _get_panic_move()
        @description Gets the neighbors of a coordinates furthest away from pacman

        @param "position" The coordinates to retrieve furthest neighbors from pacman
    '''     
    def _get_panic_move(self, position: CoordinatePair) -> None | CoordinatePair:
       
        moves = self._get_neighbors(position.x, position.y)
        # Sort 
        moves = sorted(moves, key=lambda x: math.dist(x, self.manpac_pos),
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
        ghost_spawn_coords = list(zip(*np.where(self.init_map == 127)))
        spawn_coord = random.choice(ghost_spawn_coords)
        
        ghost.set_position(CoordinatePair(*spawn_coord))
        ghost.reset()
    
    '''
        @method _find_path()
        @description Uses A* pathfinding algorithm to find a path from point A to point B

        @param "start" A CoordinatePair indicating the initial position.

        @return Calls "_backtrack()" to return a list of CoordinatePairs as path from "start" to ManPac.
    '''   
    ## TODO: Reimplement using dynamic programming  
    def _find_path(self, start: CoordinatePair) -> List[CoordinatePair]:

        closed_list = np.array([[False for _ in row] 
                                for row in self.map],
                                dtype=bool)
        
        for node in self.node_data.flatten():
            node.reset()

        open_list = []

        self.node_data[start.x, start.y].f_cost = 0.
        self.node_data[start.x,start.y].g_cost = 0.
        self.node_data[start.x, start.y].h_cost = 0.

        
        heapq.heappush(open_list, (float('inf'), start.x, start.y))
        while open_list:

            _, current_x, current_y = heapq.heappop(open_list)
            closed_list[current_x, current_y] = True

            neighbors = self._get_neighbors(current_x, current_y)
            
            for neighbor_pos in neighbors:

                if closed_list[neighbor_pos.x, neighbor_pos.y] is True:
                    continue

                if neighbor_pos == self.manpac_pos:


                    self.node_data[neighbor_pos.x, neighbor_pos.y].parent_x = current_x
                    self.node_data[neighbor_pos.x, neighbor_pos.y].parent_y = current_y

                    return self._backtrack(self.node_data[neighbor_pos.x,neighbor_pos.y],start)
             
                
                temp_g_cost = self.node_data[neighbor_pos.x, neighbor_pos.y].g_cost + 1.0
                temp_h_cost = math.dist(neighbor_pos,self.manpac_pos)
                temp_f_cost = temp_g_cost + temp_h_cost
                
                open_list_equivalent_cost = self.node_data[neighbor_pos.x,neighbor_pos.y].f_cost


                if open_list_equivalent_cost == float('inf') or open_list_equivalent_cost > temp_f_cost:
                    heapq.heappush(open_list, (temp_f_cost, neighbor_pos.x, neighbor_pos.y))
                    
                    self.node_data[neighbor_pos.x, neighbor_pos.y].g_cost = temp_g_cost
                    self.node_data[neighbor_pos.x, neighbor_pos.y].h_cost = temp_h_cost
                    self.node_data[neighbor_pos.x, neighbor_pos.y].f_cost = temp_f_cost

                    self.node_data[neighbor_pos.x, neighbor_pos.y].parent_x = current_x
                    self.node_data[neighbor_pos.x, neighbor_pos.y].parent_y = current_y

                


    
    '''
        @method _backtrack()
        @description Iterates through the parent nodes of a PathNode until None is found.

        @param "n_edge" A PathNode (passed at the end of "_find_path()")

        @return A list of every position along "n_edge" path
    '''     
    def _backtrack(self, n_edge, start) -> List[CoordinatePair]:
        result = []
        next = n_edge
        
        while CoordinatePair(next.parent_x,next.parent_y) != start:
            
            result.append(CoordinatePair(next.parent_x, next.parent_y))
            n_edge = self.node_data[next.parent_x, next.parent_y]
            next.reset()
            next = n_edge

            

        result.reverse()
        return result


    '''
        @method _get_neighbors()
        @description Gets a list of adjacent neighbors to a position.

        @param "position" The CoordinatePair (int tuple) whose adjacent neighbors will be retrieved

        @return A list of valid neighbors for "position"
    '''     
    def _get_neighbors(self, x: int, y: int) -> Tuple[CoordinatePair]:

        neighbor_cells = (
            CoordinatePair(x + 1, y), 
            CoordinatePair(x - 1, y),
            CoordinatePair(x, y + 1),
            CoordinatePair(x, y - 1)
        )
        neighbor_cells = tuple([p for p in neighbor_cells 
                          if (p.x >= 0 and p.x < len(self.map)) \
                          and (p.y >= 0 and p.y < len(self.map[0]) )
                          and not self.map[p.x][p.y].is_wall and not self.map[p.x][p.y].has_ghost])
        return neighbor_cells