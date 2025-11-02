"""
Enemy entities with different behaviors and types
"""

import pygame
import math
import random
from typing import TYPE_CHECKING, List, Tuple
from enum import Enum, auto

from ..core.settings import GameSettings
from .bullet import EnemyBullet

if TYPE_CHECKING:
    from .player import Player

class EnemyType(Enum):
    SCOUT = auto()
    FIGHTER = auto()
    BOMBER = auto()
    ELITE = auto()

class EnemyBehavior(Enum):
    STRAIGHT = auto()
    SINUSOIDAL = auto()
    CIRCLE = auto()
    CHARGE = auto()

class Enemy(pygame.sprite.Sprite):
    """Base enemy class with advanced AI behaviors"""
    
    def __init__(self, enemy_type: EnemyType, position: Tuple[float, float]):
        super().__init__()
        
        self.enemy_type = enemy_type
        self.config = self._get_type_config()
        
        # Create enemy surface based on type
        self.image = self._create_enemy_surface()
        self.rect = self.image.get_rect(center=position)
        self.mask = pygame.mask.from_surface(self.image)
        
        # Movement
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(0, self.config['speed'])
        self.direction = pygame.Vector2(0, 1)
        
        # Combat stats
        self.health = self.config['health']
        self.max_health = self.health
        self.damage = self.config['damage']
        self.fire_rate = self.config['fire_rate']
        self.score_value = self.config['score_value']
        
        # AI behavior
        self.behavior = self.config['behavior']
        self.behavior_timer = 0.0
        self.phase = 0
        self.target_position = None
        
        # Combat cooldowns
        self.last_shot_time = 0
        self.shot_cooldown = random.uniform(0, self.fire_rate / 1000.0)
        
        # Visual effects
        self.hit_flash_timer = 0.0
        self.trail_timer = 0.0
        
    def _get_type_config(self) -> dict:
        """Get configuration for enemy type"""
        configs = {
            EnemyType.SCOUT: {
                'size': (30, 30),
                'color': (255, 100, 100),
                'health': 40,
                'speed': 3.0,
                'damage': 15,
                'fire_rate': 2000,
                'score_value': 10,
                'behavior': EnemyBehavior.STRAIGHT
            },
            EnemyType.FIGHTER: {
                'size': (45, 45),
                'color': (255, 50, 50),
                'health': 80,
                'speed': 2.5,
                'damage': 25,
                'fire_rate': 1500,
                'score_value': 25,
                'behavior': EnemyBehavior.SINUSOIDAL
            },
            EnemyType.BOMBER: {
                'size': (60, 60),
                'color': (200, 50, 50),
                'health': 150,
                'speed': 1.5,
                'damage': 40,
                'fire_rate': 3000,
                'score_value': 50,
                'behavior': EnemyBehavior.STRAIGHT
            },
            EnemyType.ELITE: {
                'size': (50, 50),
                'color': (255, 20, 147),
                'health': 200,
                'speed': 2.0,
                'damage': 35,
                'fire_rate': 1000,
                'score_value': 100,
                'behavior': EnemyBehavior.CIRCLE
            }
        }
        return configs[self.enemy_type]
    
    def _create_enemy_surface(self) -> pygame.Surface:
        """Create enemy visual representation"""
        width, height = self.config['size']
        color = self.config['color']
        
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Different shapes for different enemy types
        if self.enemy_type == EnemyType.SCOUT:
            # Diamond shape
            points = [
                (width // 2, 0),
                (width, height // 2),
                (width // 2, height),
                (0, height // 2)
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 200, 200), points, 2)
            
        elif self.enemy_type == EnemyType.FIGHTER:
            # Arrow shape
            points = [
                (width // 2, 0),
                (width, height // 3),
                (width * 2 // 3, height),
                (width // 3, height),
                (0, height // 3)
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 150, 150), points, 2)
            
        elif self.enemy_type == EnemyType.BOMBER:
            # Wide shape
            points = [
                (width // 4, 0),
                (width * 3 // 4, 0),
                (width, height // 2),
                (width * 3 // 4, height),
                (width // 4, height),
                (0, height // 2)
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 100, 100), points, 3)
            
        elif self.enemy_type == EnemyType.ELITE:
            # Complex star shape
            outer_points = []
            inner_points = []
            for i in range(5):
                # Outer points
                angle = math.pi/2 + i * 2*math.pi/5
                outer_points.append((
                    width//2 + width//2 * math.cos(angle),
                    height//2 + height//2 * math.sin(angle)
                ))
                # Inner points
                angle += math.pi/5
                inner_points.append((
                    width//2 + width//4 * math.cos(angle),
                    height//2 + height//4 * math.sin(angle)
                ))
            
            # Combine points for star
            star_points = []
            for i in range(5):
                star_points.append(outer_points[i])
                star_points.append(inner_points[i])
                
            pygame.draw.polygon(surface, color, star_points)
            pygame.draw.polygon(surface, (255, 100, 255), star_points, 2)
        
        # Add cockpit/glow
        glow_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
        pygame.draw.circle(surface, glow_color, (width // 2, height // 3), width // 6)
        
        return surface
    
    def update(self, delta_time: float, player: "Player"):
        """Update enemy state and behavior"""
        self.behavior_timer += delta_time
        
        # Update behavior
        self._update_behavior(delta_time, player)
        
        # Update position
        self.position += self.velocity
        self.rect.center = self.position
        
        # Try to shoot
        self._update_shooting(delta_time, player)
        
        # Update visual effects
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= delta_time
            
        # Create trail
        self.trail_timer += delta_time
        if self.trail_timer >= 0.1:
            self._create_trail_particle()
            self.trail_timer = 0
            
        # Check if off screen
        if self.rect.top > GameSettings.SCREEN_HEIGHT:
            self.kill()
    
    def _update_behavior(self, delta_time: float, player: "Player"):
        """Update AI behavior based on behavior type"""
        player_pos = pygame.Vector2(player.rect.center) if player else None
        
        if self.behavior == EnemyBehavior.STRAIGHT:
            # Simple straight down movement
            self.velocity.y = self.config['speed']
            
        elif self.behavior == EnemyBehavior.SINUSOIDAL:
            # Sine wave movement
            self.velocity.y = self.config['speed']
            self.velocity.x = math.sin(self.behavior_timer * 2) * 3
            
        elif self.behavior == EnemyBehavior.CIRCLE:
            # Circular movement pattern
            if self.phase == 0:
                # Move down to starting position
                if self.position.y < GameSettings.SCREEN_HEIGHT * 0.3:
                    self.velocity.y = self.config['speed']
                    self.velocity.x = 0
                else:
                    self.phase = 1
                    self.behavior_timer = 0
            else:
                # Circle pattern
                radius = 100
                angular_speed = 1.0
                center_x = GameSettings.SCREEN_WIDTH // 2
                
                angle = self.behavior_timer * angular_speed
                self.position.x = center_x + math.cos(angle) * radius
                self.position.y = GameSettings.SCREEN_HEIGHT * 0.3 + math.sin(angle) * radius * 0.5
                
        elif self.behavior == EnemyBehavior.CHARGE:
            # Charge at player occasionally
            if self.behavior_timer < 2.0:
                # Normal movement
                self.velocity.y = self.config['speed'] * 0.5
                if player_pos:
                    # Drift toward player
                    direction_to_player = (player_pos - self.position).normalize()
                    self.velocity.x = direction_to_player.x * 1.5
            else:
                # Charge!
                if player_pos:
                    charge_direction = (player_pos - self.position).normalize()
                    self.velocity = charge_direction * self.config['speed'] * 2
                self.behavior_timer = 0
    
    def _update_shooting(self, delta_time: float, player: "Player"):
        """Handle enemy shooting logic"""
        if not player:
            return
            
        self.shot_cooldown -= delta_time
        
        if self.shot_cooldown <= 0:
            # Check if player is in front
            if (player.rect.centerx - 100 < self.rect.centerx < player.rect.centerx + 100 and
                player.rect.centery < self.rect.centery):
                
                self.shoot()
                self.shot_cooldown = self.fire_rate / 1000.0
    
    def shoot(self):
        """Shoot a bullet"""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_shot_time >= self.fire_rate:
            bullet = EnemyBullet(
                self.rect.centerx,
                self.rect.bottom,
                self.damage
            )
            
            # Add bullet to game (this would be handled by a bullet manager)
            self.last_shot_time = current_time
    
    def take_damage(self, damage: int):
        """Take damage with visual feedback"""
        self.health -= damage
        self.hit_flash_timer = 0.2
        
        if self.health <= 0:
            self.on_death()
    
    def on_death(self):
        """Handle enemy death"""
        # Create explosion particles
        # Grant experience to player
        # Play death sound
        self.kill()
    
    def _create_trail_particle(self):
        """Create engine trail particles"""
        # This would integrate with particle system
        pass
    
    def draw(self, screen: pygame.Surface):
        """Draw enemy with effects"""
        # Apply hit flash
        if self.hit_flash_timer > 0:
            flash_surface = self.image.copy()
            flash_value = int(255 * (self.hit_flash_timer / 0.2))
            flash_surface.fill((255, flash_value, flash_value, flash_value),
                             special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(flash_surface, self.rect)
        else:
            screen.blit(self.image, self.rect)
        
        # Draw health bar for damaged enemies
        if self.health < self.max_health:
            bar_width = self.rect.width
            bar_height = 4
            bar_x = self.rect.x
            bar_y = self.rect.y - 8
            
            # Background
            pygame.draw.rect(screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Health
            health_ratio = self.health / self.max_health
            health_width = int(bar_width * health_ratio)
            
            health_color = (
                int(255 * (1 - health_ratio)),
                int(255 * health_ratio),
                0
            )
            
            pygame.draw.rect(screen, health_color,
                           (bar_x, bar_y, health_width, bar_height))

class EnemyManager:
    """Manages enemy spawning and behavior"""
    
    def __init__(self):
        self.enemies = pygame.sprite.Group()
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0
        self.wave_multiplier = 1.0
        
    def update(self, delta_time: float, player: "Player", wave_number: int):
        """Update all enemies and handle spawning"""
        self.spawn_timer += delta_time
        
        # Spawn new enemies
        if self.spawn_timer >= self.spawn_interval:
            self._spawn_enemy(wave_number)
            self.spawn_timer = 0.0
            # Decrease spawn interval as wave increases
            self.spawn_interval = max(0.3, 2.0 - (wave_number * 0.1))
        
        # Update existing enemies
        for enemy in self.enemies:
            enemy.update(delta_time, player)
    
    def _spawn_enemy(self, wave_number: int):
        """Spawn a new enemy based on wave number"""
        x = random.randint(50, GameSettings.SCREEN_WIDTH - 50)
        y = -50
        
        # Determine enemy type based on wave
        enemy_types = []
        weights = []
        
        # Scout - always available
        enemy_types.append(EnemyType.SCOUT)
        weights.append(max(0.5, 1.0 - wave_number * 0.1))
        
        # Fighter - available from wave 2
        if wave_number >= 2:
            enemy_types.append(EnemyType.FIGHTER)
            weights.append(min(0.6, (wave_number - 1) * 0.2))
        
        # Bomber - available from wave 4
        if wave_number >= 4:
            enemy_types.append(EnemyType.BOMBER)
            weights.append(min(0.4, (wave_number - 3) * 0.15))
        
        # Elite - available from wave 6
        if wave_number >= 6:
            enemy_types.append(EnemyType.ELITE)
            weights.append(min(0.3, (wave_number - 5) * 0.1))
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
            
            # Choose enemy type
            enemy_type = random.choices(enemy_types, weights=weights)[0]
            
            # Create enemy
            enemy = Enemy(enemy_type, (x, y))
            self.enemies.add(enemy)
    
    def draw(self, screen: pygame.Surface):
        """Draw all enemies"""
        for enemy in self.enemies:
            enemy.draw(screen)
    
    def clear(self):
        """Clear all enemies"""
        self.enemies.empty()
