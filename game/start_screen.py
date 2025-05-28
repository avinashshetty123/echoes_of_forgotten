import pygame
import math
import random
from .constants import *

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.selected_option = 0
        self.options = ["Start Game", "Controls", "Settings", "Quit"]
        self.show_controls = False
        self.show_settings = False
        self.warden_speed = 1.5  # Default warden speed
        
        # Create background with floating symbols
        self.symbols = []
        for i in range(20):
            self.symbols.append({
                "x": random.randint(0, SCREEN_WIDTH),
                "y": random.randint(0, SCREEN_HEIGHT),
                "size": random.randint(5, 15),
                "speed": random.uniform(0.5, 1.5),
                "angle": random.uniform(0, 2 * math.pi)
            })
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.show_controls:
                    self.show_controls = False
                    return None
                elif self.show_settings:
                    if event.key == pygame.K_UP:
                        self.warden_speed += 0.1
                        if self.warden_speed > 3.0:
                            self.warden_speed = 3.0
                    elif event.key == pygame.K_DOWN:
                        self.warden_speed -= 0.1
                        if self.warden_speed < 0.5:
                            self.warden_speed = 0.5
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.show_settings = False
                else:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:  # Start Game
                            return "START"
                        elif self.selected_option == 1:  # Controls
                            self.show_controls = True
                        elif self.selected_option == 2:  # Settings
                            self.show_settings = True
                        elif self.selected_option == 3:  # Quit
                            return "QUIT"
        return None
    
    def update(self):
        # Update floating symbols
        for symbol in self.symbols:
            symbol["y"] += symbol["speed"]
            if symbol["y"] > SCREEN_HEIGHT:
                symbol["y"] = 0
                symbol["x"] = random.randint(0, SCREEN_WIDTH)
    
    def render(self):
        # Fill background
        self.screen.fill((10, 5, 15))
        
        # Draw floating symbols
        for symbol in self.symbols:
            pygame.draw.circle(
                self.screen, 
                (100, 0, 100, 150), 
                (int(symbol["x"]), int(symbol["y"])), 
                symbol["size"]
            )
        
        if self.show_controls:
            self._render_controls()
        elif self.show_settings:
            self._render_settings()
        else:
            self._render_menu()
    
    def _render_menu(self):
        # Draw title with pulsing effect
        pulse = int(20 * math.sin(pygame.time.get_ticks() / 200))
        title_color = (200 + pulse, 50, 200 + pulse)
        title = self.font_large.render("DARK RITUAL", True, title_color)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        
        # Draw subtitle
        subtitle = self.font_medium.render("An Endless Horror", True, (150, 150, 150))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 220))
        
        # Draw menu options
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                color = (255, 255, 255)
                # Draw selector
                pygame.draw.circle(
                    self.screen, 
                    (200, 50, 200), 
                    (SCREEN_WIDTH // 2 - 100, 300 + i * 50), 
                    5
                )
            else:
                color = (150, 150, 150)
            
            option_text = self.font_medium.render(option, True, color)
            self.screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 300 + i * 50))
    
    def _render_controls(self):
        # Draw controls screen
        title = self.font_medium.render("CONTROLS", True, (200, 200, 200))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        controls = [
            "WASD / Arrow Keys: Move",
            "SPACE: Reveal spirits and items",
            "ESC: Pause game",
            "",
            "Collect ritual items to power the portal",
            "Avoid the spirits at all costs",
            "The world is infinite - explore to find more items",
            "",
            "Warden spirits will hear your reveal sound",
            "and move toward your location"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, (200, 200, 200))
            self.screen.blit(control_text, (SCREEN_WIDTH // 2 - control_text.get_width() // 2, 180 + i * 30))
        
        back_text = self.font_small.render("Press any key to return", True, (150, 150, 150))
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 500))
    
    def _render_settings(self):
        # Draw settings screen
        title = self.font_medium.render("SETTINGS", True, (200, 200, 200))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Warden speed setting
        speed_text = self.font_medium.render(f"Warden Speed: {self.warden_speed:.1f}", True, (200, 200, 200))
        self.screen.blit(speed_text, (SCREEN_WIDTH // 2 - speed_text.get_width() // 2, 200))
        
        # Draw slider
        slider_width = 300
        slider_x = SCREEN_WIDTH // 2 - slider_width // 2
        slider_y = 250
        
        # Draw slider background
        pygame.draw.rect(self.screen, (100, 100, 100), (slider_x, slider_y, slider_width, 10))
        
        # Draw slider position
        pos_x = slider_x + int((self.warden_speed - 0.5) / 2.5 * slider_width)
        pygame.draw.circle(self.screen, (200, 50, 200), (pos_x, slider_y + 5), 10)
        
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to adjust speed",
            "Press ENTER or ESC to return"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 30))
        
        # Difficulty explanation
        if self.warden_speed < 1.0:
            diff_text = "Easy - Wardens move slowly"
        elif self.warden_speed < 2.0:
            diff_text = "Normal - Balanced warden speed"
        else:
            diff_text = "Hard - Wardens move quickly"
            
        diff_render = self.font_medium.render(diff_text, True, (200, 200, 200))
        self.screen.blit(diff_render, (SCREEN_WIDTH // 2 - diff_render.get_width() // 2, 400))