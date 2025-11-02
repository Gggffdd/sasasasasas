"""
Game state management
"""

import pygame
from enum import Enum, auto
from typing import Dict, Any, Optional

class GameState(Enum):
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    UPGRADE_SELECT = auto()
    WAVE_TRANSITION = auto()

class StateManager:
    """Manages game states and transitions"""
    
    def __init__(self):
        self.current_state = GameState.MAIN_MENU
        self.previous_state = None
        self.state_data: Dict[str, Any] = {}
        
    def change_state(self, new_state: GameState, data: Optional[Dict] = None):
        """Change to a new game state"""
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_data = data or {}
        
    def return_to_previous(self, data: Optional[Dict] = None):
        """Return to the previous state"""
        if self.previous_state:
            self.current_state, self.previous_state = self.previous_state, self.current_state
            self.state_data = data or {}
            
    def is_state(self, state: GameState) -> bool:
        """Check if current state matches"""
        return self.current_state == state
    
    def get_data(self, key: str, default=None):
        """Get state data"""
        return self.state_data.get(key, default)
    
    def set_data(self, key: str, value: Any):
        """Set state data"""
        self.state_data[key] = value
