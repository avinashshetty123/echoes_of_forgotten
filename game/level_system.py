import pygame
import json
import os
import math
from .constants import *

class LevelSystem:
    def __init__(self):
        self.current_level = 1
        self.max_level = 5
        self.levels = [
            {
                "name": "Nursery",
                "ritual_items_required": 3,
                "enemy_count": 3,
                "warden_speed_modifier": 1.0,
                "description": "The abandoned nursery. Find 3 ritual items to unlock the door."
            },
            {
                "name": "Dining Hall",
                "ritual_items_required": 5,
                "enemy_count": 4,
                "warden_speed_modifier": 1.1,
                "description": "The dining hall where children once gathered. Find 5 ritual items."
            },
            {
                "name": "Dormitory",
                "ritual_items_required": 7,
                "enemy_count": 5,
                "warden_speed_modifier": 1.2,
                "description": "The dormitory where children slept. Find 7 ritual items."
            },
            {
                "name": "Library",
                "ritual_items_required": 9,
                "enemy_count": 6,
                "warden_speed_modifier": 1.3,
                "description": "The library holds dark secrets. Find 9 ritual items."
            },
            {
                "name": "Ritual Chamber",
                "ritual_items_required": 12,
                "enemy_count": 8,
                "warden_speed_modifier": 1.5,
                "description": "The final chamber. Complete the ritual with 12 items to escape."
            }
        ]
        
        # High scores for each level
        self.high_scores = [0] * self.max_level
        self.load_high_scores()
        
    def get_current_level_data(self):
        """Get data for the current level"""
        return self.levels[self.current_level - 1]
        
    def advance_level(self):
        """Advance to the next level if possible"""
        if self.current_level < self.max_level:
            self.current_level += 1
            return True
        return False
        
    def update_high_score(self, level, score):
        """Update high score for a level if the new score is higher"""
        if level <= self.max_level and score > self.high_scores[level - 1]:
            self.high_scores[level - 1] = score
            self.save_high_scores()
            return True
        return False
        
    def save_high_scores(self):
        """Save high scores to a file"""
        try:
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "game", "save")
            os.makedirs(save_dir, exist_ok=True)
            
            save_path = os.path.join(save_dir, "high_scores.json")
            with open(save_path, 'w') as f:
                json.dump(self.high_scores, f)
        except Exception as e:
            print(f"Error saving high scores: {e}")
            
    def load_high_scores(self):
        """Load high scores from a file"""
        try:
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "game", "save")
            save_path = os.path.join(save_dir, "high_scores.json")
            
            if os.path.exists(save_path):
                with open(save_path, 'r') as f:
                    scores = json.load(f)
                    # Make sure we have the right number of scores
                    if len(scores) == self.max_level:
                        self.high_scores = scores
        except Exception as e:
            print(f"Error loading high scores: {e}")
            
class LevelTransitionScreen:
    def __init__(self, screen, level_data):
        self.screen = screen
        self.level_data = level_data
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.timer = 0
        self.done = False
        
    def update(self):
        self.timer += 1
        if self.timer > 300:  # 5 seconds
            self.done = True
            
    def render(self):
        # Fill background
        self.screen.fill((10, 5, 15))
        
        # Draw level name
        level_text = self.font_large.render(f"Level {self.level_data['name']}", True, (200, 50, 200))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 150))
        
        # Draw description
        desc_text = self.font_medium.render(self.level_data['description'], True, (200, 200, 200))
        self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, 250))
        
        # Draw ritual items required
        items_text = self.font_small.render(f"Ritual Items Required: {self.level_data['ritual_items_required']}", True, (200, 200, 200))
        self.screen.blit(items_text, (SCREEN_WIDTH // 2 - items_text.get_width() // 2, 320))
        
        # Draw continue prompt
        if self.timer > 100:
            alpha = min(255, (self.timer - 100) * 2)
            continue_text = self.font_small.render("Press any key to begin...", True, (150, 150, 150))
            continue_text.set_alpha(alpha)
            self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 400))
            
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and self.timer > 100:
                self.done = True
        return self.done