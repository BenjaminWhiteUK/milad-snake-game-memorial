"""
User-configurable settings for Snake Game
Edit these values to customize game behavior
"""

#-------------------------#
# Snake Movement Settings #
#-------------------------#

# Speed settings (moves per second)
INITIAL_SNAKE_SPEED = 1.5  # Starting speed (will be overridden by difficulty)
MAX_SNAKE_SPEED = 10.0     # Maximum possible speed
SPEED_INCREASE_RATE = 0.05  # Speed increase per food item (percentage - reduced to avoid too rapid acceleration)

#-------------------#
# Special Features  #
#-------------------#

# Mario character settings
MARIO_ENABLED = True              # Set to False to disable Mario
MARIO_APPEARANCE_CHANCE = 0.95    # 95% chance of Mario appearing (very high)
MARIO_STAY_DURATION = 60          # 60 seconds on screen

# Power-up settings
MUSHROOM_DURATION = 60            # 60 seconds for mushroom power-up
DRAGON_MODE_DURATION = 60         # 60 seconds for dragon mode

# Special effects durations
FLAG_DURATION = 6                 # How long Iran flag displays (seconds)
EXPLOSION_DURATION = 3.5          # Nuclear explosion duration (seconds)

#------------------#
# Game Difficulty  #
#------------------#

# Overall difficulty setting (EASY, NORMAL, HARD)
DIFFICULTY = "NORMAL"

# Difficulty-specific settings
DIFFICULTY_SETTINGS = {
    "EASY": {
        "initial_snake_speed": 1.0,
        "max_snake_speed": 5.0,
        "special_food_chance": 0.15,
        "mario_appearance_chance": 0.95
    },
    "NORMAL": {
        "initial_snake_speed": 2.0,
        "max_snake_speed": 8.0,
        "special_food_chance": 0.1,
        "mario_appearance_chance": 0.95
    },
    "HARD": {
        "initial_snake_speed": 3.0,
        "max_snake_speed": 12.0,
        "special_food_chance": 0.05,
        "mario_appearance_chance": 0.95
    }
}

#------------------#
# Visual Settings  #
#------------------#

# Flag colors (Iran flag)
IRAN_FLAG_COLORS = [
    (0, 153, 0),     # Green
    (255, 255, 255), # White
    (238, 34, 34)    # Red
]

# Maximum explosion size (percentage of screen)
EXPLOSION_SIZE_FACTOR = 0.9  # 0.9 = 90% of screen height/width 