#!/usr/bin/env python3
"""
NOTLIFE - Cyberpunk Survival Shooter
Dark, atmospheric bullet hell with rogue-like elements
"""

import sys
import os
import pygame
from game.core.game import NotLifeGame

def main():
    try:
        # Add the game directory to the path
        game_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, game_dir)
        
        # Initialize and run the game
        game = NotLifeGame()
        game.run()
        
    except Exception as e:
        print(f"Error starting the game: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
