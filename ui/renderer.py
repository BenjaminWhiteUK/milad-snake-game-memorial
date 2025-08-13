"""
Renderer - handles all game visuals and graphical elements
"""

import pygame
import math
import time

class Renderer:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.grid_size = settings.grid_size
        
        # Load any necessary assets
        self.load_assets()
        
        # For smooth animations
        self.frame_counter = 0
        self.last_frame_time = time.time()
        
    def load_assets(self):
        """Load graphical assets and create surfaces"""
        # Pre-render common elements
        self.grid_surface = self.create_grid_surface()
        
        # Create gradient overlays for effects
        self.vignette = self.create_vignette()
    
    def create_grid_surface(self):
        """Pre-render the grid to improve performance"""
        grid_surface = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        
        # Draw vertical lines
        for x in range(0, self.settings.screen_width, self.grid_size):
            pygame.draw.line(grid_surface, self.settings.grid_color, (x, 0), (x, self.settings.screen_height))
            
        # Draw horizontal lines
        for y in range(0, self.settings.screen_height, self.grid_size):
            pygame.draw.line(grid_surface, self.settings.grid_color, (0, y), (self.settings.screen_width, y))
            
        return grid_surface
    
    def create_vignette(self):
        """Create a vignette effect overlay"""
        vignette = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        
        # Create radial gradient
        center_x, center_y = self.settings.screen_width // 2, self.settings.screen_height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        for x in range(self.settings.screen_width):
            for y in range(self.settings.screen_height):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                # Calculate alpha based on distance from center
                alpha = int(min(255, (dist / max_dist) * 255) * 0.7)
                vignette.set_at((x, y), (0, 0, 0, alpha))
                
        return vignette
    
    def render_grid(self):
        """Render the grid on screen"""
        self.screen.blit(self.grid_surface, (0, 0))
    
    def render_snake(self, snake):
        """Render the snake with advanced visual effects"""
        segments = snake.get_all_positions()
        
        # Update delta time for fire particles
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Update fire particles if in dragon mode
        if snake.dragon_mode:
            snake.update_fire_particles(dt)
        
        # Draw each segment with a size based on its position
        for i, (x, y) in enumerate(segments):
            # Calculate size
            if i == 0:  # Head
                color = snake.colors["head"]
                segment_size = self.grid_size - 1  # Slightly smaller than grid for visual effect
                
                # Make head larger and more pointed in dragon mode
                if snake.dragon_mode:
                    segment_size = self.grid_size * 1.1
            else:  # Body
                color = snake.colors["body"]
                # Make tail segments slightly smaller
                segment_size = self.grid_size - 3 - (i / len(segments) * 2)
                segment_size = max(segment_size, self.grid_size * 0.5)  # Don't let it get too small
            
            # Calculate position with offset to center in grid
            pos_x = x * self.grid_size + (self.grid_size - segment_size) / 2
            pos_y = y * self.grid_size + (self.grid_size - segment_size) / 2
            
            # Draw segment with rounded corners or spikes for dragon
            if snake.dragon_mode and i == 0:
                # Draw dragon head with spikes
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    (pos_x, pos_y, segment_size, segment_size),
                    0, 
                    1  # Sharp corners
                )
                
                # Add spikes to dragon head
                if len(segments) > 1:
                    head_x, head_y = segments[0]
                    neck_x, neck_y = segments[1]
                    
                    # Direction from neck to head
                    dx = head_x - neck_x
                    dy = head_y - neck_y
                    
                    # Spike direction (opposite of movement)
                    spike_x = -dx * self.grid_size * 0.4
                    spike_y = -dy * self.grid_size * 0.4
                    
                    # Spike base points (at the back of the head)
                    base_x = pos_x + segment_size/2 - spike_x/2
                    base_y = pos_y + segment_size/2 - spike_y/2
                    
                    # Draw spikes on the sides
                    for i in range(2):
                        # Alternate sides
                        side = 1 if i == 0 else -1
                        
                        # Perpendicular direction for side spikes
                        perp_x, perp_y = -spike_y * side * 0.7, spike_x * side * 0.7
                        
                        # Draw spike
                        pygame.draw.polygon(
                            self.screen,
                            snake.colors["head"],
                            [
                                (base_x, base_y),  # Base
                                (base_x + perp_x, base_y + perp_y),  # Tip
                                (base_x + spike_x * 0.3, base_y + spike_y * 0.3)  # Back
                            ]
                        )
                
            else:
                # Regular segments
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    (pos_x, pos_y, segment_size, segment_size),
                    0, 
                    3  # Rounded corners radius
                )
            
            # Add highlight or eyes to head
            if i == 0:
                if snake.dragon_mode:
                    # Draw dragon eyes (red)
                    eye_size = segment_size * 0.15
                    eye_offset_x = segment_size * 0.3
                    eye_offset_y = segment_size * 0.25
                    
                    # Left eye
                    pygame.draw.circle(
                        self.screen,
                        (255, 0, 0),  # Red eyes
                        (int(pos_x + eye_offset_x), int(pos_y + eye_offset_y)),
                        int(eye_size)
                    )
                    
                    # Right eye
                    pygame.draw.circle(
                        self.screen,
                        (255, 0, 0),
                        (int(pos_x + eye_offset_x), int(pos_y + segment_size - eye_offset_y)),
                        int(eye_size)
                    )
                else:
                    # Regular snake highlight
                    highlight_size = segment_size * 0.5
                    highlight_offset = segment_size * 0.1
                    pygame.draw.circle(
                        self.screen,
                        (255, 255, 255, 180),  # White with transparency
                        (pos_x + highlight_offset, pos_y + highlight_offset),
                        highlight_size / 10
                    )
        
        # Render fire particles if in dragon mode
        if snake.dragon_mode:
            snake.render_fire_particles(self.screen)
                
    def render_food(self, food):
        """Render food with animation effects"""
        x, y = food.position
        
        # Update animation
        food.update_animation()
        
        # Calculate pulsing size
        base_size = self.grid_size * 0.7
        food_size = base_size * food.pulse_scale
        
        # Center food in the grid cell
        pos_x = x * self.grid_size + (self.grid_size - food_size) / 2
        pos_y = y * self.grid_size + (self.grid_size - food_size) / 2
        
        # Draw food with glow effect
        if food.food_type == "special":
            # Add glow for special food
            glow_radius = food_size * 1.5
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            
            # Create radial gradient for glow
            for gx in range(int(glow_radius*2)):
                for gy in range(int(glow_radius*2)):
                    distance = math.sqrt((gx - glow_radius)**2 + (gy - glow_radius)**2)
                    if distance < glow_radius:
                        # Calculate alpha based on distance from center
                        alpha = int(255 * (1 - distance / glow_radius) * 0.5)
                        glow_color = list(food.color)
                        glow_color.append(alpha)
                        glow_surface.set_at((gx, gy), glow_color)
            
            # Calculate center position for glow
            glow_x = pos_x + food_size/2 - glow_radius
            glow_y = pos_y + food_size/2 - glow_radius
            
            # Apply glow
            self.screen.blit(glow_surface, (glow_x, glow_y))
        
        # Draw food
        pygame.draw.circle(
            self.screen, 
            food.color, 
            (pos_x + food_size/2, pos_y + food_size/2), 
            food_size/2
        )
        
        # Add highlight
        highlight_size = food_size * 0.5
        highlight_offset = food_size * 0.2
        pygame.draw.circle(
            self.screen,
            (255, 255, 255, 150),  # White with transparency
            (pos_x + highlight_offset, pos_y + highlight_offset),
            highlight_size / 6
        )
    
    def render_mario(self, mario):
        """Render Mario and mushroom if active"""
        if not mario.active:
            return
        
        # Render Mario
        x, y = mario.position
        
        # Size and position calculations
        character_size = self.grid_size * 0.9
        pos_x = x * self.grid_size + (self.grid_size - character_size) / 2
        pos_y = y * self.grid_size + (self.grid_size - character_size) / 2
        
        # Draw Mario (simplified)
        # Head/face
        pygame.draw.circle(
            self.screen,
            mario.mario_colors["skin"],
            (pos_x + character_size/2, pos_y + character_size/3),
            character_size/3
        )
        
        # Hat
        pygame.draw.rect(
            self.screen,
            mario.mario_colors["hat"],
            (pos_x, pos_y, character_size, character_size/4),
            0,
            3
        )
        
        # Body
        pygame.draw.rect(
            self.screen,
            mario.mario_colors["overalls"],
            (pos_x + character_size/4, pos_y + character_size/3,
             character_size/2, character_size/2),
            0,
            2
        )
        
        # Render mushroom if active
        if mario.mushroom_active:
            mushroom_x, mushroom_y = mario.mushroom_position
            mushroom_size = self.grid_size * 0.8
            
            # Position calculations
            m_pos_x = mushroom_x * self.grid_size + (self.grid_size - mushroom_size) / 2
            m_pos_y = mushroom_y * self.grid_size + (self.grid_size - mushroom_size) / 2
            
            # Draw mushroom stem
            stem_width = mushroom_size * 0.4
            stem_height = mushroom_size * 0.4
            pygame.draw.rect(
                self.screen,
                mario.mario_colors["mushroom_stem"],
                (m_pos_x + mushroom_size/2 - stem_width/2,
                 m_pos_y + mushroom_size - stem_height,
                 stem_width, stem_height),
                0,
                2
            )
            
            # Draw mushroom cap
            cap_size = mushroom_size * 0.8
            pygame.draw.circle(
                self.screen,
                mario.mario_colors["mushroom_cap"],
                (m_pos_x + mushroom_size/2, m_pos_y + mushroom_size/2 - cap_size/4),
                cap_size/2
            )
            
            # Draw spots on mushroom
            for i in range(3):
                spot_size = cap_size * 0.2
                angle = i * 120 + (self.frame_counter % 360)
                rad_angle = math.radians(angle)
                spot_x = m_pos_x + mushroom_size/2 + math.cos(rad_angle) * cap_size/3
                spot_y = m_pos_y + mushroom_size/2 - cap_size/4 + math.sin(rad_angle) * cap_size/3
                
                pygame.draw.circle(
                    self.screen,
                    mario.mario_colors["mushroom_spots"],
                    (spot_x, spot_y),
                    spot_size
                )
    
    def render_score(self, score):
        """Render the current score"""
        score_text = self.settings.score_font.render(f"Score: {score}", True, self.settings.ui_text_color)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, 10)
        
        # Add a subtle background for the score
        bg_rect = score_rect.copy()
        bg_rect.inflate_ip(20, 10)  # Make background slightly larger
        pygame.draw.rect(self.screen, (0, 0, 0, 150), bg_rect, 0, 5)
        
        # Render the score
        self.screen.blit(score_text, score_rect)
    
    def render_pause_overlay(self):
        """Render the pause screen overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # "PAUSED" text
        pause_text = self.settings.title_font.render("PAUSED", True, self.settings.ui_text_color)
        pause_rect = pause_text.get_rect(center=(self.settings.screen_width//2, self.settings.screen_height//2 - 40))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        instr1 = self.settings.menu_font.render("Press ESC to resume", True, self.settings.ui_text_color)
        instr2 = self.settings.menu_font.render("Press Q to quit to menu", True, self.settings.ui_text_color)
        
        instr1_rect = instr1.get_rect(center=(self.settings.screen_width//2, self.settings.screen_height//2 + 20))
        instr2_rect = instr2.get_rect(center=(self.settings.screen_width//2, self.settings.screen_height//2 + 60))
        
        self.screen.blit(instr1, instr1_rect)
        self.screen.blit(instr2, instr2_rect)
    
    def render_game_over(self, score):
        """Render the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Apply vignette effect
        self.screen.blit(self.vignette, (0, 0))
        
        # "GAME OVER" text
        gameover_text = self.settings.title_font.render("GAME OVER", True, self.settings.ui_text_color)
        gameover_rect = gameover_text.get_rect(center=(self.settings.screen_width//2, self.settings.screen_height//2 - 80))
        self.screen.blit(gameover_text, gameover_rect)
        
        # Score
        score_text = self.settings.menu_font.render(f"Final Score: {score}", True, self.settings.ui_text_color)
        score_rect = score_text.get_rect(center=(self.settings.screen_width//2, self.settings.screen_height//2 - 20))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        instr1 = self.settings.menu_font.render("Press ENTER to play again", True, self.settings.ui_text_color)
        instr2 = self.settings.menu_font.render("Press ESC to return to menu", True, self.settings.ui_text_color)
        
        instr1_rect = instr1.get_rect(center=(self.settings.screen_width//2, self.settings.screen_height//2 + 40))
        instr2_rect = instr2.get_rect(center=(self.settings.screen_width//2, self.settings.screen_height//2 + 80))
        
        self.screen.blit(instr1, instr1_rect)
        self.screen.blit(instr2, instr2_rect) 