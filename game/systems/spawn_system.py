"""
Enemy and pickup spawning system
"""

import pygame
import random
import math
from typing import List, Dict, Any
from enum import Enum

from ..core.settings import GameSettings
from ..entities.enemy import Enemy, EnemyType, EnemyBehavior

class SpawnPattern(Enum):
    RANDOM = 1
    FORMATION = 2
    WAVE = 3
    BOSS = 4

class SpawnSystem:
    """Manages enemy and pickup spawning with patterns"""
    
    def __init__(self):
        self.spawn_timer = 0.0
        self.base_spawn_interval = 2.0
        self.wave_spawn_count = 0
        self.max_wave_spawns = 10
        self.current_pattern = SpawnPattern.RANDOM
        self.pattern_timer = 0.0
        self.formation_positions: List[tuple] = []
        
    def update(self, delta_time: float, enemies: pygame.sprite.Group, wave_number: int):
        """Update spawning logic"""
        self.spawn_timer += delta_time
        self.pattern_timer += delta_time
        
        # Update spawn pattern based on wave and timer
        self._update_spawn_pattern(wave_number)
        
        # Calculate current spawn interval
        spawn_interval = self._get_spawn_interval(wave_number)
        
        # Spawn enemies based on current pattern
        if self.spawn_timer >= spawn_interval and self.wave_spawn_count < self.max_wave_spawns:
            self._spawn_enemies(enemies, wave_number)
            self.spawn_timer = 0.0
            self.wave_spawn_count += 1
        
        # Reset wave spawn count if all enemies are dead and we're ready for new wave
        if len(enemies) == 0 and self.wave_spawn_count >= self.max_wave_spawns:
            self.wave_spawn_count = 0
            self.max_wave_spawns = self._get_max_spawns(wave_number)
    
    def _update_spawn_pattern(self, wave_number: int):
        """Update the current spawn pattern"""
        pattern_duration = 10.0  # Change pattern every 10 seconds
        
        if self.pattern_timer >= pattern_duration:
            available_patterns = [SpawnPattern.RANDOM]
            
            if wave_number >= 2:
                available_patterns.append(SpawnPattern.FORMATION)
            if wave_number >= 4:
                available_patterns.append(SpawnPattern.WAVE)
            if wave_number >= 6:
                available_patterns.append(SpawnPattern.BOSS)
            
            self.current_pattern = random.choice(available_patterns)
            self.pattern_timer = 0.0
            
            # Initialize pattern-specific data
            if self.current_pattern == SpawnPattern.FORMATION:
                self._generate_formation_positions()
    
    def _get_spawn_interval(self, wave_number: int) -> float:
        """Calculate spawn interval based on wave number"""
        base_interval = self.base_spawn_interval
        reduction_per_wave = 0.1
        min_interval = 0.5
        
        interval = max(min_interval, base_interval - (wave_number * reduction_per_wave))
        
        # Pattern-specific adjustments
        if self.current_pattern == SpawnPattern.FORMATION:
            interval *= 1.5  # Slower spawn for formations
        elif self.current_pattern == SpawnPattern.WAVE:
            interval *= 0.7  # Faster spawn for waves
        
        return interval
    
    def _get_max_spawns(self, wave_number: int) -> int:
        """Calculate maximum spawns per wave"""
        base_spawns = 10
        additional_per_wave = 2
        
        return base_spawns + (wave_number * additional_per_wave)
    
    def _spawn_enemies(self, enemies: pygame.sprite.Group, wave_number: int):
        """Spawn enemies based on current pattern"""
        if self.current_pattern == SpawnPattern.RANDOM:
            self._spawn_random(enemies, wave_number)
        elif self.current_pattern == SpawnPattern.FORMATION:
            self._spawn_formation(enemies, wave_number)
        elif self.current_pattern == SpawnPattern.WAVE:
            self._spawn_wave(enemies, wave_number)
        elif self.current_pattern == SpawnPattern.BOSS:
            self._spawn_boss(enemies, wave_number)
    
    def _spawn_random(self, enemies: pygame.sprite.Group, wave_number: int):
        """Spawn enemies at random positions"""
        enemy_type = self._get_random_enemy_type(wave_number)
        x = random.randint(50, GameSettings.SCREEN_WIDTH - 50)
        y = -50
        
        enemy = Enemy(enemy_type, (x, y))
        enemies.add(enemy)
    
    def _spawn_formation(self, enemies: pygame.sprite.Group, wave_number: int):
        """Spawn enemies in formations"""
        if not self.formation_positions:
            self._generate_formation_positions()
        
        formation_type = random.choice(['V', 'line', 'circle'])
        enemy_type = self._get_random_enemy_type(wave_number)
        
        if formation_type == 'V':
            self._spawn_v_formation(enemies, enemy_type)
        elif formation_type == 'line':
            self._spawn_line_formation(enemies, enemy_type)
        elif formation_type == 'circle':
            self._spawn_circle_formation(enemies, enemy_type)
    
    def _spawn_v_formation(self, enemies: pygame.sprite.Group, enemy_type: EnemyType):
        """Spawn enemies in V formation"""
        center_x = GameSettings.SCREEN_WIDTH // 2
        start_y = -100
        
        formation_size = 5
        spacing = 60
        
        for i in range(formation_size):
            # Left wing
            x_left = center_x - (i * spacing)
            enemy_left = Enemy(enemy_type, (x_left, start_y + i * 30))
            enemies.add(enemy_left)
            
            # Right wing
            x_right = center_x + (i * spacing)
            enemy_right = Enemy(enemy_type, (x_right, start_y + i * 30))
            enemies.add(enemy_right)
    
    def _spawn_line_formation(self, enemies: pygame.sprite.Group, enemy_type: EnemyType):
        """Spawn enemies in a horizontal line"""
        formation_size = 7
        start_y = -50
        spacing = 70
        start_x = (GameSettings.SCREEN_WIDTH - (formation_size * spacing)) // 2
        
        for i in range(formation_size):
            x = start_x + (i * spacing)
            enemy = Enemy(enemy_type, (x, start_y))
            enemies.add(enemy)
    
    def _spawn_circle_formation(self, enemies: pygame.sprite.Group, enemy_type: EnemyType):
        """Spawn enemies in a circular formation"""
        formation_size = 8
        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = -150
        radius = 100
        
        for i in range(formation_size):
            angle = (2 * math.pi / formation_size) * i
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            enemy = Enemy(enemy_type, (x, y))
            enemies.add(enemy)
    
    def _spawn_wave(self, enemies: pygame.sprite.Group, wave_number: int):
        """Spawn a rapid wave of enemies"""
        wave_size = min(8, 3 + wave_number // 2)
        enemy_type = self._get_random_enemy_type(wave_number)
        
        start_x = random.randint(100, GameSettings.SCREEN_WIDTH - 100)
        
        for i in range(wave_size):
            x = start_x + random.randint(-50, 50)
            y = -50 - (i * 40)  # Staggered vertically
            
            enemy = Enemy(enemy_type, (x, y))
            enemies.add(enemy)
    
    def _spawn_boss(self, enemies: pygame.sprite.Group, wave_number: int):
        """Spawn a boss enemy"""
        # For now, spawn an elite enemy as mini-boss
        # In a full implementation, this would spawn a proper boss class
        x = GameSettings.SCREEN_WIDTH // 2
        y = -100
        
        boss = Enemy(EnemyType.ELITE, (x, y))
        # Enhance boss stats
        boss.health *= 3
        boss.damage *= 2
        boss.score_value *= 5
        
        enemies.add(boss)
    
    def _generate_formation_positions(self):
        """Generate positions for formation spawning"""
        self.formation_positions = []
        # This would generate specific positions for different formations
    
    def _get_random_enemy_type(self, wave_number: int) -> EnemyType:
        """Get random enemy type based on wave number"""
        enemy_weights = []
        enemy_types = []
        
        # Scout - common in all waves
        enemy_types.append(EnemyType.SCOUT)
        enemy_weights.append(max(0.1, 1.0 - wave_number * 0.1))
        
        # Fighter - appears from wave 2
        if wave_number >= 2:
            enemy_types.append(EnemyType.FIGHTER)
            enemy_weights.append(min(0.6, (wave_number - 1) * 0.2))
        
        # Bomber - appears from wave 4
        if wave_number >= 4:
            enemy_types.append(EnemyType.BOMBER)
            enemy_weights.append(min(0.4, (wave_number - 3) * 0.15))
        
        # Elite - appears from wave 6
        if wave_number >= 6:
            enemy_types.append(EnemyType.ELITE)
            enemy_weights.append(min(0.3, (wave_number - 5) * 0.1))
        
        # Normalize weights
        total_weight = sum(enemy_weights)
        if total_weight > 0:
            normalized_weights = [w / total_weight for w in enemy_weights]
            return random.choices(enemy_types, weights=normalized_weights)[0]
        
        return EnemyType.SCOUT  # Fallback
    
    def spawn_pickup(self, position: tuple, pickup_type: str) -> bool:
        """Spawn a pickup at specified position"""
        # This would create different types of pickups
        # (health, shield, weapon upgrade, etc.)
        pass
