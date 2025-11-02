"""
Heads-Up Display (HUD) system
"""

import pygame
import math
from typing import Tuple
from ..core.settings import GameSettings

class HUD:
    """Game HUD displaying health, score, wave info, etc."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 32)
        
        # HUD elements positioning
        self.margin = 20
        self.bar_width = 200
        self.bar_height = 20
        self.icon_size = 30
        
        # Animation states
        self.wave_alert_timer = 0.0
        self.damage_flash_timer = 0.0
        self.score_pop_timer = 0.0
        self.last_score = 0
        
    def draw(self, health: int, max_health: int, shield: int, max_shield: int,
             experience: int, experience_to_level: int, level: int,
             score: int, wave: int, wave_progress: float):
        """Draw all HUD elements"""
        
        # Draw background panels
        self._draw_hud_background()
        
        # Draw health and shield bars
        self._draw_health_bar(health, max_health)
        self._draw_shield_bar(shield, max_shield)
        
        # Draw experience bar
        self._draw_experience_bar(experience, experience_to_level, level)
        
        # Draw score and wave info
        self._draw_score_display(score)
        self._draw_wave_info(wave, wave_progress)
        
        # Draw mini-map or radar
        self._draw_radar()
        
        # Draw weapon info
        self._draw_weapon_info()
        
        # Draw animated alerts
        self._draw_alerts()
    
    def _draw_hud_background(self):
        """Draw HUD background elements"""
        # Top bar
        top_bar = pygame.Surface((GameSettings.SCREEN_WIDTH, 40), pygame.SRCALPHA)
        top_bar.fill((10, 10, 20, 200))
        self.screen.blit(top_bar, (0, 0))
        
        # Bottom bar
        bottom_bar = pygame.Surface((GameSettings.SCREEN_WIDTH, 60), pygame.SRCALPHA)
        bottom_bar.fill((10, 10, 20, 180))
        self.screen.blit(bottom_bar, (0, GameSettings.SCREEN_HEIGHT - 60))
        
        # Side panels
        left_panel = pygame.Surface((200, GameSettings.SCREEN_HEIGHT - 100), pygame.SRCALPHA)
        left_panel.fill((15, 15, 25, 150))
        self.screen.blit(left_panel, (0, 40))
        
        right_panel = pygame.Surface((180, GameSettings.SCREEN_HEIGHT - 100), pygame.SRCALPHA)
        right_panel.fill((15, 15, 25, 150))
        self.screen.blit(right_panel, (GameSettings.SCREEN_WIDTH - 180, 40))
    
    def _draw_health_bar(self, health: int, max_health: int):
        """Draw health bar with cyberpunk style"""
        bar_rect = pygame.Rect(self.margin, self.margin, self.bar_width, self.bar_height)
        health_ratio = health / max_health
        
        # Health bar color based on health level
        if health_ratio > 0.6:
            bar_color = GameSettings.COLORS['NEON_GREEN']
        elif health_ratio > 0.3:
            bar_color = (255, 165, 0)  # Orange
        else:
            bar_color = GameSettings.COLORS['WARNING']
        
        # Draw background
        pygame.draw.rect(self.screen, (50, 50, 50), bar_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), bar_rect, 2)
        
        # Draw health fill
        if health_ratio > 0:
            fill_rect = pygame.Rect(
                bar_rect.x + 2, bar_rect.y + 2,
                int((bar_rect.width - 4) * health_ratio), bar_rect.height - 4
            )
            pygame.draw.rect(self.screen, bar_color, fill_rect)
            
            # Draw inner glow
            glow_surf = pygame.Surface((fill_rect.width, fill_rect.height), pygame.SRCALPHA)
            for i in range(3):
                alpha = 80 - i * 25
                glow_rect = pygame.Rect(i, i, fill_rect.width - i*2, fill_rect.height - i*2)
                pygame.draw.rect(glow_surf, (*bar_color[:3], alpha), glow_rect, 1)
            self.screen.blit(glow_surf, fill_rect)
        
        # Draw health text
        health_text = f"HP: {health}/{max_health}"
        text_surf = self.font.render(health_text, True, GameSettings.COLORS['TEXT'])
        self.screen.blit(text_surf, (bar_rect.x, bar_rect.y - 25))
        
        # Draw health icon
        self._draw_health_icon(bar_rect.x + bar_rect.width + 10, bar_rect.y)
    
    def _draw_health_icon(self, x: int, y: int):
        """Draw health icon"""
        icon_rect = pygame.Rect(x, y, self.icon_size, self.icon_size)
        
        # Draw heart icon
        points = [
            (x + 15, y + 5),
            (x + 25, y + 12),
            (x + 15, y + 25),
            (x + 5, y + 12)
        ]
        pygame.draw.polygon(self.screen, GameSettings.COLORS['WARNING'], points)
        pygame.draw.polygon(self.screen, (255, 200, 200), points, 2)
    
    def _draw_shield_bar(self, shield: int, max_shield: int):
        """Draw shield bar"""
        bar_rect = pygame.Rect(self.margin, self.margin + 40, self.bar_width, self.bar_height)
        shield_ratio = shield / max_shield if max_shield > 0 else 0
        
        # Draw background
        pygame.draw.rect(self.screen, (50, 50, 50), bar_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), bar_rect, 2)
        
        # Draw shield fill
        if shield_ratio > 0:
            fill_rect = pygame.Rect(
                bar_rect.x + 2, bar_rect.y + 2,
                int((bar_rect.width - 4) * shield_ratio), bar_rect.height - 4
            )
            pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_BLUE'], fill_rect)
            
            # Draw animated shield effect
            if shield_ratio > 0.5:
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
                alpha = int(100 * pulse)
                glow_surf = pygame.Surface((fill_rect.width, fill_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (0, 150, 255, alpha), glow_surf.get_rect())
                self.screen.blit(glow_surf, fill_rect)
        
        # Draw shield text
        shield_text = f"SHIELD: {shield}/{max_shield}"
        text_surf = self.font.render(shield_text, True, GameSettings.COLORS['TEXT'])
        self.screen.blit(text_surf, (bar_rect.x, bar_rect.y - 25))
    
    def _draw_experience_bar(self, experience: int, experience_to_level: int, level: int):
        """Draw experience bar"""
        bar_rect = pygame.Rect(self.margin, GameSettings.SCREEN_HEIGHT - 50, 
                             self.bar_width, 15)
        exp_ratio = experience / experience_to_level if experience_to_level > 0 else 0
        
        # Draw background
        pygame.draw.rect(self.screen, (30, 30, 40), bar_rect)
        pygame.draw.rect(self.screen, (80, 80, 100), bar_rect, 1)
        
        # Draw experience fill
        if exp_ratio > 0:
            fill_rect = pygame.Rect(
                bar_rect.x + 1, bar_rect.y + 1,
                int((bar_rect.width - 2) * exp_ratio), bar_rect.height - 2
            )
            pygame.draw.rect(self.screen, GameSettings.COLORS['EXPERIENCE'], fill_rect)
            
            # Draw glowing particles in exp bar
            if exp_ratio > 0.8:  # Close to level up
                particle_count = int(3 * exp_ratio)
                for i in range(particle_count):
                    particle_x = fill_rect.x + random.randint(0, fill_rect.width)
                    particle_y = fill_rect.y + random.randint(0, fill_rect.height)
                    size = random.randint(1, 2)
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                     (particle_x, particle_y), size)
        
        # Draw level text
        level_text = f"LEVEL {level}"
        text_surf = self.font.render(level_text, True, GameSettings.COLORS['TEXT'])
        self.screen.blit(text_surf, (bar_rect.x + bar_rect.width + 10, bar_rect.y - 2))
        
        # Draw experience text
        exp_text = f"EXP: {experience}/{experience_to_level}"
        exp_surf = self.small_font.render(exp_text, True, (200, 200, 200))
        self.screen.blit(exp_surf, (bar_rect.x, bar_rect.y - 20))
    
    def _draw_score_display(self, score: int):
        """Draw score display with animation"""
        score_x = GameSettings.SCREEN_WIDTH - 200
        score_y = self.margin
        
        # Animate score change
        if score != self.last_score:
            self.score_pop_timer = 0.3
            self.last_score = score
        
        # Calculate scale for pop animation
        scale = 1.0
        if self.score_pop_timer > 0:
            scale = 1.0 + (self.score_pop_timer * 0.5)
            self.score_pop_timer -= 0.016  # Roughly 60 FPS
        
        # Draw score background
        score_bg = pygame.Rect(score_x - 10, score_y - 5, 180, 40)
        pygame.draw.rect(self.screen, (20, 20, 30, 200), score_bg)
        pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_PURPLE'], score_bg, 2)
        
        # Draw score text
        score_text = f"SCORE: {score:08d}"
        text_surf = self.title_font.render(score_text, True, GameSettings.COLORS['NEON_CYAN'])
        
        # Apply scale transformation
        if scale != 1.0:
            scaled_size = (int(text_surf.get_width() * scale), 
                         int(text_surf.get_height() * scale))
            scaled_surf = pygame.transform.scale(text_surf, scaled_size)
            draw_x = score_x - (scaled_surf.get_width() - text_surf.get_width()) // 2
            draw_y = score_y - (scaled_surf.get_height() - text_surf.get_height()) // 2
            self.screen.blit(scaled_surf, (draw_x, draw_y))
        else:
            self.screen.blit(text_surf, (score_x, score_y))
    
    def _draw_wave_info(self, wave: int, wave_progress: float):
        """Draw wave information"""
        wave_x = GameSettings.SCREEN_WIDTH - 200
        wave_y = self.margin + 50
        
        # Draw wave background
        wave_bg = pygame.Rect(wave_x - 10, wave_y - 5, 180, 60)
        pygame.draw.rect(self.screen, (20, 20, 30, 200), wave_bg)
        pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_PINK'], wave_bg, 2)
        
        # Draw wave text
        wave_text = f"WAVE {wave}"
        wave_surf = self.font.render(wave_text, True, GameSettings.COLORS['NEON_PINK'])
        self.screen.blit(wave_surf, (wave_x, wave_y))
        
        # Draw wave progress bar
        progress_rect = pygame.Rect(wave_x, wave_y + 30, 160, 8)
        pygame.draw.rect(self.screen, (50, 50, 50), progress_rect)
        
        if wave_progress > 0:
            fill_width = int(progress_rect.width * wave_progress)
            fill_rect = pygame.Rect(progress_rect.x, progress_rect.y, fill_width, progress_rect.height)
            pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_PINK'], fill_rect)
            
            # Draw progress text
            progress_text = f"{int(wave_progress * 100)}%"
            progress_surf = self.small_font.render(progress_text, True, (200, 200, 200))
            self.screen.blit(progress_surf, (wave_x + 70, wave_y + 15))
    
    def _draw_radar(self):
        """Draw mini radar showing enemy positions"""
        radar_center_x = GameSettings.SCREEN_WIDTH - 100
        radar_center_y = GameSettings.SCREEN_HEIGHT - 150
        radar_radius = 40
        
        # Draw radar background
        pygame.draw.circle(self.screen, (10, 20, 30), 
                         (radar_center_x, radar_center_y), radar_radius)
        pygame.draw.circle(self.screen, GameSettings.COLORS['NEON_GREEN'], 
                         (radar_center_x, radar_center_y), radar_radius, 2)
        
        # Draw radar circles
        for i in range(1, 4):
            radius = radar_radius * i // 3
            pygame.draw.circle(self.screen, (30, 60, 40), 
                             (radar_center_x, radar_center_y), radius, 1)
        
        # Draw radar sweep (rotating line)
        sweep_angle = (pygame.time.get_ticks() * 0.002) % (2 * math.pi)
        end_x = radar_center_x + math.cos(sweep_angle) * radar_radius
        end_y = radar_center_y + math.sin(sweep_angle) * radar_radius
        pygame.draw.line(self.screen, GameSettings.COLORS['NEON_GREEN'], 
                        (radar_center_x, radar_center_y), (end_x, end_y), 2)
        
        # Draw radar title
        radar_text = "RADAR"
        text_surf = self.small_font.render(radar_text, True, GameSettings.COLORS['NEON_GREEN'])
        self.screen.blit(text_surf, (radar_center_x - 20, radar_center_y - 60))
    
    def _draw_weapon_info(self):
        """Draw current weapon information"""
        weapon_x = 20
        weapon_y = GameSettings.SCREEN_HEIGHT - 100
        
        # Draw weapon background
        weapon_bg = pygame.Rect(weapon_x - 10, weapon_y - 10, 180, 80)
        pygame.draw.rect(self.screen, (20, 20, 30, 200), weapon_bg)
        pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_BLUE'], weapon_bg, 2)
        
        # Draw weapon name
        weapon_name = "PLASMA CANNON"
        name_surf = self.font.render(weapon_name, True, GameSettings.COLORS['NEON_BLUE'])
        self.screen.blit(name_surf, (weapon_x, weapon_y))
        
        # Draw ammo/cooldown
        ammo_text = "READY"
        ammo_surf = self.small_font.render(ammo_text, True, (200, 200, 200))
        self.screen.blit(ammo_surf, (weapon_x, weapon_y + 25))
        
        # Draw damage info
        damage_text = "DMG: 25"
        damage_surf = self.small_font.render(damage_text, True, (200, 200, 200))
        self.screen.blit(damage_surf, (weapon_x, weapon_y + 45))
    
    def _draw_alerts(self):
        """Draw alert messages and warnings"""
        alert_y = 100
        
        # Draw low health warning
        # This would be triggered by game state
        # if health_ratio < 0.3:
        #     self._draw_alert("WARNING: CRITICAL HEALTH", alert_y, GameSettings.COLORS['WARNING'])
        #     alert_y += 40
        
        # Draw wave start alert
        if self.wave_alert_timer > 0:
            self._draw_alert("INCOMING WAVE!", alert_y, GameSettings.COLORS['NEON_PINK'])
            self.wave_alert_timer -= 0.016
    
    def _draw_alert(self, message: str, y: int, color: Tuple[int, int, int]):
        """Draw a single alert message"""
        alert_bg = pygame.Rect(GameSettings.SCREEN_WIDTH // 2 - 150, y, 300, 40)
        pygame.draw.rect(self.screen, (20, 20, 30, 220), alert_bg)
        pygame.draw.rect(self.screen, color, alert_bg, 3)
        
        # Pulsing effect
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
        pulse_alpha = int(100 * pulse)
        pulse_surf = pygame.Surface((alert_bg.width, alert_bg.height), pygame.SRCALPHA)
        pygame.draw.rect(pulse_surf, (*color[:3], pulse_alpha), pulse_surf.get_rect(), 2)
        self.screen.blit(pulse_surf, alert_bg)
        
        # Alert text
        text_surf = self.font.render(message, True, color)
        text_x = alert_bg.centerx - text_surf.get_width() // 2
        text_y = alert_bg.centery - text_surf.get_height() // 2
        self.screen.blit(text_surf, (text_x, text_y))
    
    def show_wave_alert(self, wave_number: int):
        """Show wave start alert"""
        self.wave_alert_timer = 3.0  # Show for 3 seconds
    
    def update(self, delta_time: float):
        """Update HUD animations"""
        if self.score_pop_timer > 0:
            self.score_pop_timer -= delta_time
        
        if self.wave_alert_timer > 0:
            self.wave_alert_timer -= delta_time
        
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= delta_time
