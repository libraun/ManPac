import unittest
import itertools

import random

from game import Game
from defs import DIRECTIONS

class MapTest(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def tearDown(self):
        self.game.reset()

    def test_character_counts(self):
        for _ in range(10000):
            game_over = False
            while not game_over:
                
                manpac_count = 0
                ghost_count = 0
                for cell in itertools.chain(*self.game.map):
                    if cell.has_manpac:
                        manpac_count += 1
                    elif cell.has_ghost:
                        ghost_count += 1

                self.assertEqual(manpac_count, 1)
                self.assertLessEqual(ghost_count, self.game.max_ghosts)
                
                game_over, _ = self.game.play_step(random.choice(DIRECTIONS)) 

    def test_character_counts(self):
        for _ in range(10000):
            game_over = False
            while not game_over:
                
                manpac_count = 0
                ghost_count = 0
                for cell in itertools.chain(*self.game.map):
                    if cell.has_manpac:
                        manpac_count += 1
                    elif cell.has_ghost:
                        ghost_count += 1

                self.assertEqual(manpac_count, 1)
                self.assertLessEqual(ghost_count, self.game.max_ghosts)
                
                game_over, _ = self.game.play_step(random.choice(DIRECTIONS)) 

if __name__ == "__main__":

    unittest.main()