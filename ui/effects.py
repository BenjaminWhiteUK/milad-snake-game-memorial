"""
Effects system - manages visual and audio effects
"""

import pygame
import random
import math

class Effects:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        
        # Initialize sound system
        pygame.mixer.init()
        
        # Load sound effects
        self.sound_effects = self.load_sound_effects()
        
        # Visual effects animations
        self.active_effects = []
    
    def load_sound_effects(self):
        """Load sound effects or create synthetic ones"""
        sounds = {}
        
        # We'll use synthesized sounds to avoid requiring sound files
        sounds["eat"] = self.create_eat_sound()
        sounds["game_over"] = self.create_game_over_sound()
        sounds["menu_select"] = self.create_menu_select_sound()
        sounds["menu_change"] = self.create_menu_change_sound()
        
        return sounds
    
    def create_eat_sound(self):
        """Create a synthetic 'eat' sound effect"""
        # Create a short beep sound using pygame.mixer
        sound = pygame.mixer.Sound(self.generate_eat_tone())
        sound.set_volume(0.4 * self.settings.sfx_volume)
        return sound
    
    def create_game_over_sound(self):
        """Create a synthetic 'game over' sound effect"""
        sound = pygame.mixer.Sound(self.generate_game_over_tone())
        sound.set_volume(0.6 * self.settings.sfx_volume)
        return sound
    
    def create_menu_select_sound(self):
        """Create a synthetic menu selection sound effect"""
        sound = pygame.mixer.Sound(self.generate_menu_select_tone())
        sound.set_volume(0.4 * self.settings.sfx_volume)
        return sound
    
    def create_menu_change_sound(self):
        """Create a synthetic menu change sound effect"""
        sound = pygame.mixer.Sound(self.generate_menu_change_tone())
        sound.set_volume(0.3 * self.settings.sfx_volume)
        return sound
    
    def generate_eat_tone(self):
        """Generate a simple tone for the eat sound"""
        # Parameters for sound generation
        sample_rate = 44100
        duration = 0.1  # seconds
        frequency = 800
        
        # Generate the tone
        num_samples = int(sample_rate * duration)
        buf = bytearray(num_samples)
        
        # Simple sine wave with a quick decay
        for i in range(num_samples):
            t = float(i) / sample_rate
            decay = 1.0 - (float(i) / num_samples)**0.5
            value = int(127 + 127 * decay * math.sin(2 * math.pi * frequency * t))
            buf[i] = value
            
        return bytes(buf)
    
    def generate_game_over_tone(self):
        """Generate a 'game over' sound effect"""
        # Parameters for sound generation
        sample_rate = 44100
        duration = 0.6  # seconds
        
        # Start with high pitched tone descending to low tone
        num_samples = int(sample_rate * duration)
        buf = bytearray(num_samples)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            progress = float(i) / num_samples
            
            # Frequency decreases over time
            frequency = 700 - 600 * progress
            
            value = int(127 + 127 * math.sin(2 * math.pi * frequency * t))
            buf[i] = value
            
        return bytes(buf)
    
    def generate_menu_select_tone(self):
        """Generate a 'menu select' sound effect"""
        # Parameters for sound generation
        sample_rate = 44100
        duration = 0.15  # seconds
        
        # Quick ascending tones
        num_samples = int(sample_rate * duration)
        buf = bytearray(num_samples)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            progress = float(i) / num_samples
            
            # Frequency increases over time
            frequency = 300 + 400 * progress
            
            value = int(127 + 127 * math.sin(2 * math.pi * frequency * t))
            buf[i] = value
            
        return bytes(buf)
    
    def generate_menu_change_tone(self):
        """Generate a 'menu change' sound effect"""
        # Parameters for sound generation
        sample_rate = 44100
        duration = 0.05  # seconds
        
        # Quick click sound
        num_samples = int(sample_rate * duration)
        buf = bytearray(num_samples)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            progress = float(i) / num_samples
            
            # Simple click tone with decay
            frequency = 500
            decay = 1.0 - progress
            
            value = int(127 + 127 * decay * math.sin(2 * math.pi * frequency * t))
            buf[i] = value
            
        return bytes(buf)
    
    def play_effect(self, effect_name, **kwargs):
        """Play a sound effect and trigger a visual effect"""
        # Play sound effect if enabled
        if self.settings.sound_enabled and effect_name in self.sound_effects:
            self.sound_effects[effect_name].play()
        
        # Add visual effect
        if effect_name == "eat":
            food_pos = kwargs.get("position")
            if food_pos:
                self.active_effects.append({
                    "type": "eat_flash",
                    "position": food_pos,
                    "duration": 10,
                    "current_frame": 0,
                    "color": kwargs.get("color", (255, 255, 255))
                })
        elif effect_name == "game_over":
            self.active_effects.append({
                "type": "screen_shake",
                "duration": 30,
                "current_frame": 0,
                "intensity": 5
            })
    
    def update(self):
        """Update all active effects"""
        for effect in self.active_effects[:]:
            effect["current_frame"] += 1
            
            # Remove expired effects
            if effect["current_frame"] >= effect["duration"]:
                self.active_effects.remove(effect)
    
    def render(self):
        """Render all active visual effects"""
        for effect in self.active_effects:
            if effect["type"] == "eat_flash":
                self.render_eat_flash(effect)
            elif effect["type"] == "screen_shake":
                self.render_screen_shake(effect)
    
    def render_eat_flash(self, effect):
        """Render an eating flash effect"""
        x, y = effect["position"]
        grid_size = self.settings.grid_size
        
        # Calculate size and opacity based on current frame
        progress = effect["current_frame"] / effect["duration"]
        size = grid_size * (1 + progress * 2)
        alpha = int(255 * (1 - progress))
        
        # Create a surface for the flash
        flash_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw the flash with fading opacity
        color = list(effect["color"])
        color.append(alpha)
        pygame.draw.circle(flash_surf, color, (size, size), size)
        
        # Blit to screen
        screen_x = x * grid_size + grid_size/2 - size
        screen_y = y * grid_size + grid_size/2 - size
        self.screen.blit(flash_surf, (screen_x, screen_y))
    
    def render_screen_shake(self, effect):
        """Apply screen shake effect"""
        # Calculate intensity based on progress
        progress = effect["current_frame"] / effect["duration"]
        intensity = effect["intensity"] * (1 - progress)
        
        # Apply random offset to the screen
        offset_x = random.uniform(-intensity, intensity)
        offset_y = random.uniform(-intensity, intensity)
        
        # We'd actually need to apply this to the game rendering process
        # by shifting all rendered elements, but for a simple implementation
        # we'll just note that this effect was designed 