"""
Game settings and configuration
"""

import pygame
# Import user configuration
from utils.config import *

class Settings:
    def __init__(self):
        # Screen settings
        self.screen_width = 800
        self.screen_height = 600
        self.fps = 60
        
        # Grid settings
        self.grid_size = 20
        
        # Color settings
        self.bg_color = (15, 15, 20)
        self.grid_color = (30, 30, 40)
        
        self.snake_head_color = (50, 200, 50)
        self.snake_body_color = (20, 140, 20)
        
        self.food_color = (230, 50, 50)
        self.special_food_color = (230, 230, 50)
        
        self.ui_text_color = (230, 230, 230)
        self.ui_highlight_color = (100, 200, 255)
        
        # Special features - use config values
        self.mario_enabled = MARIO_ENABLED
        self.mario_stay_duration = MARIO_STAY_DURATION
        self.mushroom_duration = MUSHROOM_DURATION
        
        # Dragon mode
        self.dragon_head_color = (220, 50, 20)  # Red
        self.dragon_body_color = (180, 30, 10)
        self.dragon_fire_color = (250, 150, 10)
        self.dragon_mode_duration = DRAGON_MODE_DURATION
        
        # Font settings
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 60)
        self.menu_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 30)
        
        # Sound settings
        self.sound_enabled = True
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # UI settings
        self.menu_padding = 50
        self.menu_item_spacing = 20
        
        # Game difficulty settings - use config values
        self.difficulty = DIFFICULTY
        self.difficulty_settings = DIFFICULTY_SETTINGS
        
        # Speed settings - will be set by difficulty
        self.initial_snake_speed = 0  # Placeholder, will be set by difficulty
        self.max_snake_speed = 0      # Placeholder, will be set by difficulty
        self.speed_increase_rate = SPEED_INCREASE_RATE
        
        # Flag colors
        self.iran_flag_colors = IRAN_FLAG_COLORS
        
        # Apply difficulty settings - this MUST be done last
        self.apply_difficulty(self.difficulty)
    
    def apply_difficulty(self, difficulty):
        """Apply settings based on selected difficulty"""
        if difficulty in self.difficulty_settings:
            settings = self.difficulty_settings[difficulty]
            
            # Apply speed settings from difficulty
            self.initial_snake_speed = settings["initial_snake_speed"]
            self.max_snake_speed = settings["max_snake_speed"]
            
            # Apply appearance chances
            self.mario_appearance_chance = settings.get("mario_appearance_chance", 0.05)
            
            print(f"Difficulty set to {difficulty}:")
            print(f"  - Snake speed: {self.initial_snake_speed} (max: {self.max_snake_speed})")
            print(f"  - Mario chance: {self.mario_appearance_chance}")
    
    def change_difficulty(self, new_difficulty):
        """Change difficulty during gameplay"""
        if new_difficulty in self.difficulty_settings:
            self.difficulty = new_difficulty
            self.apply_difficulty(new_difficulty)
            return True
        return False 