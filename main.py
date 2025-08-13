"""
Snake Game - Main entry point
A modern, modular implementation of the classic Snake game with enhanced visuals
"""

import sys
import pygame
from game.core import Game
from utils.settings import Settings

def main():
    # Initialize pygame
    pygame.init()
    
    # Initialize settings
    settings = Settings()
    
    # Create and run the game
    game = Game(settings)
    game.run()
    
    # Clean exit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 