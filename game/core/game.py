"""
Main game class
"""

import pygame
import sys
import os
from typing import Dict, Any

from .settings import GameSettings
from .state_manager import StateManager, GameState
from ..entities.player import Player
from ..entities.bullet import BulletManager
from ..entities.particle import ParticleSystem
from ..systems.render_system import RenderSystem
from ..systems.collision_system import CollisionSystem
from ..systems.spawn_system import SpawnSystem
from ..systems.wave_system import WaveSystem
from ..ui.hud import HUD
from ..ui.menu import MainMenu, PauseMenu, GameOverMenu, UpgradeMenu

class NotLifeGame:
    """Main game controller"""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Create window
        self.screen = pygame.display.set_mode(
            (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT),
            pygame.DOUBLEBUF | pygame.HWSURFACE
        )
        pygame.display.set_caption(GameSettings.TITLE)
        
        # Game clock
        self.clock = pygame.time.Clock()
        self.delta_time = 0.0
        
        # Core systems
        self.state_manager = StateManager()
        self.particle_system = ParticleSystem()
        self.bullet_manager = BulletManager()
        
        # Game systems
        self.render_system = RenderSystem(self.screen)
        self.collision_system = CollisionSystem()
        self.spawn_system = SpawnSystem()
        self.wave_system = WaveSystem()
        
        # UI systems
        self.hud = HUD(self.screen)
        self.main_menu = MainMenu(self.screen)
        self.pause_menu = PauseMenu(self.screen)
        self.game_over_menu = GameOverMenu(self.screen)
        self.upgrade_menu = UpgradeMenu(self.screen)
        
        # Game objects
        self.player = None
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        
        # Game state
        self.score = 0
        self.wave_number = 0
        self.game_time = 0.0
        self.running = True
        
        # Initialize fonts
        self._load_fonts()
        
    def _load_fonts(self):
        """Load game fonts"""
        try:
            # Try to load custom font, fallback to system font
            font_path = os.path.join('game', 'assets', 'fonts', 'cyberpunk.ttf')
            if os.path.exists(font_path):
                self.title_font = pygame.font.Font(font_path, 48)
                self.ui_font = pygame.font.Font(font_path, 24)
                self.small_font = pygame.font.Font(font_path, 18)
            else:
                self.title_font = pygame.font.SysFont('courier', 48, bold=True)
                self.ui_font = pygame.font.SysFont('courier', 24)
                self.small_font = pygame.font.SysFont('courier', 18)
        except:
            # Ultimate fallback
            self.title_font = pygame.font.Font(None, 48)
            self.ui_font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.delta_time = self.clock.tick(GameSettings.FPS) / 1000.0
            self.game_time += self.delta_time
            
            self._handle_events()
            self._update()
            self._render()
            
        self._quit()
    
    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event)
                
        self._handle_continuous_input()
    
    def _handle_keydown(self, event):
        """Handle key press events"""
        if event.key == pygame.K_ESCAPE:
            if self.state_manager.is_state(GameState.PLAYING):
                self.state_manager.change_state(GameState.PAUSED)
            elif self.state_manager.is_state(GameState.PAUSED):
                self.state_manager.change_state(GameState.PLAYING)
                
        elif event.key == pygame.K_SPACE:
            if self.state_manager.is_state(GameState.MAIN_MENU):
                self._start_new_game()
    
    def _handle_mouse_click(self, event):
        """Handle mouse click events"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.state_manager.is_state(GameState.MAIN_MENU):
            self.main_menu.handle_click(mouse_pos, self)
        elif self.state_manager.is_state(GameState.PAUSED):
            self.pause_menu.handle_click(mouse_pos, self)
        elif self.state_manager.is_state(GameState.GAME_OVER):
            self.game_over_menu.handle_click(mouse_pos, self)
        elif self.state_manager.is_state(GameState.UPGRADE_SELECT):
            self.upgrade_menu.handle_click(mouse_pos, self)
    
    def _handle_continuous_input(self):
        """Handle continuous input like held keys"""
        if self.state_manager.is_state(GameState.PLAYING) and self.player:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            
            # Shooting
            if keys[pygame.K_SPACE]:
                self.player.shoot(self.player_bullets)
    
    def _update(self):
        """Update game state based on current state"""
        current_state = self.state_manager.current_state
        
        if current_state == GameState.PLAYING:
            self._update_playing()
        elif current_state == GameState.UPGRADE_SELECT:
            self.upgrade_menu.update()
    
    def _update_playing(self):
        """Update game during play state"""
        if not self.player:
            return
            
        # Update entities
        self.player.update(self.delta_time)
        self.enemies.update(self.delta_time, self.player)
        self.player_bullets.update(self.delta_time)
        self.enemy_bullets.update(self.delta_time)
        self.pickups.update(self.delta_time)
        self.particle_system.update(self.delta_time)
        
        # Update systems
        self.spawn_system.update(self.delta_time, self.enemies, self.wave_number)
        self.wave_system.update(self.delta_time, self)
        
        # Check collisions
        self.collision_system.check_collisions(
            self.player, self.enemies, self.player_bullets, 
            self.enemy_bullets, self.pickups, self.particle_system
        )
        
        # Clean up off-screen objects
        self._cleanup_objects()
        
        # Check game over
        if not self.player.is_alive():
            self.state_manager.change_state(GameState.GAME_OVER, {'score': self.score})
    
    def _render(self):
        """Render the game based on current state"""
        self.screen.fill(GameSettings.COLORS['BACKGROUND'])
        
        current_state = self.state_manager.current_state
        
        if current_state == GameState.MAIN_MENU:
            self.main_menu.draw()
        elif current_state == GameState.PLAYING:
            self._render_playing()
        elif current_state == GameState.PAUSED:
            self._render_playing()
            self.pause_menu.draw()
        elif current_state == GameState.GAME_OVER:
            self._render_playing()
            self.game_over_menu.draw(self.score)
        elif current_state == GameState.UPGRADE_SELECT:
            self._render_playing()
            self.upgrade_menu.draw()
            
        pygame.display.flip()
    
    def _render_playing(self):
        """Render gameplay elements"""
        # Draw background effects
        self.render_system.draw_background(self.wave_number)
        
        # Draw game objects
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        for bullet in self.player_bullets:
            bullet.draw(self.screen)
            
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)
            
        for pickup in self.pickups:
            pickup.draw(self.screen)
            
        # Draw player and particles
        if self.player:
            self.player.draw(self.screen)
            
        self.particle_system.draw(self.screen)
        
        # Draw HUD
        if self.player:
            self.hud.draw(
                self.player.health, self.player.max_health,
                self.player.shield, self.player.max_shield,
                self.player.experience, self.player.experience_to_level,
                self.player.level, self.score, self.wave_number,
                self.wave_system.get_wave_progress()
            )
    
    def _cleanup_objects(self):
        """Remove off-screen objects"""
        for bullet in self.player_bullets:
            if not self._is_on_screen(bullet.rect):
                bullet.kill()
                
        for bullet in self.enemy_bullets:
            if not self._is_on_screen(bullet.rect):
                bullet.kill()
                
        for enemy in self.enemies:
            if not self._is_on_screen(enemy.rect):
                enemy.kill()
    
    def _is_on_screen(self, rect: pygame.Rect) -> bool:
        """Check if a rectangle is on screen"""
        return (rect.right > 0 and rect.left < GameSettings.SCREEN_WIDTH and
                rect.bottom > 0 and rect.top < GameSettings.SCREEN_HEIGHT)
    
    def _start_new_game(self):
        """Start a new game"""
        self.player = Player()
        self.enemies.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.pickups.empty()
        self.particle_system.clear()
        
        self.score = 0
        self.wave_number = 1
        self.game_time = 0.0
        
        self.wave_system.start_wave(1)
        self.state_manager.change_state(GameState.PLAYING)
    
    def _quit(self):
        """Clean up and quit"""
        pygame.quit()
        sys.exit()
