"""
Snake Game - Main entry point
Import and run the game from here
"""

import sys
import pygame
from game.core import Game
from utils.settings import Settings

def main():
    # Initialize the game
    settings = Settings()
    game = Game(settings)
    
    # Start the game loop
    game.run()
    
    # Clean exit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
