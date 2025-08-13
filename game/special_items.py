"""
Special items - handles Mario character and power-up mushrooms
"""

import pygame
import random
import time
import math
from utils.config import EXPLOSION_SIZE_FACTOR, FLAG_DURATION

class Mario:
    def __init__(self, settings):
        self.settings = settings
        self.grid_size = settings.grid_size
        self.grid_width = settings.screen_width // settings.grid_size
        self.grid_height = settings.screen_height // settings.grid_size
        
        # Mario state
        self.active = False
        self.position = (0, 0)
        self.mushroom_position = None
        self.mushroom_active = False
        
        # Timing
        self.appear_time = 0
        self.duration = settings.mario_stay_duration
        
        # Colors
        self.mario_colors = {
            "hat": (255, 0, 0),         # Red hat
            "skin": (255, 200, 150),    # Skin tone
            "overalls": (0, 0, 255),    # Blue overalls
            "mushroom_cap": (255, 0, 0), # Red mushroom cap
            "mushroom_spots": (255, 255, 255), # White spots
            "mushroom_stem": (255, 255, 220)  # Off-white stem
        }
    
    def try_spawn(self):
        """Try to spawn Mario with the configured chance"""
        if not self.active and random.random() < self.settings.mario_appearance_chance:
            self.spawn()
            return True
        return False
    
    def spawn(self):
        """Spawn Mario at a random position"""
        # Find valid position that's not at the edge
        x = random.randint(2, self.grid_width - 3)
        y = random.randint(2, self.grid_height - 3)
        self.position = (x, y)
        self.active = True
        self.appear_time = time.time()
        self.mushroom_active = False
        self.mushroom_position = None
    
    def update(self, snake):
        """Update Mario state"""
        if not self.active:
            return False
        
        # Check if Mario's time is up
        current_time = time.time()
        if current_time - self.appear_time > self.duration:
            self.active = False
            return False
        
        # If Mario is active and mushroom is not spawned, place mushroom randomly
        if not self.mushroom_active and random.random() < 0.02:  # 2% chance per frame
            self.spawn_mushroom(snake)
        
        return True
    
    def spawn_mushroom(self, snake):
        """Spawn a mushroom near Mario"""
        if self.active and not self.mushroom_active:
            # Attempt to find a valid position for the mushroom
            for _ in range(10):  # Try 10 times
                dx = random.randint(-2, 2)
                dy = random.randint(-2, 2)
                
                # Don't place directly on Mario
                if dx == 0 and dy == 0:
                    continue
                    
                potential_pos = (
                    max(0, min(self.grid_width - 1, self.position[0] + dx)),
                    max(0, min(self.grid_height - 1, self.position[1] + dy))
                )
                
                # Check if position doesn't collide with snake
                if potential_pos not in snake.get_all_positions():
                    self.mushroom_position = potential_pos
                    self.mushroom_active = True
                    break
    
    def check_mushroom_collision(self, snake):
        """Check if snake collided with mushroom"""
        if self.mushroom_active and snake.get_head_position() == self.mushroom_position:
            self.mushroom_active = False
            self.active = False  # Mario disappears after mushroom is eaten
            return True
        return False


class PowerUpEffects:
    def __init__(self, settings, screen):
        self.settings = settings
        self.screen = screen
        
        # Power-up state
        self.dragon_mode_active = False
        self.dragon_mode_start_time = 0
        
        # Flag animation
        self.show_flag = False
        self.flag_start_time = 0
        self.flag_duration = FLAG_DURATION  # Use value from config
        
        # Nuclear explosion
        self.explosion_active = False
        self.explosion_start_time = 0
        self.explosion_duration = 3.5  # seconds, increased for longer effect
        self.explosion_radius = 0
        self.max_explosion_radius = min(settings.screen_width, settings.screen_height) * EXPLOSION_SIZE_FACTOR
        
        # Shockwave effects for nuclear explosion
        self.shockwaves = []
        self.explosion_particles = []
        
        # Lion animation
        self.lion_scale = 1.0
        self.lion_growing = True
    
    def activate_mushroom_power(self):
        """Activate all effects from eating a mushroom"""
        # Show flag
        self.show_flag = True
        self.flag_start_time = time.time()
        self.lion_scale = 1.0
        self.lion_growing = True
        
        # Start explosion
        self.explosion_active = True
        self.explosion_start_time = time.time()
        self.explosion_radius = 0
        self.shockwaves = []
        self.explosion_particles = []
        
        # Create initial shockwave
        self.add_shockwave()
        
        # Activate dragon mode
        self.dragon_mode_active = True
        self.dragon_mode_start_time = time.time()
    
    def add_shockwave(self):
        """Add a new shockwave effect"""
        self.shockwaves.append({
            'radius': 0,
            'max_radius': self.max_explosion_radius * 1.2,
            'speed': self.max_explosion_radius / (self.explosion_duration * 0.6),
            'thickness': random.randint(5, 12),
            'color': (255, 255, 255, 180),
            'birth_time': time.time()
        })
    
    def add_explosion_particles(self, count=50):
        """Add debris particles to the explosion"""
        center_x = self.settings.screen_width // 2
        center_y = self.settings.screen_height // 2
        
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 300)
            size = random.uniform(3, 10)
            lifetime = random.uniform(0.5, self.explosion_duration * 0.9)
            
            # Colors vary: yellow, orange, red, smoke
            color_choice = random.randint(0, 3)
            if color_choice == 0:
                color = (255, 255, 100, 230)  # Yellow
            elif color_choice == 1:
                color = (255, 150, 50, 230)   # Orange
            elif color_choice == 2:
                color = (220, 40, 40, 230)    # Red
            else:
                # Smoke (dark gray)
                gray = random.randint(50, 100)
                color = (gray, gray, gray, 200)
            
            self.explosion_particles.append({
                'x': center_x,
                'y': center_y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'lifetime': lifetime,
                'age': 0,
                'gravity': random.uniform(50, 150)
            })
    
    def update(self):
        """Update all active effects"""
        current_time = time.time()
        dt = 1/60  # Assume 60fps for particle physics
        
        # Update flag animation
        if self.show_flag:
            # Animate lion scale
            if self.lion_growing:
                self.lion_scale += 0.01
                if self.lion_scale >= 1.2:
                    self.lion_growing = False
            else:
                self.lion_scale -= 0.01
                if self.lion_scale <= 0.9:
                    self.lion_growing = True
            
            # Check if flag duration is over
            if current_time - self.flag_start_time > self.flag_duration:
                self.show_flag = False
        
        # Update explosion animation
        if self.explosion_active:
            progress = (current_time - self.explosion_start_time) / self.explosion_duration
            
            # Add particles over time
            if progress < 0.4 and random.random() < 0.3:
                self.add_explosion_particles(random.randint(5, 15))
            
            # Add shockwaves at intervals
            if len(self.shockwaves) < 3 and random.random() < 0.02:
                self.add_shockwave()
            
            # Update radius
            if progress >= 1.0:
                self.explosion_active = False
            else:
                # Non-linear growth for more realistic explosion
                if progress < 0.3:
                    # Fast initial expansion
                    factor = progress / 0.3
                    self.explosion_radius = self.max_explosion_radius * factor * 0.5
                else:
                    # Slower later expansion
                    factor = (progress - 0.3) / 0.7
                    self.explosion_radius = self.max_explosion_radius * (0.5 + factor * 0.5)
            
            # Update shockwaves
            for wave in list(self.shockwaves):
                wave['radius'] += wave['speed'] * dt
                
                # Remove old shockwaves
                if wave['radius'] > wave['max_radius']:
                    self.shockwaves.remove(wave)
            
            # Update particles
            for particle in list(self.explosion_particles):
                particle['age'] += dt
                if particle['age'] >= particle['lifetime']:
                    self.explosion_particles.remove(particle)
                    continue
                
                # Update position with gravity
                particle['dy'] += particle['gravity'] * dt
                particle['x'] += particle['dx'] * dt
                particle['y'] += particle['dy'] * dt
        
        # Update dragon mode
        if self.dragon_mode_active and current_time - self.dragon_mode_start_time > self.settings.dragon_mode_duration:
            self.dragon_mode_active = False
            
        return self.is_any_effect_active()
    
    def is_any_effect_active(self):
        """Check if any effect is currently active"""
        return self.show_flag or self.explosion_active or self.dragon_mode_active
    
    def render(self):
        """Render all active effects"""
        if self.explosion_active:
            self.render_explosion()
            
        if self.show_flag:
            self.render_iran_flag()
    
    def render_iran_flag(self):
        """Render the Iran flag with enhanced lion in center"""
        # Flag dimensions - slightly larger
        flag_width = self.settings.screen_width * 0.7
        flag_height = self.settings.screen_height * 0.5
        
        # Position in center of screen
        x = (self.settings.screen_width - flag_width) // 2
        y = (self.settings.screen_height - flag_height) // 2
        
        # Draw flag border
        border_width = 5
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (x - border_width, y - border_width, 
             flag_width + border_width*2, flag_height + border_width*2),
            border_width,
            3  # Rounded corners
        )
        
        # Draw flag sections (green, white, red)
        strip_height = flag_height / 3
        
        for i, color in enumerate(self.settings.iran_flag_colors):
            pygame.draw.rect(
                self.screen,
                color,
                (x, y + i * strip_height, flag_width, strip_height)
            )
        
        # Draw emblem (improved lion) in center, with scale animation
        lion_size = min(flag_width, flag_height) * 0.35 * self.lion_scale  # Much larger than before
        self.draw_enhanced_lion_emblem(
            x + flag_width // 2,
            y + flag_height // 2,
            lion_size
        )
        
        # Add text with glow effect
        self.render_glowing_text("MEGA UPGRADE!", 48, 
                                 self.settings.screen_width // 2, 
                                 y + flag_height + 50)
    
    def render_glowing_text(self, text, size, x, y):
        """Render text with a pulsing glow effect"""
        font = pygame.font.Font(None, size)
        
        # Pulsing glow based on time
        glow_intensity = 0.7 + 0.3 * math.sin(time.time() * 5)
        
        # Create multiple layers with increasing size for glow
        for i in range(5, 0, -1):
            alpha = int(150 * glow_intensity / i)
            glow_color = (255, 255, 100, alpha)
            glow_text = font.render(text, True, glow_color)
            glow_rect = glow_text.get_rect(center=(x, y))
            
            # Expand the rect slightly for each layer
            glow_rect.inflate_ip(i*4, i*4)
            
            # Draw the glow layer
            self.screen.blit(glow_text, glow_rect)
        
        # Draw the main text
        main_text = font.render(text, True, (255, 255, 255))
        main_rect = main_text.get_rect(center=(x, y))
        self.screen.blit(main_text, main_rect)
    
    def draw_enhanced_lion_emblem(self, center_x, center_y, size):
        """Draw an enhanced lion emblem"""
        # Base lion color (gold)
        lion_color = (220, 180, 0)
        lion_dark = (180, 140, 0)
        
        # Calculate positions
        body_width = size * 1.4
        body_height = size * 0.8
        head_size = size * 0.5
        
        # Body (oval shape)
        pygame.draw.ellipse(
            self.screen,
            lion_color,
            (center_x - body_width/2, center_y - body_height/2, body_width, body_height)
        )
        
        # Add texture/shading to body
        for i in range(3):
            offset = size * 0.1 * i
            pygame.draw.arc(
                self.screen,
                lion_dark,
                (center_x - body_width/2 + offset, center_y - body_height/2, body_width - offset*2, body_height),
                math.pi * 0.2,
                math.pi * 0.8,
                3
            )
        
        # Head position (at the front of body)
        head_x = center_x + body_width/2 - head_size/2
        head_y = center_y - head_size/2
        
        # Head (circle)
        pygame.draw.circle(
            self.screen,
            lion_color,
            (int(head_x), int(head_y)),
            int(head_size)
        )
        
        # Eyes (two small circles)
        eye_size = head_size * 0.15
        eye_color = (0, 0, 0)
        
        # Left eye
        pygame.draw.circle(
            self.screen,
            eye_color,
            (int(head_x - head_size * 0.2), int(head_y - head_size * 0.2)),
            int(eye_size)
        )
        
        # Right eye
        pygame.draw.circle(
            self.screen,
            eye_color,
            (int(head_x + head_size * 0.2), int(head_y - head_size * 0.2)),
            int(eye_size)
        )
        
        # Nose
        nose_points = [
            (head_x, head_y - head_size * 0.1),
            (head_x + head_size * 0.3, head_y + head_size * 0.1),
            (head_x - head_size * 0.3, head_y + head_size * 0.1)
        ]
        pygame.draw.polygon(
            self.screen,
            lion_dark,
            nose_points
        )
        
        # Mane (more detailed)
        mane_color = (240, 200, 0)  # Slightly lighter than body
        mane_segments = 18  # More segments for detail
        mane_length_var = 0.4  # Variability in length
        
        for i in range(mane_segments):
            angle = i * 2 * math.pi / mane_segments
            # Add some randomness to mane length
            length_factor = 1.0 + (math.sin(angle * 3) * mane_length_var)
            
            start_x = head_x
            start_y = head_y
            end_x = head_x + math.cos(angle) * head_size * 1.5 * length_factor
            end_y = head_y + math.sin(angle) * head_size * 1.5 * length_factor
            
            # Draw mane segment
            pygame.draw.line(
                self.screen,
                mane_color,
                (start_x, start_y),
                (end_x, end_y),
                int(head_size * 0.15)
            )
        
        # Legs
        leg_width = size * 0.15
        leg_height = size * 0.5
        leg_color = lion_color
        
        # Front legs
        pygame.draw.rect(
            self.screen,
            leg_color,
            (center_x + body_width/3 - leg_width/2, center_y + body_height/2 - leg_width/2, 
             leg_width, leg_height),
            0,
            5  # Rounded corners
        )
        
        pygame.draw.rect(
            self.screen,
            leg_color,
            (center_x + body_width/4 - leg_width/2, center_y + body_height/2 - leg_width/2, 
             leg_width, leg_height),
            0,
            5
        )
        
        # Back legs
        pygame.draw.rect(
            self.screen,
            leg_color,
            (center_x - body_width/3 - leg_width/2, center_y + body_height/2 - leg_width/2, 
             leg_width, leg_height),
            0,
            5
        )
        
        pygame.draw.rect(
            self.screen,
            leg_color,
            (center_x - body_width/4 - leg_width/2, center_y + body_height/2 - leg_width/2, 
             leg_width, leg_height),
            0,
            5
        )
        
        # Tail
        tail_start_x = center_x - body_width/2
        tail_start_y = center_y
        
        # Curved tail
        curve_points = []
        for i in range(10):
            t = i / 9.0
            # Parametric equation for a curve
            curve_x = tail_start_x - (body_width * 0.4 * t)
            curve_y = tail_start_y - (body_height * 0.5 * math.sin(t * math.pi))
            curve_points.append((curve_x, curve_y))
        
        # Draw tail curve
        if len(curve_points) >= 2:
            pygame.draw.lines(
                self.screen,
                lion_color,
                False,
                curve_points,
                int(size * 0.08)
            )
            
            # Tail tuft
            tuft_size = size * 0.15
            pygame.draw.circle(
                self.screen,
                lion_dark,
                (int(curve_points[-1][0]), int(curve_points[-1][1])),
                int(tuft_size)
            )
    
    def render_explosion(self):
        """Render enhanced nuclear explosion effect with shockwaves and particles"""
        # Create gradient explosion
        current_time = time.time()
        progress = (current_time - self.explosion_start_time) / self.explosion_duration
        
        # Draw particles first (so they appear behind the main explosion)
        self.render_explosion_particles()
        
        # Draw shockwaves
        self.render_shockwaves()
        
        # Calculate colors based on progress for main explosion
        if progress < 0.2:
            # Initial flash - bright white
            color = (255, 255, 255)
            alpha = 230
        elif progress < 0.4:
            # Bright yellow/white
            color = (255, 255, 200)
            alpha = 210
        elif progress < 0.6:
            # Orange
            color = (255, 150, 50)
            alpha = 190
        else:
            # Reddish
            color = (200, 60, 60)
            alpha = int(180 * (1 - (progress - 0.6) / 0.4))
        
        # Create a surface for the main explosion with transparency
        size = int(self.explosion_radius * 2.2)
        if size <= 0:
            return
            
        explosion_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw gradient circles for mushroom cloud effect
        cloud_layers = 5
        for i in range(cloud_layers):
            factor = 1.0 - (i * (0.8 / cloud_layers))
            radius = int(self.explosion_radius * factor)
            
            # Adjust alpha for fade-out near the end
            layer_alpha = int(alpha * (1 - i / cloud_layers))
            
            explosion_color = list(color)
            explosion_color.append(layer_alpha)
            
            # Draw main explosion circle
            pygame.draw.circle(
                explosion_surf,
                explosion_color,
                (size//2, size//2),
                radius
            )
            
            # Add some noise/texture to the explosion
            if radius > 20:
                for _ in range(10):
                    noise_radius = random.uniform(0.8, 1.0) * radius
                    angle = random.uniform(0, math.pi * 2)
                    offset_x = math.cos(angle) * noise_radius * 0.2
                    offset_y = math.sin(angle) * noise_radius * 0.2
                    
                    noise_color = list(color)
                    # Ensure minimum range of 1 for randint to avoid crash
                    if layer_alpha <= 30:
                        noise_alpha = 30  # Just use minimum value
                    else:
                        noise_alpha = random.randint(30, layer_alpha)
                    noise_color.append(noise_alpha)
                    
                    noise_size = random.uniform(0.1, 0.3) * radius
                    
                    # Draw noise circle
                    pygame.draw.circle(
                        explosion_surf,
                        noise_color,
                        (int(size//2 + offset_x), int(size//2 + offset_y)),
                        int(noise_size)
                    )
        
        # Draw mushroom cloud stem if the explosion is developed enough
        if progress > 0.3 and progress < 0.85:
            stem_width = self.explosion_radius * 0.5
            stem_height = self.explosion_radius * 1.5
            
            # Stem gets taller as explosion progresses
            if progress < 0.5:
                stem_height *= (progress - 0.3) / 0.2
            
            stem_x = size//2 - stem_width//2
            stem_y = size//2
            
            # Draw stem
            stem_color = list(color)
            stem_color.append(int(alpha * 0.7))
            
            pygame.draw.rect(
                explosion_surf,
                stem_color,
                (stem_x, stem_y, stem_width, stem_height),
                0,
                int(stem_width * 0.2)  # Slightly rounded corners
            )
            
            # Draw some texture/smoke on the stem
            for _ in range(5):
                smoke_x = stem_x + random.uniform(0, stem_width)
                smoke_y = stem_y + random.uniform(0, stem_height)
                smoke_size = random.uniform(stem_width * 0.1, stem_width * 0.3)
                
                smoke_color = list(color)
                smoke_color.append(random.randint(30, 100))
                
                pygame.draw.circle(
                    explosion_surf,
                    smoke_color,
                    (int(smoke_x), int(smoke_y)),
                    int(smoke_size)
                )
        
        # Position the explosion in the center of the screen
        explosion_rect = explosion_surf.get_rect(
            center=(self.settings.screen_width//2, self.settings.screen_height//2)
        )
        
        # Apply the explosion to the screen
        self.screen.blit(explosion_surf, explosion_rect)
    
    def render_shockwaves(self):
        """Render shockwave rings"""
        center_x = self.settings.screen_width // 2
        center_y = self.settings.screen_height // 2
        
        for wave in self.shockwaves:
            # Calculate alpha based on progress
            progress = wave['radius'] / wave['max_radius']
            alpha = int(255 * (1 - progress))
            
            color = list(wave['color'])
            color[3] = alpha
            
            # Draw shockwave ring
            pygame.draw.circle(
                self.screen,
                color,
                (center_x, center_y),
                int(wave['radius']),
                wave['thickness']
            )
    
    def render_explosion_particles(self):
        """Render explosion particles"""
        for particle in self.explosion_particles:
            # Calculate alpha based on age
            progress = particle['age'] / particle['lifetime']
            alpha = int(particle['color'][3] * (1 - progress))
            
            # Ensure alpha is valid (0-255)
            alpha = max(0, min(255, alpha))
            
            color = list(particle['color'])
            color[3] = alpha
            
            # Make sure particle size is at least 1 pixel
            size = max(1, int(particle['size'] * (1 - progress * 0.7)))
            
            # Draw particle
            pygame.draw.circle(
                self.screen,
                color,
                (int(particle['x']), int(particle['y'])),
                size  # Particles shrink as they age
            ) 