"""
Core game logic and main game loop
"""

import pygame
import time
import random
from game.snake import Snake
from game.food import Food
from game.special_items import Mario, PowerUpEffects
from ui.renderer import Renderer
from ui.menu import Menu
from ui.effects import Effects
from utils.scoreboard import Scoreboard

class Game:
    def __init__(self, settings):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Advanced Snake Game")
        
        # Game components
        self.settings = settings
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "MENU"  # MENU, PLAYING, PAUSED, GAME_OVER
        
        # Initialize screen
        self.screen = pygame.display.set_mode(
            (settings.screen_width, settings.screen_height)
        )
        
        # Initialize game objects
        self.snake = Snake(settings)
        self.food = Food(settings)
        
        # Initialize special features
        self.mario = Mario(settings)
        self.power_up_effects = PowerUpEffects(settings, self.screen)
        
        # Initialize UI components
        self.renderer = Renderer(self.screen, settings)
        self.menu = Menu(self.screen, settings)
        self.effects = Effects(self.screen, settings)
        self.scoreboard = Scoreboard(settings)
        
        # Last time Mario tried to spawn
        self.last_mario_try_time = 0
        self.mario_try_interval = 5  # seconds
        
        # Timing variables
        self.frame_count = 0
    
    def process_events(self):
        """Process keyboard events and update game state"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            # Handle different game states
            if self.game_state == "MENU":
                self.menu.handle_event(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.game_state = "PLAYING"
                    
            elif self.game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "PAUSED"
                    elif event.key == pygame.K_UP and self.snake.direction != "DOWN":
                        self.snake.change_direction("UP")
                    elif event.key == pygame.K_DOWN and self.snake.direction != "UP":
                        self.snake.change_direction("DOWN")
                    elif event.key == pygame.K_LEFT and self.snake.direction != "RIGHT":
                        self.snake.change_direction("LEFT")
                    elif event.key == pygame.K_RIGHT and self.snake.direction != "LEFT":
                        self.snake.change_direction("RIGHT")
                        
            elif self.game_state == "PAUSED":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "PLAYING"
                    elif event.key == pygame.K_q:
                        self.game_state = "MENU"
                        self.reset_game()
                        
            elif self.game_state == "GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.game_state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "MENU"
                        self.reset_game()
    
    def update(self):
        """Update game objects based on game state"""
        if self.game_state == "PLAYING":
            self.frame_count += 1
            
            # Check if any power-up effects are active
            if self.power_up_effects.update():
                # Apply dragon mode to snake
                self.snake.set_dragon_mode(self.power_up_effects.dragon_mode_active)
            
            # Move snake
            snake_moved = self.snake.move()
            
            # Only process game updates when snake actually moves
            if snake_moved:
                # Check for collisions - only with self, not with walls
                if self.snake.check_collision_with_self():
                    self.game_state = "GAME_OVER"
                    self.effects.play_effect("game_over")
                    return
                    
                # Check if snake eats food
                if self.snake.check_collision_with_food(self.food):
                    self.snake.grow()
                    self.food.respawn(self.snake)
                    self.scoreboard.add_points(10)
                    self.effects.play_effect("eat")
                    
                    # Increase speed very slightly based on score
                    self.snake.increase_speed()
                
                # Check if snake collides with mushroom
                if self.mario.check_mushroom_collision(self.snake):
                    # Activate all special effects
                    self.power_up_effects.activate_mushroom_power()
                    self.scoreboard.add_points(50)  # Bonus points
            
            # Try to spawn Mario occasionally
            current_time = time.time()
            if current_time - self.last_mario_try_time > self.mario_try_interval:
                self.last_mario_try_time = current_time
                self.mario.try_spawn()
            
            # Update Mario if active
            self.mario.update(self.snake)
    
    def render(self):
        """Render game elements based on game state"""
        # Clear screen
        self.screen.fill(self.settings.bg_color)
        
        if self.game_state == "MENU":
            self.menu.render()
            
        elif self.game_state == "PLAYING" or self.game_state == "PAUSED":
            # Render game elements
            self.renderer.render_grid()
            self.renderer.render_food(self.food)
            
            # Render Mario and mushroom if active
            self.renderer.render_mario(self.mario)
            
            # Render the snake
            self.renderer.render_snake(self.snake)
            
            # Render score
            self.renderer.render_score(self.scoreboard.score)
            
            # Render special effects
            self.power_up_effects.render()
            
            # Show pause overlay if paused
            if self.game_state == "PAUSED":
                self.renderer.render_pause_overlay()
                
        elif self.game_state == "GAME_OVER":
            # Render game elements with overlay
            self.renderer.render_grid()
            self.renderer.render_food(self.food)
            self.renderer.render_snake(self.snake)
            self.renderer.render_score(self.scoreboard.score)
            self.renderer.render_game_over(self.scoreboard.score)
            
        # Update display
        pygame.display.flip()
    
    def reset_game(self):
        """Reset the game to initial state"""
        print(f"Resetting game with difficulty: {self.settings.difficulty}")
        print(f"Initial snake speed: {self.settings.initial_snake_speed}")
        
        # Re-create snake with current settings
        self.snake = Snake(self.settings)
        
        # Reset food
        self.food = Food(self.settings)
        self.food.respawn(self.snake)
        
        # Reset special features
        self.mario = Mario(self.settings)
        self.power_up_effects = PowerUpEffects(self.settings, self.screen)
        
        # Reset score and timing
        self.scoreboard.reset()
        self.last_mario_try_time = time.time()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.process_events()
            self.update()
            self.render()
            self.clock.tick(self.settings.fps) 