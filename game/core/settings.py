"""
Game configuration and constants
"""

import pygame
import os
import math
from typing import Tuple, Dict, Any

class GameSettings:
    """Centralized game settings and constants"""
    
    # Display settings
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    FPS = 144
    TITLE = "NOTLIFE"
    
    # Colors - Cyberpunk palette
    COLORS = {
        'BACKGROUND': (5, 5, 15),
        'NEON_PINK': (255, 20, 147),
        'NEON_BLUE': (0, 191, 255),
        'NEON_PURPLE': (138, 43, 226),
        'NEON_GREEN': (57, 255, 20),
        'NEON_CYAN': (0, 255, 255),
        'DARK_GRAY': (20, 20, 30),
        'LIGHT_GRAY': (100, 100, 120),
        'UI_BACKGROUND': (10, 10, 20, 200),
        'TEXT': (220, 220, 220),
        'WARNING': (255, 50, 50),
        'EXPERIENCE': (0, 200, 255)
    }
    
    # Player settings
    PLAYER_SPEED = 7
    PLAYER_HEALTH = 100
    PLAYER_SHIELD = 50
    PLAYER_SHOOT_COOLDOWN = 150  # ms
    PLAYER_INVULNERABILITY_TIME = 1000  # ms
    
    # Bullet settings
    BULLET_SPEED = 12
    BULLET_DAMAGE = 25
    BULLET_LIFETIME = 2000  # ms
    
    # Enemy settings
    ENEMY_SPAWN_RATE = 1.5  # seconds
    ENEMY_BASE_HEALTH = 50
    ENEMY_BASE_SPEED = 2.5
    ENEMY_BASE_DAMAGE = 10
    
    # Wave system
    WAVE_DURATION = 45  # seconds
    WAVE_ENEMY_MULTIPLIER = 1.2
    WAVE_DIFFICULTY_SCALE = 1.15
    
    # Experience system
    EXP_PER_KILL = 10
    LEVEL_UP_EXP = 100
    LEVEL_UP_MULTIPLIER = 1.5
    
    # Particle system
    PARTICLE_LIFETIME = 1.0  # seconds
    MAX_PARTICLES = 500
    
    # UI settings
    UI_MARGIN = 20
    UI_FONT_SIZE = 18
    UI_TITLE_SIZE = 48
    UI_BUTTON_WIDTH = 300
    UI_BUTTON_HEIGHT = 60
    
    # Audio settings
    MASTER_VOLUME = 0.7
    SFX_VOLUME = 0.8
    MUSIC_VOLUME = 0.6
    
    # Game progression
    UPGRADES = {
        'damage': {'base': 25, 'cost': 50, 'multiplier': 1.2},
        'fire_rate': {'base': 150, 'cost': 75, 'multiplier': 0.85},
        'health': {'base': 100, 'cost': 100, 'multiplier': 1.3},
        'shield': {'base': 50, 'cost': 80, 'multiplier': 1.25},
        'speed': {'base': 7, 'cost': 60, 'multiplier': 1.15}
    }
    
    @classmethod
    def get_screen_center(cls) -> Tuple[int, int]:
        return (cls.SCREEN_WIDTH // 2, cls.SCREEN_HEIGHT // 2)
    
    @classmethod
    def get_neon_color(cls, color_name: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        base_color = cls.COLORS[color_name]
        return (*base_color, alpha)
