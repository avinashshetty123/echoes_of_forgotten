import pygame
import math

class Projectile:
    def __init__(self, x, y, target_x, target_y, speed=5.0):
        self.x = x
        self.y = y
        self.radius = 6
        self.speed = speed
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        self.dx = dx / distance * speed
        self.dy = dy / distance * speed
        
        # Set lifetime
        self.lifetime = 120  # 2 seconds at 60 FPS
        self.damage = 15
        
    def update(self):
        # Move projectile
        self.x += self.dx
        self.y += self.dy
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius
        
        # Decrease lifetime
        self.lifetime -= 1
        return self.lifetime > 0
    
    def check_collision(self, player_rect):
        """Check if projectile collides with player"""
        return self.rect.colliderect(player_rect)
        
    def render(self, screen, camera_pos):
        # Calculate screen position
        screen_x = self.x - camera_pos[0]
        screen_y = self.y - camera_pos[1]
        
        # Only draw if on screen
        if -20 < screen_x < screen_x + 20 and -20 < screen_y < screen_y + 20:
            # Draw projectile with glow effect
            glow_radius = self.radius * 2
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 100, 0, 100), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (screen_x - glow_radius, screen_y - glow_radius))
            
            # Draw core
            pygame.draw.circle(screen, (255, 200, 0), (int(screen_x), int(screen_y)), self.radius)