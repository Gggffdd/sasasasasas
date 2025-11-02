"""
Menu system for main menu, pause, game over, etc.
"""

import pygame
import math
from typing import List, Dict, Any, Callable, Optional
from ..core.settings import GameSettings
from .buttons import Button

class BaseMenu:
    """Base class for all menus"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.buttons: List[Button] = []
        self.title_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.background_alpha = 180
        self.animation_time = 0.0
        
    def update(self, delta_time: float = 0.0):
        """Update menu animations"""
        self.animation_time += delta_time
        
    def draw(self):
        """Draw the menu (to be implemented by subclasses)"""
        pass
    
    def handle_click(self, mouse_pos: tuple, game=None):
        """Handle mouse clicks on buttons"""
        for button in self.buttons:
            if button.is_clicked(mouse_pos):
                self.on_button_click(button.action, game)
                return True
        return False
    
    def on_button_click(self, action: str, game=None):
        """Handle button actions (to be implemented by subclasses)"""
        pass
    
    def draw_cyberpunk_background(self):
        """Draw cyberpunk-style background for menus"""
        # Dark background with transparency
        overlay = pygame.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 15, self.background_alpha))
        self.screen.blit(overlay, (0, 0))
        
        # Animated grid lines
        grid_surf = pygame.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Vertical lines
        for x in range(0, GameSettings.SCREEN_WIDTH, 40):
            offset = math.sin(self.animation_time + x * 0.01) * 3
            alpha = 30 + int(math.sin(self.animation_time * 2 + x * 0.02) * 20)
            color = (0, 100, 200, alpha)
            pygame.draw.line(grid_surf, color, 
                           (x + offset, 0), (x + offset, GameSettings.SCREEN_HEIGHT), 1)
        
        # Horizontal lines
        for y in range(0, GameSettings.SCREEN_HEIGHT, 40):
            offset = math.cos(self.animation_time + y * 0.01) * 3
            alpha = 30 + int(math.cos(self.animation_time * 2 + y * 0.02) * 20)
            color = (0, 100, 200, alpha)
            pygame.draw.line(grid_surf, color, 
                           (0, y + offset), (GameSettings.SCREEN_WIDTH, y + offset), 1)
        
        self.screen.blit(grid_surf, (0, 0))
        
        # Pulsing nodes at line intersections
        node_surf = pygame.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(40, GameSettings.SCREEN_WIDTH, 80):
            for y in range(40, GameSettings.SCREEN_HEIGHT, 80):
                pulse = (math.sin(self.animation_time * 3 + x + y) + 1) * 0.5
                size = 2 + pulse * 2
                alpha = 50 + int(pulse * 100)
                color = (0, 200, 255, alpha)
                pygame.draw.circle(node_surf, color, (x, y), size)
        
        self.screen.blit(node_surf, (0, 0))

class MainMenu(BaseMenu):
    """Main menu screen"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.background_alpha = 220
        self._create_buttons()
        
    def _create_buttons(self):
        """Create main menu buttons"""
        center_x = GameSettings.SCREEN_WIDTH // 2
        button_y = 300
        
        self.buttons = [
            Button(center_x - 150, button_y, 300, 60, "START MISSION", 
                  "start", GameSettings.COLORS['NEON_GREEN']),
            Button(center_x - 150, button_y + 80, 300, 60, "UPGRADES", 
                  "upgrades", GameSettings.COLORS['NEON_BLUE']),
            Button(center_x - 150, button_y + 160, 300, 60, "OPTIONS", 
                  "options", GameSettings.COLORS['NEON_PURPLE']),
            Button(center_x - 150, button_y + 240, 300, 60, "QUIT", 
                  "quit", GameSettings.COLORS['NEON_PINK'])
        ]
    
    def draw(self):
        """Draw the main menu"""
        # Draw background
        self.draw_cyberpunk_background()
        
        # Draw title with glow effect
        title_text = "NOTLIFE"
        subtitle_text = "CYBER DEFENSE PROTOCOL"
        
        # Main title with multiple glow passes
        for i in range(3):
            offset = (i + 1) * 2
            alpha = 100 - i * 30
            glow_color = (255, 20, 147, alpha)
            
            # Top glow
            glow_surf = self.title_font.render(title_text, True, glow_color)
            self.screen.blit(glow_surf, 
                           (GameSettings.SCREEN_WIDTH // 2 - glow_surf.get_width() // 2 - offset, 
                            100 - offset))
            # Bottom glow
            self.screen.blit(glow_surf, 
                           (GameSettings.SCREEN_WIDTH // 2 - glow_surf.get_width() // 2 + offset, 
                            100 + offset))
        
        # Main title
        title_surf = self.title_font.render(title_text, True, GameSettings.COLORS['NEON_PINK'])
        self.screen.blit(title_surf, 
                        (GameSettings.SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 100))
        
        # Subtitle
        subtitle_surf = self.font.render(subtitle_text, True, GameSettings.COLORS['NEON_CYAN'])
        self.screen.blit(subtitle_surf, 
                        (GameSettings.SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, 180))
        
        # Draw version info
        version_text = "v1.0.0 | CYBERDEV STUDIO"
        version_surf = self.small_font.render(version_text, True, (150, 150, 150))
        self.screen.blit(version_surf, (20, GameSettings.SCREEN_HEIGHT - 30))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, self.animation_time)
        
        # Draw animated preview
        self._draw_game_preview()
    
    def _draw_game_preview(self):
        """Draw animated game preview"""
        preview_rect = pygame.Rect(GameSettings.SCREEN_WIDTH - 350, 300, 300, 200)
        
        # Preview background
        pygame.draw.rect(self.screen, (10, 15, 25), preview_rect)
        pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_BLUE'], preview_rect, 2)
        
        # Preview title
        preview_text = "LIVE FEED"
        text_surf = self.small_font.render(preview_text, True, GameSettings.COLORS['NEON_BLUE'])
        self.screen.blit(text_surf, (preview_rect.centerx - text_surf.get_width() // 2, 
                                   preview_rect.y - 25))
        
        # Animated elements in preview
        center_x = preview_rect.centerx
        center_y = preview_rect.centery
        
        # Player ship
        ship_points = [
            (center_x, center_y - 20),
            (center_x - 15, center_y + 20),
            (center_x + 15, center_y + 20)
        ]
        pygame.draw.polygon(self.screen, GameSettings.COLORS['NEON_GREEN'], ship_points)
        
        # Enemy dots
        enemy_count = 5
        for i in range(enemy_count):
            angle = (self.animation_time + i * 0.5) % (2 * math.pi)
            radius = 70 + math.sin(self.animation_time * 2 + i) * 10
            enemy_x = center_x + math.cos(angle) * radius
            enemy_y = center_y + math.sin(angle) * radius
            
            # Pulsing enemy dots
            pulse = (math.sin(self.animation_time * 3 + i) + 1) * 0.5
            size = 3 + int(pulse * 2)
            pygame.draw.circle(self.screen, GameSettings.COLORS['NEON_PINK'], 
                             (int(enemy_x), int(enemy_y)), size)
        
        # Bullet trails
        for i in range(3):
            bullet_y = center_y - 30 - i * 10 - (self.animation_time * 50) % 50
            pygame.draw.line(self.screen, GameSettings.COLORS['NEON_BLUE'],
                           (center_x - 2, bullet_y), (center_x - 2, bullet_y + 10), 2)
            pygame.draw.line(self.screen, GameSettings.COLORS['NEON_BLUE'],
                           (center_x + 2, bullet_y), (center_x + 2, bullet_y + 10), 2)
    
    def on_button_click(self, action: str, game=None):
        """Handle main menu button actions"""
        if action == "start" and game:
            game.state_manager.change_state(game.state_manager.GameState.PLAYING)
            game._start_new_game()
        elif action == "upgrades":
            print("Upgrades menu not implemented")
        elif action == "options":
            print("Options menu not implemented")
        elif action == "quit" and game:
            game.running = False

class PauseMenu(BaseMenu):
    """Pause menu screen"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.background_alpha = 200
        self._create_buttons()
    
    def _create_buttons(self):
        """Create pause menu buttons"""
        center_x = GameSettings.SCREEN_WIDTH // 2
        button_y = 300
        
        self.buttons = [
            Button(center_x - 150, button_y, 300, 60, "RESUME", 
                  "resume", GameSettings.COLORS['NEON_GREEN']),
            Button(center_x - 150, button_y + 80, 300, 60, "RESTART", 
                  "restart", GameSettings.COLORS['NEON_BLUE']),
            Button(center_x - 150, button_y + 160, 300, 60, "MAIN MENU", 
                  "main_menu", GameSettings.COLORS['NEON_PURPLE']),
            Button(center_x - 150, button_y + 240, 300, 60, "QUIT", 
                  "quit", GameSettings.COLORS['NEON_PINK'])
        ]
    
    def draw(self):
        """Draw the pause menu"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw menu background
        menu_rect = pygame.Rect(GameSettings.SCREEN_WIDTH // 2 - 200, 150, 400, 400)
        pygame.draw.rect(self.screen, (15, 20, 30, 240), menu_rect)
        pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_CYAN'], menu_rect, 3)
        
        # Draw title
        title_text = "MISSION PAUSED"
        title_surf = self.title_font.render(title_text, True, GameSettings.COLORS['NEON_CYAN'])
        self.screen.blit(title_surf, 
                        (GameSettings.SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 180))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, self.animation_time)
        
        # Draw pause icon
        self._draw_pause_icon()
    
    def _draw_pause_icon(self):
        """Draw pause icon"""
        icon_x = GameSettings.SCREEN_WIDTH // 2
        icon_y = 250
        icon_size = 40
        
        # Draw two vertical bars
        bar_width = 10
        bar_spacing = 15
        
        left_bar = pygame.Rect(icon_x - bar_spacing - bar_width, icon_y - icon_size // 2,
                             bar_width, icon_size)
        right_bar = pygame.Rect(icon_x + bar_spacing, icon_y - icon_size // 2,
                              bar_width, icon_size)
        
        pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_CYAN'], left_bar)
        pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_CYAN'], right_bar)
    
    def on_button_click(self, action: str, game=None):
        """Handle pause menu button actions"""
        if action == "resume" and game:
            game.state_manager.change_state(game.state_manager.GameState.PLAYING)
        elif action == "restart" and game:
            game._start_new_game()
            game.state_manager.change_state(game.state_manager.GameState.PLAYING)
        elif action == "main_menu" and game:
            game.state_manager.change_state(game.state_manager.GameState.MAIN_MENU)
        elif action == "quit" and game:
            game.running = False

class GameOverMenu(BaseMenu):
    """Game over screen"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.background_alpha = 220
        self._create_buttons()
        self.final_score = 0
    
    def _create_buttons(self):
        """Create game over menu buttons"""
        center_x = GameSettings.SCREEN_WIDTH // 2
        button_y = 400
        
        self.buttons = [
            Button(center_x - 150, button_y, 300, 60, "PLAY AGAIN", 
                  "restart", GameSettings.COLORS['NEON_GREEN']),
            Button(center_x - 150, button_y + 80, 300, 60, "MAIN MENU", 
                  "main_menu", GameSettings.COLORS['NEON_BLUE']),
            Button(center_x - 150, button_y + 160, 300, 60, "QUIT", 
                  "quit", GameSettings.COLORS['NEON_PINK'])
        ]
    
    def draw(self, final_score: int = 0):
        """Draw the game over menu"""
        self.final_score = final_score
        
        # Draw background
        self.draw_cyberpunk_background()
        
        # Draw menu panel
        menu_rect = pygame.Rect(GameSettings.SCREEN_WIDTH // 2 - 250, 150, 500, 450)
        pygame.draw.rect(self.screen, (20, 10, 15, 240), menu_rect)
        pygame.draw.rect(self.screen, GameSettings.COLORS['WARNING'], menu_rect, 3)
        
        # Draw title with warning effect
        title_text = "MISSION FAILED"
        subtitle_text = "SYSTEM BREACH DETECTED"
        
        # Flashing title
        flash_alpha = int((math.sin(self.animation_time * 5) + 1) * 0.5 * 255)
        title_surf = self.title_font.render(title_text, True, GameSettings.COLORS['WARNING'])
        self.screen.blit(title_surf, 
                        (GameSettings.SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 180))
        
        # Subtitle
        subtitle_surf = self.font.render(subtitle_text, True, (200, 100, 100))
        self.screen.blit(subtitle_surf, 
                        (GameSettings.SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, 250))
        
        # Draw score
        score_text = f"FINAL SCORE: {self.final_score:08d}"
        score_surf = self.font.render(score_text, True, GameSettings.COLORS['NEON_CYAN'])
        self.screen.blit(score_surf, 
                        (GameSettings.SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 320))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, self.animation_time)
        
        # Draw failure analysis
        self._draw_failure_analysis()
    
    def _draw_failure_analysis(self):
        """Draw mission failure analysis"""
        analysis_y = 500
        
        # Analysis title
        analysis_title = "MISSION ANALYSIS:"
        title_surf = self.small_font.render(analysis_title, True, (200, 200, 200))
        self.screen.blit(title_surf, (GameSettings.SCREEN_WIDTH // 2 - 200, analysis_y))
        
        # Analysis points (would be dynamic based on game state)
        analysis_points = [
            "• Primary systems compromised",
            "• Defense grid overloaded", 
            "• Enemy saturation: Critical",
            "• Recommend tactical retreat"
        ]
        
        for i, point in enumerate(analysis_points):
            point_surf = self.small_font.render(point, True, (150, 150, 150))
            self.screen.blit(point_surf, (GameSettings.SCREEN_WIDTH // 2 - 180, analysis_y + 30 + i * 25))
    
    def on_button_click(self, action: str, game=None):
        """Handle game over menu button actions"""
        if action == "restart" and game:
            game._start_new_game()
            game.state_manager.change_state(game.state_manager.GameState.PLAYING)
        elif action == "main_menu" and game:
            game.state_manager.change_state(game.state_manager.GameState.MAIN_MENU)
        elif action == "quit" and game:
            game.running = False

class UpgradeMenu(BaseMenu):
    """Upgrade selection screen"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.background_alpha = 200
        self.upgrades = []
        self.selected_upgrade = None
        self._create_upgrades()
        self._create_buttons()
    
    def _create_upgrades(self):
        """Create available upgrades"""
        self.upgrades = [
            {
                'name': 'PLASMA CANNON',
                'description': 'Increase damage output by 25%',
                'cost': 50,
                'type': 'damage',
                'icon': '💥'
            },
            {
                'name': 'RAPID FIRE', 
                'description': 'Increase fire rate by 15%',
                'cost': 75,
                'type': 'fire_rate',
                'icon': '⚡'
            },
            {
                'name': 'REINFORCED HULL',
                'description': 'Increase maximum health by 30%',
                'cost': 100, 
                'type': 'health',
                'icon': '🛡️'
            },
            {
                'name': 'SHIELD BOOST',
                'description': 'Increase shield capacity by 25%',
                'cost': 80,
                'type': 'shield', 
                'icon': '🔰'
            },
            {
                'name': 'THRUSTERS',
                'description': 'Increase movement speed by 15%',
                'cost': 60,
                'type': 'speed',
                'icon': '🚀'
            }
        ]
    
    def _create_buttons(self):
        """Create upgrade menu buttons"""
        center_x = GameSettings.SCREEN_WIDTH // 2
        
        self.buttons = [
            Button(center_x - 150, 550, 300, 60, "CONFIRM SELECTION", 
                  "confirm", GameSettings.COLORS['NEON_GREEN']),
            Button(center_x - 150, 620, 300, 60, "BACK TO GAME", 
                  "back", GameSettings.COLORS['NEON_BLUE'])
        ]
    
    def draw(self):
        """Draw the upgrade menu"""
        # Draw background
        self.draw_cyberpunk_background()
        
        # Draw title
        title_text = "SYSTEM UPGRADES"
        title_surf = self.title_font.render(title_text, True, GameSettings.COLORS['NEON_PURPLE'])
        self.screen.blit(title_surf, 
                        (GameSettings.SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 80))
        
        # Draw upgrade cards
        self._draw_upgrade_cards()
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, self.animation_time)
    
    def _draw_upgrade_cards(self):
        """Draw upgrade selection cards"""
        card_width = 220
        card_height = 180
        card_margin = 20
        start_x = (GameSettings.SCREEN_WIDTH - (len(self.upgrades) * (card_width + card_margin))) // 2
        
        for i, upgrade in enumerate(self.upgrades):
            card_x = start_x + i * (card_width + card_margin)
            card_y = 150
            
            # Card background
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            is_selected = (self.selected_upgrade == upgrade['type'])
            
            # Card color based on selection
            if is_selected:
                card_color = (30, 20, 40)
                border_color = GameSettings.COLORS['NEON_GREEN']
            else:
                card_color = (20, 20, 30)
                border_color = GameSettings.COLORS['NEON_BLUE']
            
            pygame.draw.rect(self.screen, card_color, card_rect)
            pygame.draw.rect(self.screen, border_color, card_rect, 3)
            
            # Draw upgrade icon
            icon_text = upgrade['icon']
            icon_surf = self.font.render(icon_text, True, GameSettings.COLORS['NEON_CYAN'])
            self.screen.blit(icon_surf, (card_x + 20, card_y + 15))
            
            # Draw upgrade name
            name_surf = self.small_font.render(upgrade['name'], True, GameSettings.COLORS['TEXT'])
            self.screen.blit(name_surf, (card_x + 60, card_y + 20))
            
            # Draw upgrade description
            desc_lines = self._wrap_text(upgrade['description'], self.small_font, card_width - 40)
            for j, line in enumerate(desc_lines):
                desc_surf = self.small_font.render(line, True, (180, 180, 180))
                self.screen.blit(desc_surf, (card_x + 20, card_y + 60 + j * 20))
            
            # Draw upgrade cost
            cost_text = f"COST: {upgrade['cost']} SP"
            cost_surf = self.small_font.render(cost_text, True, GameSettings.COLORS['NEON_PINK'])
            self.screen.blit(cost_surf, (card_x + 20, card_y + 140))
            
            # Draw selection indicator
            if is_selected:
                select_indicator = pygame.Rect(card_x - 5, card_y - 5, 
                                            card_width + 10, card_height + 10)
                pygame.draw.rect(self.screen, GameSettings.COLORS['NEON_GREEN'], select_indicator, 2)
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def handle_click(self, mouse_pos: tuple, game=None):
        """Handle clicks on upgrades and buttons"""
        # Check upgrade card clicks
        card_width = 220
        card_height = 180
        card_margin = 20
        start_x = (GameSettings.SCREEN_WIDTH - (len(self.upgrades) * (card_width + card_margin))) // 2
        
        for i, upgrade in enumerate(self.upgrades):
            card_x = start_x + i * (card_width + card_margin)
            card_y = 150
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            if card_rect.collidepoint(mouse_pos):
                self.selected_upgrade = upgrade['type']
                return True
        
        # Check button clicks
        return super().handle_click(mouse_pos, game)
    
    def on_button_click(self, action: str, game=None):
        """Handle upgrade menu button actions"""
        if action == "confirm" and game and self.selected_upgrade:
            if game.player.apply_upgrade(self.selected_upgrade):
                # Upgrade applied successfully
                game.state_manager.change_state(game.state_manager.GameState.PLAYING)
            else:
                # Not enough skill points
                print("Not enough skill points!")
        elif action == "back" and game:
            game.state_manager.change_state(game.state_manager.GameState.PLAYING)
