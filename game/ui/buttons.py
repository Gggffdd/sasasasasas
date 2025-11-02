"""
Interactive button system with animations
"""

import pygame
import math
from ..core.settings import GameSettings

class Button:
    """Animated interactive button"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, action: str, base_color: tuple):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.base_color = base_color
        self.hover_color = self._lighten_color(base_color, 30)
        self.click_color = self._lighten_color(base_color, 50)
        self.current_color = base_color
        self.is_hovered = False
        self.is_clicked = False
        self.animation_progress = 0.0
        self.glow_intensity = 0.0
        
        # Font
        self.font = pygame.font.Font(None, 28)
        self.text_surface = self.font.render(text, True, (255, 255, 255))
        
    def _lighten_color(self, color: tuple, amount: int) -> tuple:
        """Lighten a color by specified amount"""
        return tuple(min(255, c + amount) for c in color)
    
    def draw(self, screen: pygame.Surface, animation_time: float):
        """Draw the button with animations"""
        # Update glow intensity
        self.glow_intensity = (math.sin(animation_time * 3) + 1) * 0.5 * 0.3
        
        # Draw button background with glow
        self._draw_button_background(screen)
        
        # Draw button border
        self._draw_button_border(screen)
        
        # Draw button text
        self._draw_button_text(screen)
        
        # Draw hover/click effects
        self._draw_interaction_effects(screen)
    
    def _draw_button_background(self, screen: pygame.Surface):
        """Draw button background with cyberpunk style"""
        # Main button fill
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)
        
        # Inner glow
        inner_rect = self.rect.inflate(-4, -4)
        glow_surf = pygame.Surface(inner_rect.size, pygame.SRCALPHA)
        glow_alpha = int(100 * self.glow_intensity)
        pygame.draw.rect(glow_surf, (*self.base_color[:3], glow_alpha), 
                        glow_surf.get_rect())
        screen.blit(glow_surf, inner_rect)
    
    def _draw_button_border(self, screen: pygame.Surface):
        """Draw animated button border"""
        border_color = self._lighten_color(self.base_color, 80)
        
        # Animated border segments
        segment_length = 20
        gap_length = 5
        total_length = 2 * (self.rect.width + self.rect.height)
        animated_offset = (pygame.time.get_ticks() // 20) % total_length
        
        # Draw top border
        self._draw_animated_line(screen, border_color,
                               (self.rect.left, self.rect.top),
                               (self.rect.right, self.rect.top),
                               segment_length, gap_length, animated_offset)
        
        # Draw right border
        self._draw_animated_line(screen, border_color,
                               (self.rect.right, self.rect.top),
                               (self.rect.right, self.rect.bottom),
                               segment_length, gap_length, 
                               animated_offset - self.rect.width)
        
        # Draw bottom border (reverse)
        self._draw_animated_line(screen, border_color,
                               (self.rect.right, self.rect.bottom),
                               (self.rect.left, self.rect.bottom),
                               segment_length, gap_length,
                               animated_offset - self.rect.width - self.rect.height)
        
        # Draw left border (reverse)
        self._draw_animated_line(screen, border_color,
                               (self.rect.left, self.rect.bottom),
                               (self.rect.left, self.rect.top),
                               segment_length, gap_length,
                               animated_offset - 2*self.rect.width - self.rect.height)
    
    def _draw_animated_line(self, screen: pygame.Surface, color: tuple,
                          start: tuple, end: tuple, segment_length: int,
                          gap_length: int, offset: float):
        """Draw an animated segmented line"""
        line_vector = pygame.Vector2(end[0] - start[0], end[1] - start[1])
        line_length = line_vector.length()
        line_vector.normalize_ip()
        
        current_pos = offset
        while current_pos < line_length + offset:
            segment_start = max(0, current_pos - offset)
            segment_end = min(line_length, segment_start + segment_length)
            
            if segment_start < segment_end:
                draw_start = (start[0] + line_vector.x * segment_start,
                            start[1] + line_vector.y * segment_start)
                draw_end = (start[0] + line_vector.x * segment_end,
                          start[1] + line_vector.y * segment_end)
                
                pygame.draw.line(screen, color, draw_start, draw_end, 2)
            
            current_pos += segment_length + gap_length
    
    def _draw_button_text(self, screen: pygame.Surface):
        """Draw button text with glow effect"""
        text_x = self.rect.centerx - self.text_surface.get_width() // 2
        text_y = self.rect.centery - self.text_surface.get_height() // 2
        
        # Text glow
        for i in range(2):
            offset = i + 1
            glow_surf = self.font.render(self.text, True, 
                                       (*self.base_color[:3], 100 // (i + 1)))
            screen.blit(glow_surf, (text_x - offset, text_y - offset))
            screen.blit(glow_surf, (text_x + offset, text_y + offset))
        
        # Main text
        screen.blit(self.text_surface, (text_x, text_y))
    
    def _draw_interaction_effects(self, screen: pygame.Surface):
        """Draw hover and click effects"""
        if self.is_hovered:
            # Hover glow
            hover_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.rect(hover_surf, (255, 255, 255, 30), hover_surf.get_rect())
            screen.blit(hover_surf, self.rect)
        
        if self.is_clicked:
            # Click ripple effect
            click_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            ripple_radius = min(self.rect.width, self.rect.height) * 0.8
            pygame.draw.circle(click_surf, (255, 255, 255, 100),
                             (self.rect.width // 2, self.rect.height // 2),
                             ripple_radius)
            screen.blit(click_surf, self.rect)
    
    def update(self, mouse_pos: tuple, mouse_clicked: bool):
        """Update button state based on mouse interaction"""
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Update color based on state
        if self.is_clicked and mouse_clicked:
            self.current_color = self.click_color
        elif self.is_hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.base_color
        
        # Handle click state
        if self.is_hovered and mouse_clicked:
            self.is_clicked = True
        else:
            self.is_clicked = False
        
        # Start animation on hover start
        if self.is_hovered and not was_hovered:
            self.animation_progress = 0.0
    
    def is_clicked(self, mouse_pos: tuple) -> bool:
        """Check if button is being clicked"""
        return (self.rect.collidepoint(mouse_pos) and 
                pygame.mouse.get_pressed()[0])
