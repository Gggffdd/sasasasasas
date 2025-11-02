"""
Wave-based progression system
"""

import pygame
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import NotLifeGame

from ..core.settings import GameSettings

class WaveSystem:
    """Manages wave-based game progression"""
    
    def __init__(self):
        self.current_wave = 0
        self.wave_timer = 0.0
        self.wave_duration = GameSettings.WAVE_DURATION
        self.is_wave_active = False
        self.wave_start_time = 0.0
        self.enemies_defeated = 0
        self.total_wave_enemies = 0
        self.wave_completion_bonus = 100
        
        # Wave configuration
        self.wave_configs = {
            1: {'enemy_count': 10, 'difficulty': 1.0, 'description': "Scout Patrol"},
            2: {'enemy_count': 15, 'difficulty': 1.2, 'description': "Fighter Squadron"},
            3: {'enemy_count': 20, 'difficulty': 1.5, 'description': "Mixed Assault"},
            4: {'enemy_count': 18, 'difficulty': 1.8, 'description': "Bomber Run"},
            5: {'enemy_count': 25, 'difficulty': 2.0, 'description': "Elite Strike"},
            # Waves continue with increasing difficulty...
        }
    
    def update(self, delta_time: float, game: 'NotLifeGame'):
        """Update wave system"""
        if not self.is_wave_active:
            return
            
        self.wave_timer += delta_time
        
        # Check for wave completion
        if self._is_wave_completed(game):
            self._complete_wave(game)
        
        # Check for wave timeout
        elif self.wave_timer >= self.wave_duration:
            self._timeout_wave(game)
    
    def start_wave(self, wave_number: int):
        """Start a new wave"""
        self.current_wave = wave_number
        self.wave_timer = 0.0
        self.is_wave_active = True
        self.enemies_defeated = 0
        self.wave_start_time = pygame.time.get_ticks()
        
        # Get wave configuration
        config = self._get_wave_config(wave_number)
        self.total_wave_enemies = config['enemy_count']
        
        # Apply wave difficulty scaling
        self._apply_wave_difficulty(config['difficulty'])
        
        print(f"Wave {wave_number} started: {config['description']}")
    
    def _get_wave_config(self, wave_number: int) -> dict:
        """Get configuration for specified wave"""
        if wave_number in self.wave_configs:
            return self.wave_configs[wave_number]
        else:
            # Generate configuration for higher waves
            base_enemies = 20 + (wave_number * 3)
            difficulty = 1.0 + (wave_number * 0.3)
            
            return {
                'enemy_count': base_enemies,
                'difficulty': difficulty,
                'description': f"Wave {wave_number} Assault"
            }
    
    def _apply_wave_difficulty(self, difficulty: float):
        """Apply difficulty scaling to game settings"""
        # Scale enemy stats
        GameSettings.ENEMY_BASE_HEALTH = int(50 * difficulty)
        GameSettings.ENEMY_BASE_DAMAGE = int(10 * difficulty)
        GameSettings.ENEMY_BASE_SPEED = 2.5 * difficulty
        
        # Adjust spawn rates
        GameSettings.ENEMY_SPAWN_RATE = max(0.5, 1.5 / difficulty)
    
    def _is_wave_completed(self, game: 'NotLifeGame') -> bool:
        """Check if current wave is completed"""
        # Wave is completed when all enemies are defeated
        # and the minimum time has passed
        min_wave_duration = 10.0  # Minimum seconds per wave
        
        return (self.enemies_defeated >= self.total_wave_enemies and 
                self.wave_timer >= min_wave_duration and
                len(game.enemies) == 0)
    
    def _complete_wave(self, game: 'NotLifeGame'):
        """Handle wave completion"""
        self.is_wave_active = False
        
        # Calculate score bonus
        time_bonus = max(0, int((self.wave_duration - self.wave_timer) * 10))
        completion_bonus = self.wave_completion_bonus * self.current_wave
        total_bonus = time_bonus + completion_bonus
        
        # Add bonus to score
        game.score += total_bonus
        
        # Show wave complete message
        print(f"Wave {self.current_wave} completed!")
        print(f"Time bonus: {time_bonus}")
        print(f"Completion bonus: {completion_bonus}")
        
        # Prepare for next wave
        self._prepare_next_wave(game)
    
    def _timeout_wave(self, game: 'NotLifeGame'):
        """Handle wave timeout"""
        self.is_wave_active = False
        
        # Wave failed - maybe apply penalty or end game
        print(f"Wave {self.current_wave} failed - timeout!")
        
