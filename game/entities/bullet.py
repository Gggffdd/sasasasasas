"""
Bullet and projectile system
"""

import pygame
import math
from typing import Tuple
from ..core.settings import GameSettings

class Bullet(pygame.sprite.Sprite):
    """Base bullet class"""
    
    def __init__(self, x: float, y: float, damage: int, speed: float, 
                 direction: Tuple[float, float], color: Tuple[int, int, int]):
        super().__init__()
        
        self.damage = damage
        self.speed = speed
        self.direction = pygame.Vector2(direction).normalize()
        self.lifetime = GameSettings.BULLET_LIFETIME
        self.spawn_time = pygame.time.get_ticks()
        
        # Create bullet surface
        self.image = self._create_bullet_surface(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        
        # Position for smooth movement
        self.position = pygame.Vector2(x, y)
        
    def _create_bullet_surface(self, color: Tuple[int, int, int]) -> pygame.Surface:
        """Create bullet visual representation"""
        surface = pygame.Surface((6, 12), pygame.SRCALPHA)
        
        # Bullet body
        pygame.draw.rect(surface, color, (1, 0, 4, 10))
        
        # Bullet tip
        pygame.draw.polygon(surface, (255, 255, 200), [
            (3, 0), (0, -3), (6, -3)
        ])
        
        # Glow effect
        glow = pygame.Surface((8, 14), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color[:3], 50), (0, 1, 8, 12))
        surface.blit(glow, (-1, -1), special_flags=pygame.BLEND_RGBA_ADD)
        
        return surface
    
    def update(self, delta_time: float):
        """Update bullet position and check lifetime"""
        # Move bullet
        self.position += self.direction * self.speed * delta_time * 60
        self.rect.center = self.position
        
        # Check lifetime
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
            
        # Check bounds
        if (self.rect.right < 0 or self.rect.left > GameSettings.SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > GameSettings.SCREEN_HEIGHT):
            self.kill()
    
    def draw(self, screen: pygame.Surface):
        """Draw the bullet"""
        screen.blit(self.image, self.rect)

class PlayerBullet(Bullet):
    """Player's bullets"""
    
    def __init__(self, x: float, y: float, damage: int):
        super().__init__(x, y, damage, GameSettings.BULLET_SPEED, 
                        (0, -1), GameSettings.COLORS['NEON_BLUE'])

class EnemyBullet(Bullet):
    """Enemy bullets"""
    
    def __init__(self, x: float, y: float, damage: int):
        super().__init__(x, y, damage, GameSettings.BULLET_SPEED * 0.8, 
                        (0, 1), GameSettings.COLORS['NEON_PINK'])

class HomingMissile(Bullet):
    """Homing missile that follows targets"""
    
    def __init__(self, x: float, y: float, damage: int, target):
        super().__init__(x, y, damage, GameSettings.BULLET_SPEED * 0.6,
                        (0, -1), GameSettings.COLORS['NEON_GREEN'])
        self.target = target
        self.turn_rate = 2.0  # Degrees per frame
        self.acceleration = 0.1
        
    def update(self, delta_time: float):
        """Update with homing behavior"""
        if self.target and self.target.alive():
            # Calculate direction to target
            target_dir = (pygame.Vector2(self.target.rect.center) - self.position).normalize()
            
            # Gradually turn toward target
            current_angle = math.atan2(-self.direction.y, self.direction.x)
            target_angle = math.atan2(-target_dir.y, target_dir.x)
            
            # Calculate shortest angle difference
            angle_diff = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
            
            # Apply turn rate limit
            max_turn = math.radians(self.turn_rate) * delta_time * 60
            turn_amount = max(-max_turn, min(max_turn, angle_diff))
            
            new_angle = current_angle + turn_amount
            
            # Update direction
            self.direction.x = math.cos(new_angle)
            self.direction.y = -math.sin(new_angle)
            
            # Accelerate
            self.speed += self.acceleration * delta_time * 60
        
        super().update(delta_time)

class LaserBeam(pygame.sprite.Sprite):
    """Continuous laser beam weapon"""
    
    def __init__(self, owner, damage: int, color: Tuple[int, int, int]):
        super().__init__()
        self.owner = owner
        self.damage = damage
        self.color = color
        self.active = False
        self.max_range = 500
        self.width = 8
        
        self.image = pygame.Surface((self.width, self.max_range), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
    def update(self, delta_time: float):
        """Update laser position and check hits"""
        if not self.active or not self.owner.alive():
            self.kill()
            return
            
        # Position laser at owner
        self.rect.midtop = self.owner.rect.midtop
        
        # Create laser beam
        self.image.fill((0, 0, 0, 0))
        
        # Draw laser with gradient
        for i in range(self.width):
            alpha = 200 - (i * 20)
            pygame.draw.line(self.image, (*self.color[:3], alpha),
                           (i, 0), (i, self.max_range), 1)
        
        # Add glow
        glow_surf = pygame.Surface((self.width + 10, self.max_range), pygame.SRCALPHA)
        for i in range(5):
            glow_width = self.width + 10 - i * 2
            glow_alpha = 50 - i * 10
            pygame.draw.line(glow_surf, (*self.color[:3], glow_alpha),
                           (self.width // 2, 0), (self.width // 2, self.max_range),
                           glow_width)
        
        self.image.blit(glow_surf, (-5, 0), special_flags=pygame.BLEND_RGBA_ADD)
    
    def activate(self):
        """Activate the laser beam"""
        self.active = True
    
    def deactivate(self):
        """Deactivate the laser beam"""
        self.active = False
        self.kill()

class BulletManager:
    """Manages all bullets in the game"""
    
    def __init__(self):
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.special_bullets = pygame.sprite.Group()
        
    def update(self, delta_time: float):
        """Update all bullets"""
        self.player_bullets.update(delta_time)
        self.enemy_bullets.update(delta_time)
        self.special_bullets.update(delta_time)
        
    def draw(self, screen: pygame.Surface):
        """Draw all bullets"""
        self.player_bullets.draw(screen)
        self.enemy_bullets.draw(screen)
        self.special_bullets.draw(screen)
        
    def clear(self):
        """Clear all bullets"""
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.special_bullets.empty()
        
    def add_player_bullet(self, bullet: Bullet):
        """Add a player bullet"""
        self.player_bullets.add(bullet)
        
    def add_enemy_bullet(self, bullet: Bullet):
        """Add an enemy bullet"""
        self.enemy_bullets.add(bullet)
        
    def add_special_bullet(self, bullet: Bullet):
        """Add a special bullet (homing, laser, etc.)"""
        self.special_bullets.add(bullet)
