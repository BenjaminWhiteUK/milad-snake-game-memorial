"""
Food class - manages food generation and properties
"""

import random
import pygame

class Food:
    def __init__(self, settings):
        self.settings = settings
        self.grid_size = settings.grid_size
        self.grid_width = settings.screen_width // settings.grid_size
        self.grid_height = settings.screen_height // settings.grid_size
        
        # Initialize with a random position
        self.position = (0, 0)  # Will be set in respawn
        
        # Food colors and animation properties
        self.color = settings.food_color
        self.pulse_max = 1.3
        self.pulse_min = 0.7
        self.pulse_speed = 0.04
        self.pulse_scale = 1.0
        self.pulse_growing = True
        
        # Food types (for potential special food items)
        self.food_types = {
            "normal": {
                "color": settings.food_color,
                "points": 10,
                "effect": None
            },
            "special": {
                "color": settings.special_food_color,
                "points": 30,
                "effect": "speed_boost"
            }
        }
        
        self.food_type = "normal"
        self.special_chance = 0.1  # 10% chance for special food
        
        # Set initial position
        self.respawn(None)
    
    def respawn(self, snake):
        """Generate a new food position that doesn't collide with the snake"""
        valid_position = False
        
        # Choose food type
        if random.random() < self.special_chance:
            self.food_type = "special"
        else:
            self.food_type = "normal"
        
        # Update color based on type
        self.color = self.food_types[self.food_type]["color"]
        
        while not valid_position:
            # Generate random position
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            potential_position = (x, y)
            
            # Check if position doesn't collide with snake
            if snake is None or potential_position not in snake.get_all_positions():
                self.position = potential_position
                valid_position = True
    
    def update_animation(self):
        """Update food animation effects (pulsing, etc.)"""
        # Pulsing animation effect
        if self.pulse_growing:
            self.pulse_scale += self.pulse_speed
            if self.pulse_scale >= self.pulse_max:
                self.pulse_growing = False
        else:
            self.pulse_scale -= self.pulse_speed
            if self.pulse_scale <= self.pulse_min:
                self.pulse_growing = True
    
    def get_points(self):
        """Get points value for the current food type"""
        return self.food_types[self.food_type]["points"]
    
    def get_effect(self):
        """Get special effect for the current food type"""
        return self.food_types[self.food_type]["effect"] 