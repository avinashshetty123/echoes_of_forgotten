import pygame
import math
from .constants import *

class StoryScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.timer = 0
        self.done = False
        
        # Story text
        self.story_title = "Echoes of the Forgotten"
        self.story_text = [
            "You are Elara, a blind girl with a gift for sensing the supernatural.",
            "You've awakened in an abandoned orphanage, your memories fragmented.",
            "",
            "The spirits of the orphanage are restless, trapped by dark rituals.",
            "You must collect ritual items to complete the ceremony and free them.",
            "",
            "Use your ability to sense the spirits, but be careful...",
            "Every time you reveal the world around you, they can sense you too.",
            "",
            "Complete the ritual, escape the orphanage, and discover your past."
        ]
        
    def update(self):
        self.timer += 1
        if self.timer > 600:  # 10 seconds
            self.done = True
            
    def render(self):
        # Fill background
        self.screen.fill((10, 5, 15))
        
        # Draw title with pulsing effect
        pulse = int(20 * math.sin(pygame.time.get_ticks() / 200))
        title_color = (200 + pulse, 50, 200 + pulse)
        title = self.font_large.render(self.story_title, True, title_color)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Draw story text with fade-in effect
        for i, line in enumerate(self.story_text):
            alpha = min(255, self.timer * 2 - i * 20)
            if alpha <= 0:
                continue
                
            text_surf = self.font_medium.render(line, True, (200, 200, 200))
            text_surf.set_alpha(alpha)
            self.screen.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, 180 + i * 30))
        
        # Draw continue prompt if near end
        if self.timer > 400:
            alpha = min(255, (self.timer - 400) * 2)
            continue_text = self.font_small.render("Press any key to continue...", True, (150, 150, 150))
            continue_text.set_alpha(alpha)
            self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 500))
            
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and self.timer > 200:
                self.done = True
        return self.done