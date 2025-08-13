"""
Scoreboard - manages score tracking and high scores
"""

import json
import os
import time

class Scoreboard:
    def __init__(self, settings):
        self.settings = settings
        self.score = 0
        self.high_scores = []
        self.max_high_scores = 10
        
        # Score file path
        self.score_file = "snake_high_scores.json"
        
        # Load high scores
        self.load_high_scores()
    
    def add_points(self, points):
        """Add points to the current score"""
        self.score += points
    
    def reset(self):
        """Reset current score"""
        self.score = 0
    
    def check_high_score(self):
        """Check if current score is a high score"""
        if not self.high_scores or self.score > min(score for score, _, _ in self.high_scores):
            return True
        return len(self.high_scores) < self.max_high_scores
    
    def add_high_score(self, player_name="Player"):
        """Add current score to high scores"""
        # Only store the date, not the time
        timestamp = time.strftime("%Y-%m-%d")
        
        self.high_scores.append((self.score, player_name, timestamp))
        
        # Sort high scores in descending order
        self.high_scores.sort(reverse=True, key=lambda x: x[0])
        
        # Trim to max high scores
        self.high_scores = self.high_scores[:self.max_high_scores]
        
        # Save high scores
        self.save_high_scores()
    
    def get_rank(self):
        """Get the rank of the current score in the high scores"""
        for i, (score, _, _) in enumerate(self.high_scores):
            if self.score >= score:
                return i + 1
        
        if len(self.high_scores) < self.max_high_scores:
            return len(self.high_scores) + 1
        
        return None  # Not a high score
    
    def load_high_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists(self.score_file):
                with open(self.score_file, 'r') as f:
                    self.high_scores = json.load(f)
            else:
                # Default high scores if file doesn't exist
                self.high_scores = [
                    (100, "Player1", "2023-01-01"),
                    (80, "Player2", "2023-01-02"),
                    (60, "Player3", "2023-01-03"),
                ]
        except (json.JSONDecodeError, IOError):
            # Handle error by setting default high scores
            self.high_scores = [
                (100, "Player1", "2023-01-01"),
                (80, "Player2", "2023-01-02"),
                (60, "Player3", "2023-01-03"),
            ]
    
    def save_high_scores(self):
        """Save high scores to file"""
        try:
            with open(self.score_file, 'w') as f:
                json.dump(self.high_scores, f)
        except IOError:
            # Handle error - maybe log or show message to user
            pass
    
    def get_high_scores_formatted(self):
        """Get formatted high scores as a list of strings"""
        formatted_scores = []
        for i, (score, name, date) in enumerate(self.high_scores):
            formatted_scores.append(f"{i+1}. {name}: {score} ({date})")
        return formatted_scores 