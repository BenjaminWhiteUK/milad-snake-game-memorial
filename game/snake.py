"""
Snake class - manages the snake's body, movement, and collision detection
"""

import pygame
import random
import math
from collections import deque

class Snake:
    def __init__(self, settings):
        self.settings = settings
        self.grid_size = settings.grid_size
        
        # Initialize snake in the middle of the screen
        grid_width = settings.screen_width // settings.grid_size
        grid_height = settings.screen_height // settings.grid_size
        
        # Snake body represented as a deque of positions (x, y)
        self.body = deque()
        
        # Create initial snake (3 segments)
        mid_x, mid_y = grid_width // 2, grid_height // 2
        self.body.append((mid_x, mid_y))        # Head
        self.body.append((mid_x - 1, mid_y))    # Body
        self.body.append((mid_x - 2, mid_y))    # Tail
        
        # Movement properties
        self.direction = "RIGHT"
        self.speed = settings.initial_snake_speed  # Initialize with settings speed
        print(f"Snake initialized with speed: {self.speed} (from settings: {settings.initial_snake_speed})")
        self.growth_pending = 0
        
        # Key tracking for single press movement
        self.pending_direction = None
        self.last_move_time = 0
        
        # Visuals
        self.colors = {
            "head": settings.snake_head_color,
            "body": settings.snake_body_color
        }
        
        # Dragon mode
        self.dragon_mode = False
        self.fire_particles = []
        
        # Movement cooldown to prevent multiple direction changes per frame
        self.move_cooldown = 0
        
    def change_direction(self, new_direction):
        """Queue direction change for next movement"""
        # Prevent changing to opposite direction
        opposites = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT"
        }
        
        # Only queue direction if not moving to opposite direction
        if new_direction != opposites.get(self.direction):
            # Store as pending direction to be applied on next move
            self.pending_direction = new_direction
    
    def apply_pending_direction(self):
        """Apply any pending direction change"""
        if self.pending_direction:
            self.direction = self.pending_direction
            self.pending_direction = None
    
    def move(self):
        """Move the snake based on current direction"""
        # Apply any pending direction change
        self.apply_pending_direction()
        
        # Calculate move time based on current speed
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        move_interval = 1.0 / self.speed
        
        # Check if it's time to move
        if current_time - self.last_move_time < move_interval:
            return False  # Not time to move yet
        
        # Update last move time
        self.last_move_time = current_time
        
        # Get current head position
        head_x, head_y = self.body[0]
        
        # Calculate new head position based on direction
        if self.direction == "UP":
            new_head = (head_x, head_y - 1)
        elif self.direction == "DOWN":
            new_head = (head_x, head_y + 1)
        elif self.direction == "LEFT":
            new_head = (head_x - 1, head_y)
        elif self.direction == "RIGHT":
            new_head = (head_x + 1, head_y)
            
        # Wrap around screen edges
        grid_width = self.settings.screen_width // self.settings.grid_size
        grid_height = self.settings.screen_height // self.settings.grid_size
        
        wrapped_x = new_head[0] % grid_width
        wrapped_y = new_head[1] % grid_height
        
        # If negative position, wrap to the other side
        if wrapped_x < 0:
            wrapped_x = grid_width - 1
        if wrapped_y < 0:
            wrapped_y = grid_height - 1
            
        new_head = (wrapped_x, wrapped_y)
            
        # Add new head
        self.body.appendleft(new_head)
        
        # Create fire particles if in dragon mode
        if self.dragon_mode:
            self.add_fire_particles()
        
        # Remove tail if not growing
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()
            
        return True  # Successfully moved
    
    def add_fire_particles(self):
        """Add fire particles behind the dragon's head"""
        if len(self.body) < 2:
            return
            
        head_x, head_y = self.body[0]
        neck_x, neck_y = self.body[1]
        
        # Direction from neck to head
        dx = head_x - neck_x
        dy = head_y - neck_y
        
        # Perpendicular directions
        perp_dx, perp_dy = -dy, dx
        
        # Create particles on both sides
        for i in range(2):
            side = 1 if i == 0 else -1
            offset_x = perp_dx * side * 0.3
            offset_y = perp_dy * side * 0.3
            
            # Add randomness to position
            jitter_x = random.uniform(-0.2, 0.2)
            jitter_y = random.uniform(-0.2, 0.2)
            
            # Position particle slightly behind head
            particle_x = (neck_x + (head_x - neck_x) * 0.7 + offset_x + jitter_x) * self.grid_size
            particle_y = (neck_y + (head_y - neck_y) * 0.7 + offset_y + jitter_y) * self.grid_size
            
            # Create particle
            lifetime = random.uniform(0.5, 1.0)
            size = random.uniform(3, 6)
            self.fire_particles.append({
                'x': particle_x,
                'y': particle_y,
                'dx': -dx * random.uniform(0.5, 1.5) + random.uniform(-0.5, 0.5),
                'dy': -dy * random.uniform(0.5, 1.5) + random.uniform(-0.5, 0.5),
                'size': size,
                'max_size': size,
                'lifetime': lifetime,
                'age': 0
            })
    
    def update_fire_particles(self, dt):
        """Update fire particles"""
        # Update existing particles
        for particle in list(self.fire_particles):
            particle['age'] += dt
            if particle['age'] >= particle['lifetime']:
                self.fire_particles.remove(particle)
                continue
                
            # Update position
            particle['x'] += particle['dx'] * dt * 60
            particle['y'] += particle['dy'] * dt * 60
            
            # Shrink particle as it ages
            age_factor = 1.0 - (particle['age'] / particle['lifetime'])
            particle['size'] = particle['max_size'] * age_factor
    
    def grow(self):
        """Increase the snake's length"""
        self.growth_pending += 1
    
    def increase_speed(self):
        """Increase the snake's speed by a tiny amount"""
        old_speed = self.speed
        self.speed = min(self.speed * (1.0 + self.settings.speed_increase_rate), self.settings.max_snake_speed)
        
        # Print debug info if speed changed
        if abs(old_speed - self.speed) > 0.01:
            print(f"Speed increased: {old_speed:.2f} -> {self.speed:.2f} (max: {self.settings.max_snake_speed})")
    
    def reset_speed(self):
        """Reset the snake's speed to the initial value from settings"""
        self.speed = self.settings.initial_snake_speed
        print(f"Speed reset to {self.speed}")
    
    def set_dragon_mode(self, active):
        """Activate or deactivate dragon mode"""
        self.dragon_mode = active
        if active:
            self.colors = {
                "head": self.settings.dragon_head_color,
                "body": self.settings.dragon_body_color
            }
        else:
            self.colors = {
                "head": self.settings.snake_head_color,
                "body": self.settings.snake_body_color
            }
            # Clear fire particles when dragon mode ends
            self.fire_particles = []
    
    def check_collision_with_self(self):
        """Check if the snake's head collides with its body"""
        head = self.body[0]
        # Check if head position exists in the rest of the body
        return head in list(self.body)[1:]
    
    def check_collision_with_walls(self, settings):
        """Check if the snake's head collides with the walls"""
        # We no longer need to check wall collisions since we're wrapping around
        # Just return False to indicate no collision
        return False
    
    def check_collision_with_food(self, food):
        """Check if the snake's head collides with food"""
        return self.body[0] == food.position
    
    def get_head_position(self):
        """Get the position of the snake's head"""
        return self.body[0]
    
    def get_all_positions(self):
        """Get all positions occupied by the snake"""
        return list(self.body)
    
    def render_fire_particles(self, screen):
        """Render fire particles"""
        if not self.dragon_mode:
            return
            
        for particle in self.fire_particles:
            # Calculate color based on age
            age_factor = 1.0 - (particle['age'] / particle['lifetime'])
            
            if age_factor > 0.7:
                # Yellow/white
                color = (255, 255, 100, int(255 * age_factor))
            elif age_factor > 0.4:
                # Orange
                color = (255, 150, 0, int(255 * age_factor))
            else:
                # Red
                color = (255, 0, 0, int(255 * age_factor))
                
            # Draw particle
            pygame.draw.circle(
                screen,
                color,
                (int(particle['x']), int(particle['y'])),
                int(particle['size'])
            ) 