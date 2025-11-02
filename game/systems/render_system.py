"""
Advanced rendering system with post-processing effects
"""

import pygame
import math
import random
from typing import List, Tuple
from ..core.settings import GameSettings

class RenderSystem:
    """Handles all rendering with advanced visual effects"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background_stars: List[Tuple[Tuple[int, int], float]] = []
        self.background_parallax_layers: List[List[Tuple[int, int, float]]] = []
        self.scanline_texture = self._create_scanline_texture()
        self.crt_distortion = self._create_crt_distortion()
        self.time = 0.0
        
        self._generate_background()
    
    def _generate_background(self):
        """Generate background stars and nebulas"""
        # Generate stars for multiple parallax layers
        for layer in range(3):
            stars = []
            star_count = 100 * (layer + 1)
            brightness_factor = 0.3 + (layer * 0.3)
            
            for _ in range(star_count):
                x = random.randint(0, GameSettings.SCREEN_WIDTH)
                y = random.randint(0, GameSettings.SCREEN_HEIGHT)
                brightness = random.uniform(0.3, 1.0) * brightness_factor
                stars.append((x, y, brightness))
            
            self.background_parallax_layers.append(stars)
    
    def _create_scanline_texture(self) -> pygame.Surface:
        """Create CRT scanline effect texture"""
        texture = pygame.Surface((2, 2), pygame.SRCALPHA)
        # First pixel bright, second pixel dark
        texture.set_at((0, 0), (255, 255, 255, 15))
        texture.set_at((1, 0), (255, 255, 255, 5))
        texture.set_at((0, 1), (255, 255, 255, 5))
        texture.set_at((1, 1), (255, 255, 255, 15))
        return pygame.transform.scale(texture, (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
    
    def _create_crt_distortion(self) -> pygame.Surface:
        """Create CRT curvature distortion map"""
        distortion = pygame.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        center_x, center_y = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(GameSettings.SCREEN_HEIGHT):
            for x in range(GameSettings.SCREEN_WIDTH):
                # Calculate distance from center
                dx = x - center_x
                dy = y - center_y
                dist = math.sqrt(dx**2 + dy**2) / max_dist
                
                # Apply barrel distortion
                distortion_amount = dist ** 2 * 0.1
                new_x = int(x + dx * distortion_amount)
                new_y = int(y + dy * distortion_amount)
                
                # Store as RGBA (using R and G for displacement)
                if 0 <= new_x < GameSettings.SCREEN_WIDTH and 0 <= new_y < GameSettings.SCREEN_HEIGHT:
                    r = min(255, max(0, new_x))
                    g = min(255, max(0, new_y))
                    distortion.set_at((x, y), (r, g, 0, 50))
        
        return distortion
    
    def draw_background(self, wave_number: int):
        """Draw the cyberpunk background with parallax and effects"""
        self.time += 0.01
        
        # Clear screen with dark background
        self.screen.fill(GameSettings.COLORS['BACKGROUND'])
        
        # Draw parallax star layers
        for layer_idx, stars in enumerate(self.background_parallax_layers):
            parallax_offset = math.sin(self.time * 0.5 + layer_idx) * (layer_idx + 1) * 2
            
            for x, y, brightness in stars:
                # Calculate parallax position
                parallax_x = (x + parallax_offset * (layer_idx + 1)) % GameSettings.SCREEN_WIDTH
                parallax_y = (y + math.sin(self.time * 0.3 + x * 0.01) * 2) % GameSettings.SCREEN_HEIGHT
                
                # Calculate star color and size based on layer and brightness
                if layer_idx == 0:  # Distant stars
                    color = (200, 200, 255, int(brightness * 150))
                    size = 1
                elif layer_idx == 1:  # Medium stars
                    color = (255, 255, 200, int(brightness * 200))
                    size = 2
                else:  # Close stars
                    # Twinkling effect
                    twinkle = (math.sin(self.time * 3 + x + y) + 1) * 0.5
                    alpha = int(brightness * 255 * (0.7 + twinkle * 0.3))
                    color = (255, 255, 255, alpha)
                    size = random.randint(1, 3)
                
                # Draw star
                if size == 1:
                    self.screen.set_at((int(parallax_x), int(parallax_y)), color[:3])
                else:
                    pygame.draw.circle(self.screen, color[:3], 
                                     (int(parallax_x), int(parallax_y)), size)
        
        # Draw nebula/gas clouds
        self._draw_nebulas()
        
        # Draw grid lines for cyberpunk feel
        self._draw_grid()
        
        # Apply post-processing effects
        self._apply_post_processing()
    
    def _draw_nebulas(self):
        """Draw colorful nebula effects"""
        nebula_colors = [
            (138, 43, 226, 30),   # Purple
            (255, 20, 147, 25),   # Pink
            (0, 191, 255, 20),    # Blue
            (57, 255, 20, 15)     # Green
        ]
        
        for i, color in enumerate(nebula_colors):
            # Animate nebula positions
            offset_x = math.sin(self.time * 0.2 + i) * 100
            offset_y = math.cos(self.time * 0.3 + i) * 80
            
            # Create nebula surface
            nebula_surf = pygame.Surface((400, 300), pygame.SRCALPHA)
            
            # Draw multiple circles for nebula
            for j in range(5):
                circle_x = 200 + math.sin(self.time * 0.1 + j) * 50
                circle_y = 150 + math.cos(self.time * 0.15 + j) * 40
                radius = 80 + math.sin(self.time * 0.2 + j) * 20
                
                # Draw with gradient
                for r in range(int(radius), 0, -10):
                    alpha = max(0, color[3] - int(r / radius * color[3]))
                    current_color = (color[0], color[1], color[2], alpha)
                    pygame.draw.circle(nebula_surf, current_color, 
                                     (int(circle_x), int(circle_y)), r)
            
            # Position nebula on screen
            pos_x = (i * 300 + offset_x) % (GameSettings.SCREEN_WIDTH + 400) - 200
            pos_y = (i * 200 + offset_y) % (GameSettings.SCREEN_HEIGHT + 300) - 150
            
            self.screen.blit(nebula_surf, (pos_x, pos_y))
    
    def _draw_grid(self):
        """Draw cyberpunk grid lines"""
        grid_color = (0, 100, 200, 50)
        grid_surf = pygame.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Vertical lines
        for x in range(0, GameSettings.SCREEN_WIDTH, 50):
            offset = math.sin(self.time + x * 0.01) * 2
            pygame.draw.line(grid_surf, grid_color, 
                           (x + offset, 0), (x + offset, GameSettings.SCREEN_HEIGHT), 1)
        
        # Horizontal lines
        for y in range(0, GameSettings.SCREEN_HEIGHT, 50):
            offset = math.cos(self.time + y * 0.01) * 2
            pygame.draw.line(grid_surf, grid_color, 
                           (0, y + offset), (GameSettings.SCREEN_WIDTH, y + offset), 1)
        
        self.screen.blit(grid_surf, (0, 0))
    
    def _apply_post_processing(self):
        """Apply CRT and scanline post-processing effects"""
        # Apply scanlines
        self.screen.blit(self.scanline_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Apply subtle vignette
        self._apply_vignette()
        
        # Apply occasional screen shake during intense moments
        if random.random() < 0.02:  # 2% chance per frame during combat
            self._apply_screen_shake()
    
    def _apply_vignette(self):
        """Apply dark vignette effect around edges"""
        vignette = pygame.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        center_x, center_y = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(0, GameSettings.SCREEN_HEIGHT, 4):
            for x in range(0, GameSettings.SCREEN_WIDTH, 4):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2) / max_radius
                alpha = int(min(100, dist * 150))
                pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, 4, 4))
        
        self.screen.blit(vignette, (0, 0))
    
    def _apply_screen_shake(self):
        """Apply subtle screen shake effect"""
        shake_x = random.randint(-2, 2)
        shake_y = random.randint(-2, 2)
        
        # Create a temporary surface to apply shake
        temp_surface = self.screen.copy()
        self.screen.fill((0, 0, 0))
        self.screen.blit(temp_surface, (shake_x, shake_y))
    
    def draw_glow_text(self, text: str, font: pygame.font.Font, 
                      position: Tuple[int, int], color: Tuple[int, int, int],
                      glow_color: Tuple[int, int, int] = None):
        """Draw text with glow effect"""
        if glow_color is None:
            glow_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
        
        # Draw glow (multiple passes)
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            glow_surf = font.render(text, True, glow_color)
            self.screen.blit(glow_surf, (position[0] + offset[0], position[1] + offset[1]))
        
        # Draw main text
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, position)
    
    def draw_progress_bar(self, rect: pygame.Rect, progress: float, 
                         fill_color: Tuple[int, int, int],
                         background_color: Tuple[int, int, int] = None,
                         border_color: Tuple[int, int, int] = None):
        """Draw a cyberpunk-style progress bar"""
        if background_color is None:
            background_color = (50, 50, 50)
        if border_color is None:
            border_color = (100, 100, 100)
        
        # Draw background
        pygame.draw.rect(self.screen, background_color, rect)
        
        # Draw fill
        if progress > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, int(rect.width * progress), rect.height)
            pygame.draw.rect(self.screen, fill_color, fill_rect)
            
            # Draw inner glow
            glow_surf = pygame.Surface((fill_rect.width, fill_rect.height), pygame.SRCALPHA)
            for i in range(3):
                alpha = 50 - i * 15
                glow_rect = pygame.Rect(i, i, fill_rect.width - i*2, fill_rect.height - i*2)
                pygame.draw.rect(glow_surf, (*fill_color[:3], alpha), glow_rect, 1)
            self.screen.blit(glow_surf, fill_rect)
        
        # Draw border
        pygame.draw.rect(self.screen, border_color, rect, 2)
        
        # Draw cyberpunk details
        if rect.width > 100:  # Only add details to larger bars
            segment_width = 20
            for i in range(0, rect.width, segment_width):
                segment_x = rect.x + i
                pygame.draw.line(self.screen, (200, 200, 200, 100),
                               (segment_x, rect.y), (segment_x, rect.y + rect.height), 1)
