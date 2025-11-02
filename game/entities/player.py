"""
Player entity with advanced mechanics
"""

import pygame
import math
from typing import TYPE_CHECKING

from ..core.settings import GameSettings
from .bullet import PlayerBullet

if TYPE_CHECKING:
    from pygame.sprite import Group

class Player(pygame.sprite.Sprite):
    """Player controlled spaceship with RPG elements"""
    
    def __init__(self):
        super().__init__()
        
        # Create player surface
        self.image = self._create_ship_surface()
        self.rect = self.image.get_rect(center=GameSettings.get_screen_center())
        self.mask = pygame.mask.from_surface(self.image)
        
        # Movement
        self.position = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = GameSettings.PLAYER_SPEED
        self.drag = 0.9
        
        # Combat stats
        self.max_health = GameSettings.PLAYER_HEALTH
        self.health = self.max_health
        self.max_shield = GameSettings.PLAYER_SHIELD
        self.shield = self.max_shield
        self.damage = GameSettings.BULLET_DAMAGE
        self.fire_rate = GameSettings.PLAYER_SHOOT_COOLDOWN
        
        # RPG progression
        self.level = 1
        self.experience = 0
        self.experience_to_level = GameSettings.LEVEL_UP_EXP
        self.skill_points = 0
        
        # Cooldowns and timers
        self.last_shot_time = 0
        self.last_hit_time = 0
        self.invulnerable = False
        self.shield_regen_timer = 0
        
        # Visual effects
        self.thrust_particles = []
        self.trail_timer = 0
        self.hit_flash_timer = 0
        
    def _create_ship_surface(self) -> pygame.Surface:
        """Create the player ship with cyberpunk styling"""
        surface = pygame.Surface((40, 60), pygame.SRCALPHA)
        
        # Main ship body (triangle)
        points = [
            (20, 0),    # Nose
            (0, 60),    # Bottom left
            (40, 60)    # Bottom right
        ]
        
        # Draw ship with gradient
        for i, color in enumerate([(200, 200, 255), (100, 100, 200), (50, 50, 150)]):
            offset = i * 2
            scaled_points = [
                (20, offset),
                (offset, 60 - offset),
                (40 - offset, 60 - offset)
            ]
            pygame.draw.polygon(surface, color, scaled_points)
        
        # Cockpit
        pygame.draw.circle(surface, (0, 255, 255), (20, 20), 8)
        
        # Engine glow
        for i in range(3):
            y_pos = 60 + i * 5
            radius = 10 - i * 2
            alpha = 100 - i * 30
            glow_surf = pygame.Surface((radius * 2, radius), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 191, 255, alpha), (radius, radius), radius)
            surface.blit(glow_surf, (20 - radius, y_pos - radius))
        
        return surface
    
    def handle_input(self, keys: pygame.key.ScancodeWrapper):
        """Handle player input for movement"""
        # Reset velocity
        input_vector = pygame.Vector2(0, 0)
        
        # Movement input
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            input_vector.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            input_vector.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            input_vector.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            input_vector.x += 1
            
        # Normalize diagonal movement
        if input_vector.length() > 0:
            input_vector.normalize_ip()
            
        # Apply input to velocity
        self.velocity += input_vector * self.speed * 0.5
        self.velocity *= self.drag  # Apply drag
        
        # Clamp velocity
        if self.velocity.length() > self.speed:
            self.velocity.scale_to_length(self.speed)
    
    def update(self, delta_time: float):
        """Update player state"""
        # Update position
        self.position += self.velocity
        self.rect.center = self.position
        
        # Keep player on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        self.position.update(self.rect.center)
        
        # Update timers
        current_time = pygame.time.get_ticks()
        
        # Invulnerability
        if self.invulnerable and current_time - self.last_hit_time > GameSettings.PLAYER_INVULNERABILITY_TIME:
            self.invulnerable = False
            
        # Shield regeneration
        self.shield_regen_timer += delta_time
        if self.shield_regen_timer >= 3.0 and self.shield < self.max_shield:
            self.shield = min(self.max_shield, self.shield + 5)
            self.shield_regen_timer = 0
            
        # Hit flash
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= delta_time
            
        # Create trail particles when moving
        if self.velocity.length() > 0.1:
            self.trail_timer += delta_time
            if self.trail_timer >= 0.05:
                self._create_trail_particle()
                self.trail_timer = 0
    
    def shoot(self, bullet_group: "Group"):
        """Shoot a bullet if cooldown allows"""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_shot_time >= self.fire_rate:
            # Create bullet at player position
            bullet = PlayerBullet(
                self.rect.centerx,
                self.rect.top,
                self.damage
            )
            bullet_group.add(bullet)
            
            self.last_shot_time = current_time
            
            # Create muzzle flash effect
            self._create_muzzle_flash()
    
    def take_damage(self, damage: int):
        """Take damage, applying to shield first"""
        if self.invulnerable:
            return
            
        # Apply to shield first
        shield_damage = min(damage, self.shield)
        self.shield -= shield_damage
        damage -= shield_damage
        
        # Apply remaining damage to health
        if damage > 0:
            self.health -= damage
            self.hit_flash_timer = 0.3  # Flash effect duration
            
        # Set invulnerable and reset shield regen
        self.invulnerable = True
        self.last_hit_time = pygame.time.get_ticks()
        self.shield_regen_timer = 0
    
    def heal(self, amount: int):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
    
    def add_experience(self, amount: int):
        """Add experience and check for level up"""
        self.experience += amount
        
        while self.experience >= self.experience_to_level:
            self.experience -= self.experience_to_level
            self.level_up()
    
    def level_up(self):
        """Handle level up progression"""
        self.level += 1
        self.skill_points += 1
        self.experience_to_level = int(GameSettings.LEVEL_UP_EXP * 
                                    (GameSettings.LEVEL_UP_MULTIPLIER ** (self.level - 1)))
        
        # Restore health and shield on level up
        self.health = self.max_health
        self.shield = self.max_shield
    
    def apply_upgrade(self, upgrade_type: str):
        """Apply a purchased upgrade"""
        if self.skill_points <= 0:
            return False
            
        config = GameSettings.UPGRADES[upgrade_type]
        
        if upgrade_type == 'damage':
            self.damage = int(self.damage * config['multiplier'])
        elif upgrade_type == 'fire_rate':
            self.fire_rate = max(50, self.fire_rate * config['multiplier'])
        elif upgrade_type == 'health':
            self.max_health = int(self.max_health * config['multiplier'])
            self.health = self.max_health
        elif upgrade_type == 'shield':
            self.max_shield = int(self.max_shield * config['multiplier'])
            self.shield = self.max_shield
        elif upgrade_type == 'speed':
            self.speed *= config['multiplier']
            
        self.skill_points -= 1
        return True
    
    def _create_trail_particle(self):
        """Create engine trail particles"""
        # This would integrate with the particle system
        pass
    
    def _create_muzzle_flash(self):
        """Create muzzle flash effect"""
        # This would integrate with the particle system
        pass
    
    def draw(self, screen: pygame.Surface):
        """Draw the player with effects"""
        # Apply hit flash effect
        if self.hit_flash_timer > 0:
            flash_surface = self.image.copy()
            flash_value = int(255 * (self.hit_flash_timer / 0.3))
            flash_surface.fill((255, flash_value, flash_value, flash_value), 
                             special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(flash_surface, self.rect)
        else:
            screen.blit(self.image, self.rect)
        
        # Draw shield effect if active
        if self.shield > 0:
            shield_alpha = min(100, int(150 * (self.shield / self.max_shield)))
            shield_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), 
                                          pygame.SRCALPHA)
            pygame.draw.polygon(shield_surface, (0, 100, 255, shield_alpha), [
                (self.rect.width // 2 + 10, 0),
                (0, self.rect.height + 20),
                (self.rect.width + 20, self.rect.height + 20)
            ])
            screen.blit(shield_surface, (self.rect.x - 10, self.rect.y - 10))
    
    def is_alive(self) -> bool:
        """Check if player is alive"""
        return self.health > 0
    
    def get_stats(self) -> dict:
        """Get player statistics for UI"""
        return {
            'level': self.level,
            'health': f"{self.health}/{self.max_health}",
            'shield': f"{self.shield}/{self.max_shield}",
            'damage': self.damage,
            'fire_rate': f"{60 / (self.fire_rate / 1000):.1f} RPM",
            'speed': f"{self.speed:.1f}",
            'skill_points': self.skill_points
        }
