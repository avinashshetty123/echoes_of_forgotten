import pygame
import math
from .projectile import Projectile

class TurretEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 32, 32)
        self.detection_range = 250
        self.fire_cooldown = 120  # 2 seconds at 60 FPS
        self.cooldown_timer = 0
        self.active = False
        self.has_new_projectile = False
        self.new_projectile = None
        
        # Create texture
        self.texture = self._create_texture()
        
    def _create_texture(self):
        texture = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Base
        pygame.draw.rect(texture, (100, 100, 100, 220), (8, 16, 16, 16))
        
        # Turret head
        pygame.draw.circle(texture, (150, 150, 150, 220), (16, 16), 10)
        
        # Barrel
        pygame.draw.rect(texture, (80, 80, 80, 220), (16, 8, 4, 8))
        
        # Red targeting light
        pygame.draw.circle(texture, (255, 0, 0, 255), (16, 16), 3)
        
        return texture
        
    def update(self, player_pos):
        # Calculate distance to player
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Reset new projectile flag
        self.has_new_projectile = False
        
        # Check if player is in range
        if distance < self.detection_range:
            self.active = True
            
            # Update cooldown timer
            if self.cooldown_timer > 0:
                self.cooldown_timer -= 1
            
            # Fire projectile if cooldown is ready
            if self.cooldown_timer == 0:
                self.new_projectile = Projectile(self.x + 16, self.y + 16, player_pos[0], player_pos[1])
                self.has_new_projectile = True
                self.cooldown_timer = self.fire_cooldown
        else:
            self.active = False
    
    def get_projectile(self):
        """Get the newly created projectile"""
        if self.has_new_projectile:
            self.has_new_projectile = False
            return self.new_projectile
        return None
                
    def render(self, screen, camera_pos):
        # Calculate screen position
        screen_x = self.x - camera_pos[0]
        screen_y = self.y - camera_pos[1]
        
        # Only draw if on screen
        if -50 < screen_x < screen_x + 50 and -50 < screen_y < screen_y + 50:
            # Draw detection range if active
            if self.active:
                range_surf = pygame.Surface((self.detection_range*2, self.detection_range*2), pygame.SRCALPHA)
                pygame.draw.circle(range_surf, (255, 0, 0, 20), 
                                 (self.detection_range, self.detection_range), self.detection_range)
                pygame.draw.circle(range_surf, (255, 0, 0, 40), 
                                 (self.detection_range, self.detection_range), self.detection_range, 2)
                screen.blit(range_surf, (screen_x + 16 - self.detection_range, screen_y + 16 - self.detection_range))
            
            # Draw turret
            screen.blit(self.texture, (screen_x, screen_y))