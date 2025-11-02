"""
Advanced collision detection and response system
"""

import pygame
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.player import Player
    from ..entities.enemy import Enemy
    from ..entities.bullet import Bullet
    from ..entities.particle import ParticleSystem

class CollisionSystem:
    """Handles all collision detection and response"""
    
    def __init__(self):
        self.collision_types = {
            'player_bullet_enemy': self._handle_player_bullet_enemy,
            'enemy_bullet_player': self._handle_enemy_bullet_player,
            'player_enemy': self._handle_player_enemy,
            'player_pickup': self._handle_player_pickup
        }
    
    def check_collisions(self, player: 'Player', enemies: pygame.sprite.Group,
                        player_bullets: pygame.sprite.Group, enemy_bullets: pygame.sprite.Group,
                        pickups: pygame.sprite.Group, particle_system: 'ParticleSystem'):
        """Check all possible collisions"""
        # Player bullets vs Enemies
        enemy_hits = pygame.sprite.groupcollide(
            player_bullets, enemies, True, False,
            collided=pygame.sprite.collide_mask
        )
        
        for bullet, hit_enemies in enemy_hits.items():
            for enemy in hit_enemies:
                self._handle_player_bullet_enemy(bullet, enemy, particle_system)
        
        # Enemy bullets vs Player
        player_hits = pygame.sprite.spritecollide(
            player, enemy_bullets, True,
            collided=pygame.sprite.collide_mask
        )
        
        for bullet in player_hits:
            self._handle_enemy_bullet_player(bullet, player, particle_system)
        
        # Enemy vs Player (collision damage)
        enemy_collisions = pygame.sprite.spritecollide(
            player, enemies, False,
            collided=pygame.sprite.collide_mask
        )
        
        for enemy in enemy_collisions:
            self._handle_player_enemy(enemy, player, particle_system)
        
        # Player vs Pickups
        pickup_collisions = pygame.sprite.spritecollide(
            player, pickups, True,
            collided=pygame.sprite.collide_rect
        )
        
        for pickup in pickup_collisions:
            self._handle_player_pickup(pickup, player)
    
    def _handle_player_bullet_enemy(self, bullet: 'Bullet', enemy: 'Enemy', 
                                  particle_system: 'ParticleSystem'):
        """Handle player bullet hitting enemy"""
        # Apply damage
        enemy.take_damage(bullet.damage)
        
        # Create impact effect
        particle_system.create_explosion(
            bullet.rect.centerx, bullet.rect.centery,
            color=GameSettings.COLORS['NEON_BLUE'],
            size=2.0,
            count=8
        )
        
        # Add screen shake for significant hits
        if bullet.damage >= 30:
            self._add_screen_shake(2)
    
    def _handle_enemy_bullet_player(self, bullet: 'Bullet', player: 'Player',
                                  particle_system: 'ParticleSystem'):
        """Handle enemy bullet hitting player"""
        # Apply damage
        player.take_damage(bullet.damage)
        
        # Create impact effect
        particle_system.create_explosion(
            bullet.rect.centerx, bullet.rect.centery,
            color=GameSettings.COLORS['NEON_PINK'],
            size=1.5,
            count=5
        )
        
        # Add screen shake
        self._add_screen_shake(1)
    
    def _handle_player_enemy(self, enemy: 'Enemy', player: 'Player',
                           particle_system: 'ParticleSystem'):
        """Handle player colliding with enemy"""
        # Calculate collision force
        dx = player.rect.centerx - enemy.rect.centerx
        dy = player.rect.centery - enemy.rect.centery
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        
        # Normalize and apply push force
        push_force = 5.0
        player.velocity.x += (dx / distance) * push_force
        player.velocity.y += (dy / distance) * push_force
        
        # Apply damage to both
        collision_damage = 10
        player.take_damage(collision_damage)
        enemy.take_damage(collision_damage // 2)
        
        # Create collision effect
        particle_system.create_explosion(
            (player.rect.centerx + enemy.rect.centerx) // 2,
            (player.rect.centery + enemy.rect.centery) // 2,
            color=GameSettings.COLORS['NEON_PURPLE'],
            size=3.0,
            count=15
        )
        
        # Strong screen shake for collisions
        self._add_screen_shake(3)
    
    def _handle_player_pickup(self, pickup, player: 'Player'):
        """Handle player collecting pickup"""
        pickup.apply_effect(player)
        
        # Create collection effect
        # (Would use particle system here)
        
        # Play collection sound
        # (Would use audio system here)
    
    def _add_screen_shake(self, intensity: int):
        """Add screen shake effect"""
        # This would communicate with the render system
        # For now, we'll implement a simple version
        pass
    
    def check_line_of_sight(self, start_pos: pygame.Vector2, end_pos: pygame.Vector2,
                          obstacles: pygame.sprite.Group) -> bool:
        """Check if there's a clear line of sight between two points"""
        # Create a temporary surface for line casting
        temp_surface = pygame.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))
        
        # Draw line
        pygame.draw.line(temp_surface, (255, 255, 255, 255), start_pos, end_pos, 2)
        
        # Check for collisions with obstacles
        for obstacle in obstacles:
            if pygame.sprite.collide_mask(obstacle, temp_surface):
                return False
        
        return True
    
    def get_collision_normal(self, rect1: pygame.Rect, rect2: pygame.Rect) -> pygame.Vector2:
        """Calculate collision normal between two rectangles"""
        # Calculate overlap on each axis
        dx = (rect1.centerx - rect2.centerx) / (rect1.width + rect2.width)
        dy = (rect1.centery - rect2.centery) / (rect1.height + rect2.height)
        
        # Return normalized vector pointing from rect2 to rect1
        return pygame.Vector2(dx, dy).normalize()
