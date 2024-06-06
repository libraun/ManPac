from Game import Game
from defs import EXIT_FAILURE, EXIT_SUCCESS

if __name__ == "__main__":

    env = Game()

    result = env.play_step((1, 0))

    # Check if game is running
    print(result)

    exit(EXIT_SUCCESS)
