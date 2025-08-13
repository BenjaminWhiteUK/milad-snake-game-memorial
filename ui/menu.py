"""
Menu system - handles all menu screens and user interface interactions
"""

import pygame
import math
import time
import random

class MenuItem:
    def __init__(self, text, action=None, args=None):
        self.text = text
        self.action = action  # Function to call when selected
        self.args = args or []  # Arguments to pass to the action
        self.selected = False
        self.hover_scale = 1.0
        self.hover_growing = True
        self.hover_speed = 0.002
        self.hover_max = 1.05
        self.hover_min = 0.95
    
    def update_animation(self):
        """Update hover animation"""
        if self.selected:
            if self.hover_growing:
                self.hover_scale += self.hover_speed
                if self.hover_scale >= self.hover_max:
                    self.hover_growing = False
            else:
                self.hover_scale -= self.hover_speed
                if self.hover_scale <= self.hover_min:
                    self.hover_growing = True

class Menu:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.current_menu = "main"  # main, settings, difficulty
        self.selected_index = 0
        
        # Background animations
        self.particles = []
        self.last_particle_time = 0
        self.particle_interval = 0.2  # Time between particle spawns
        
        # Create menu items
        self.create_menus()
        
        # Animation variables
        self.title_y_offset = 0
        self.title_direction = 1
        self.title_speed = 0.2
        self.title_max_offset = 10
    
    def create_menus(self):
        """Create all menu screens"""
        self.menus = {
            "main": [
                MenuItem("Play", self.start_game),
                MenuItem("Difficulty", self.open_difficulty_menu),
                MenuItem("Settings", self.open_settings_menu),
                MenuItem("Quit", self.quit_game)
            ],
            "difficulty": [
                MenuItem("Easy", self.set_difficulty, ["EASY"]),
                MenuItem("Normal", self.set_difficulty, ["NORMAL"]),
                MenuItem("Hard", self.set_difficulty, ["HARD"]),
                MenuItem("Back", self.open_main_menu)
            ],
            "settings": [
                MenuItem("Sound: " + ("On" if self.settings.sound_enabled else "Off"), 
                         self.toggle_sound),
                MenuItem("Back", self.open_main_menu)
            ]
        }
    
    def handle_event(self, event):
        """Handle menu input events"""
        menu_items = self.menus[self.current_menu]
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(menu_items)
            elif event.key == pygame.K_RETURN:
                # Get the selected menu item and call its action
                selected_item = menu_items[self.selected_index]
                if selected_item.action:
                    selected_item.action(*selected_item.args)
    
    def render(self):
        """Render the current menu screen"""
        # Fill background
        self.screen.fill(self.settings.bg_color)
        
        # Update and render background animations
        self.update_particles()
        self.render_particles()
        
        # Get current menu items
        menu_items = self.menus[self.current_menu]
        
        # Update title animation
        self.update_title_animation()
        
        # Render title
        title_text = "SNAKE GAME"
        if self.current_menu == "difficulty":
            title_text = "DIFFICULTY"
        elif self.current_menu == "settings":
            title_text = "SETTINGS"
            
        title_surf = self.settings.title_font.render(title_text, True, self.settings.ui_highlight_color)
        title_rect = title_surf.get_rect(center=(self.settings.screen_width//2, 
                                                  self.settings.screen_height//4 + self.title_y_offset))
        self.screen.blit(title_surf, title_rect)
        
        # Render menu items
        for i, item in enumerate(menu_items):
            # Update item animation if selected
            item.selected = (i == self.selected_index)
            if item.selected:
                item.update_animation()
                text_color = self.settings.ui_highlight_color
            else:
                text_color = self.settings.ui_text_color
            
            # Render item text
            text_surf = self.settings.menu_font.render(item.text, True, text_color)
            
            # Apply scale if selected
            if item.selected:
                original_size = text_surf.get_size()
                new_size = (int(original_size[0] * item.hover_scale), 
                            int(original_size[1] * item.hover_scale))
                text_surf = pygame.transform.scale(text_surf, new_size)
            
            # Position text
            text_rect = text_surf.get_rect(center=(
                self.settings.screen_width//2,
                self.settings.screen_height//2 + i * (self.settings.menu_item_spacing + 20)
            ))
            
            # Add selector indicator if selected
            if item.selected:
                indicator_rect = pygame.Rect(
                    text_rect.left - 20, 
                    text_rect.centery - 2,
                    10, 
                    5
                )
                pygame.draw.rect(self.screen, self.settings.ui_highlight_color, indicator_rect)
                
                indicator_rect = pygame.Rect(
                    text_rect.right + 10, 
                    text_rect.centery - 2,
                    10, 
                    5
                )
                pygame.draw.rect(self.screen, self.settings.ui_highlight_color, indicator_rect)
            
            # Draw text
            self.screen.blit(text_surf, text_rect)
        
        # Render the current difficulty level if on main menu
        if self.current_menu == "main":
            diff_text = f"Difficulty: {self.settings.difficulty}"
            diff_surf = self.settings.score_font.render(diff_text, True, self.settings.ui_text_color)
            diff_rect = diff_surf.get_rect(center=(self.settings.screen_width//2, 
                                                   self.settings.screen_height - 50))
            self.screen.blit(diff_surf, diff_rect)
    
    def update_title_animation(self):
        """Update the floating animation of the title"""
        self.title_y_offset += self.title_direction * self.title_speed
        if abs(self.title_y_offset) > self.title_max_offset:
            self.title_direction *= -1
    
    def update_particles(self):
        """Update background particle animations"""
        # Add new particles occasionally
        current_time = time.time()
        if current_time - self.last_particle_time > self.particle_interval:
            self.last_particle_time = current_time
            
            # Add new particle
            particle = {
                'x': random.randint(0, self.settings.screen_width),
                'y': self.settings.screen_height + 10,
                'size': random.randint(3, 8),
                'speed': random.uniform(0.5, 2.0),
                'color': (
                    min(255, self.settings.snake_head_color[0] + random.randint(-20, 20)),
                    min(255, self.settings.snake_head_color[1] + random.randint(-20, 20)),
                    min(255, self.settings.snake_head_color[2] + random.randint(-20, 20)),
                    random.randint(50, 150)  # Alpha
                )
            }
            self.particles.append(particle)
        
        # Update existing particles
        for particle in self.particles[:]:
            particle['y'] -= particle['speed']
            
            # Remove particles that have gone off screen
            if particle['y'] < -20:
                self.particles.remove(particle)
    
    def render_particles(self):
        """Render background particles"""
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'],
                (particle['x'], particle['y']),
                particle['size']
            )
    
    # Menu action functions
    def start_game(self):
        """Start the game"""
        # This will be handled by the game state change in the main game loop
        self.game_state = "PLAYING"
    
    def open_main_menu(self):
        """Open the main menu"""
        self.current_menu = "main"
        self.selected_index = 0
    
    def open_difficulty_menu(self):
        """Open the difficulty menu"""
        self.current_menu = "difficulty"
        self.selected_index = 0
    
    def open_settings_menu(self):
        """Open the settings menu"""
        self.current_menu = "settings"
        self.selected_index = 0
        
        # Update settings text
        self.menus["settings"][0].text = "Sound: " + ("On" if self.settings.sound_enabled else "Off")
    
    def set_difficulty(self, difficulty):
        """Set the game difficulty"""
        print(f"Changing difficulty from {self.settings.difficulty} to {difficulty}")
        
        # Update settings with new difficulty
        if self.settings.change_difficulty(difficulty):
            print(f"Difficulty changed successfully")
            
            # Update menu item text
            for item in self.menus["difficulty"]:
                if item.args and item.args[0] == difficulty:
                    item.text = f"{difficulty} ✓"
                elif item.args and item.args[0] in ["EASY", "NORMAL", "HARD"]:
                    # Remove check mark from other difficulties
                    item.text = item.args[0].capitalize()
        
        # Return to main menu
        self.open_main_menu()
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.settings.sound_enabled = not self.settings.sound_enabled
        self.menus["settings"][0].text = "Sound: " + ("On" if self.settings.sound_enabled else "Off")
    
    def quit_game(self):
        """Quit the game"""
        # This will be handled by the main game loop
        pygame.event.post(pygame.event.Event(pygame.QUIT)) 