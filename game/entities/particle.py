"""
Advanced particle system for visual effects
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
from ..core.settings import GameSettings

class Particle:
    """Single particle with physics and rendering"""
    
    def __init__(self, x: float, y: float, 
                 particle_type: str = "circle",
                 color: Tuple[int, int, int] = (255, 255, 255),
                 size: float = 4.0,
                 lifetime: float = 1.0,
                 velocity: Tuple[float, float] = (0, 0),
                 acceleration: Tuple[float, float] = (0, 0),
                 fade_out: bool = True,
                 gravity: float = 0.0):
        
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(velocity)
        self.acceleration = pygame.Vector2(acceleration)
        self.color = color
        self.size = size
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.particle_type = particle_type
        self.fade_out = fade_out
        self.gravity = gravity
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.scale = 1.0
        self.scale_speed = 0.0
        
    def update(self, delta_time: float) -> bool:
        """Update particle and return False if dead"""
        self.lifetime -= delta_time
        
        if self.lifetime <= 0:
            return False
            
        # Update physics
        self.velocity.x += self.acceleration.x * delta_time
        self.velocity.y += self.acceleration.y * delta_time
        self.velocity.y += self.gravity * delta_time
        
        self.position.x += self.velocity.x * delta_time * 60
        self.position.y += self.velocity.y * delta_time * 60
        
        # Update rotation and scale
        self.rotation += self.rotation_speed * delta_time
        self.scale += self.scale_speed * delta_time
        
        return True
    
    def draw(self, screen: pygame.Surface):
        """Draw the particle"""
        alpha = 255
        if self.fade_out:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            
        current_size = max(1, int(self.size * self.scale))
        
        if self.particle_type == "circle":
            # Draw circle particle
            surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color[:3], alpha), 
                             (current_size, current_size), current_size)
            screen.blit(surf, (self.position.x - current_size, self.position.y - current_size))
            
        elif self.particle_type == "square":
            # Draw square particle
            surf = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
            surf.fill((*self.color[:3], alpha))
            screen.blit(surf, (self.position.x - current_size//2, self.position.y - current_size//2))
            
        elif self.particle_type == "spark":
            # Draw spark (rotated line)
            angle_rad = math.radians(self.rotation)
            end_x = self.position.x + math.cos(angle_rad) * current_size
            end_y = self.position.y + math.sin(angle_rad) * current_size
            
            pygame.draw.line(screen, (*self.color[:3], alpha),
                           (self.position.x, self.position.y),
                           (end_x, end_y), max(1, current_size // 2))
            
        elif self.particle_type == "trail":
            # Draw trail particle (elongated)
            angle = math.atan2(self.velocity.y, self.velocity.x)
            length = current_size * 2
            
            end_x = self.position.x + math.cos(angle) * length
            end_y = self.position.y + math.sin(angle) * length
            
            pygame.draw.line(screen, (*self.color[:3], alpha),
                           (self.position.x, self.position.y),
                           (end_x, end_y), max(1, current_size // 2))

class ParticleSystem:
    """Manages and renders particle effects"""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.emitters: List[ParticleEmitter] = []
        
    def update(self, delta_time: float):
        """Update all particles and emitters"""
        # Update particles
        self.particles = [p for p in self.particles if p.update(delta_time)]
        
        # Update emitters
        for emitter in self.emitters[:]:
            emitter.update(delta_time)
            if not emitter.active:
                self.emitters.remove(emitter)
    
    def draw(self, screen: pygame.Surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)
    
    def add_particle(self, particle: Particle):
        """Add a single particle"""
        if len(self.particles) < GameSettings.MAX_PARTICLES:
            self.particles.append(particle)
    
    def add_emitter(self, emitter: "ParticleEmitter"):
        """Add a particle emitter"""
        self.emitters.append(emitter)
    
    def create_explosion(self, x: float, y: float, 
                        color: Tuple[int, int, int] = (255, 100, 50),
                        size: float = 3.0,
                        count: int = 30):
        """Create an explosion effect"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            
            particle = Particle(
                x, y,
                particle_type=random.choice(["circle", "spark"]),
                color=color,
                size=random.uniform(size * 0.5, size * 1.5),
                lifetime=random.uniform(0.5, 1.5),
                velocity=velocity,
                acceleration=(0, 0),
                gravity=0.0,
                fade_out=True
            )
            self.add_particle(particle)
    
    def create_trail(self, x: float, y: float, 
                    color: Tuple[int, int, int] = (100, 150, 255),
                    count: int = 3):
        """Create a trail effect"""
        for _ in range(count):
            particle = Particle(
                x + random.uniform(-5, 5),
                y + random.uniform(-5, 5),
                particle_type="circle",
                color=color,
                size=random.uniform(1.0, 3.0),
                lifetime=random.uniform(0.2, 0.5),
                velocity=(random.uniform(-10, 10), random.uniform(-10, 10)),
                fade_out=True
            )
            self.add_particle(particle)
    
    def create_sparkle(self, x: float, y: float,
                      color: Tuple[int, int, int] = (255, 255, 200)):
        """Create a sparkle effect"""
        particle = Particle(
            x, y,
            particle_type="spark",
            color=color,
            size=random.uniform(2.0, 4.0),
            lifetime=random.uniform(0.3, 0.7),
            velocity=(0, 0),
            rotation_speed=random.uniform(-10, 10),
            scale_speed=-2.0,
            fade_out=True
        )
        self.add_particle(particle)
    
    def clear(self):
        """Clear all particles and emitters"""
        self.particles.clear()
        self.emitters.clear()

class ParticleEmitter:
    """Continuous particle emitter"""
    
    def __init__(self, x: float, y: float, 
                 particle_system: ParticleSystem,
                 emit_rate: float = 10.0,  # particles per second
                 duration: float = -1.0):  # -1 for continuous
        self.position = pygame.Vector2(x, y)
        self.particle_system = particle_system
        self.emit_rate = emit_rate
        self.duration = duration
        self.active = True
        self.timer = 0.0
        self.emission_accumulator = 0.0
        
        # Emission properties
        self.particle_color = (255, 200, 100)
        self.particle_size = 2.0
        self.particle_lifetime = 1.0
        self.emit_angle_range = (0, math.pi * 2)
        self.emit_speed_range = (10, 50)
        
    def update(self, delta_time: float):
        """Update emitter and create new particles"""
        if not self.active:
            return
            
        self.timer += delta_time
        
        # Check duration
        if self.duration > 0 and self.timer >= self.duration:
            self.active = False
            return
        
        # Calculate how many particles to emit
        self.emission_accumulator += self.emit_rate * delta_time
        
        while self.emission_accumulator >= 1.0:
            self.emit_particle()
            self.emission_accumulator -= 1.0
    
    def emit_particle(self):
        """Emit a single particle"""
        angle = random.uniform(*self.emit_angle_range)
        speed = random.uniform(*self.emit_speed_range)
        velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
        
        particle = Particle(
            self.position.x, self.position.y,
            particle_type=random.choice(["circle", "square"]),
            color=self.particle_color,
            size=random.uniform(self.particle_size * 0.5, self.particle_size * 1.5),
            lifetime=random.uniform(self.particle_lifetime * 0.5, self.particle_lifetime * 1.5),
            velocity=velocity,
            fade_out=True
        )
        
        self.particle_system.add_particle(particle)
    
    def stop(self):
        """Stop the emitter"""
        self.active = False
