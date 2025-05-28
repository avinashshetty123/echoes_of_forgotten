import pygame
import math
import random
import os
from .constants import *

class Warden:
    def __init__(self, x, y, player):
        """Initialize the Warden enemy AI."""
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 30, 30)
        self.speed = WARDEN_SPEED
        self.player = player
        self.detection_radius = WARDEN_DETECTION_RADIUS
        self.state = "PATROLLING"  # PATROLLING, HUNTING, INVESTIGATING
        self.patrol_points = []
        self.current_patrol_point = 0
        self.investigation_timer = 0
        self.investigation_duration = 180  # frames (3 seconds)
        self.last_heard_position = None
        
        # Generate patrol points
        self._generate_patrol_points()
    
    def _generate_patrol_points(self):
        """Generate random patrol points for the Warden."""
        num_points = 5
        for _ in range(num_points):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            self.patrol_points.append((x, y))
    
    def update(self):
        """Update the Warden's position and state."""
        if self.state == "PATROLLING":
            self._patrol()
            
            # Check if player made a sound recently
            if pygame.time.get_ticks() - self.player.last_sound_time < 1000:
                self.state = "INVESTIGATING"
                self.last_heard_position = (self.player.x, self.player.y)
                self.investigation_timer = 0
        
        elif self.state == "INVESTIGATING":
            self._investigate()
            
            # Check if player is visible during investigation
            distance = math.sqrt((self.x - self.player.x)**2 + (self.y - self.player.y)**2)
            if distance < self.detection_radius:
                self.state = "HUNTING"
        
        elif self.state == "HUNTING":
            self._hunt()
            
            # If player hasn't made sound in a while and is far enough, go back to patrolling
            if pygame.time.get_ticks() - self.player.last_sound_time > 5000:
                distance = math.sqrt((self.x - self.player.x)**2 + (self.y - self.player.y)**2)
                if distance > self.detection_radius * 1.5:
                    self.state = "PATROLLING"
    
    def _patrol(self):
        """Move between patrol points."""
        target_x, target_y = self.patrol_points[self.current_patrol_point]
        
        # Move towards the current patrol point
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 5:  # If not at the target point
            # Normalize direction vector
            dx /= distance
            dy /= distance
            
            # Move towards target
            self.x += dx * self.speed
            self.y += dy * self.speed
        else:
            # Move to next patrol point
            self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def _investigate(self):
        """Move to the last heard position and look around."""
        target_x, target_y = self.last_heard_position
        
        # Move towards the sound source
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 5:  # If not at the target point
            # Normalize direction vector
            dx /= distance
            dy /= distance
            
            # Move towards target
            self.x += dx * self.speed
            self.y += dy * self.speed
        else:
            # Increment investigation timer
            self.investigation_timer += 1
            
            # If investigation complete, go back to patrolling
            if self.investigation_timer >= self.investigation_duration:
                self.state = "PATROLLING"
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def _hunt(self):
        """Chase the player directly."""
        # Move towards the player
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:  # Avoid division by zero
            # Normalize direction vector
            dx /= distance
            dy /= distance
            
            # Move towards player
            self.x += dx * self.speed * 1.2  # Slightly faster when hunting
            self.y += dy * self.speed * 1.2
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def check_player_collision(self):
        """Check if the Warden has caught the player."""
        return self.rect.colliderect(self.player.rect)
    
    def render(self, surface, echo_active):
        """Render the Warden (only visible during echo or when close)."""
        # Calculate distance to player
        distance = math.sqrt((self.x - self.player.x)**2 + (self.y - self.player.y)**2)
        
        # Only render if echo is active or Warden is very close to player
        if echo_active or distance < 100:
            try:
                # Try to use the sprite if available
                assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                         "game", "assets", "images")
                warden_img = pygame.image.load(os.path.join(assets_dir, "warden.png")).convert_alpha()
                
                # Adjust visibility based on state and distance
                alpha = 255 if echo_active else int(255 * (1 - distance/100))
                
                # Colorize based on state
                if self.state == "PATROLLING":
                    color_overlay = (100, 100, 150)  # Bluish
                elif self.state == "INVESTIGATING":
                    color_overlay = (150, 100, 100)  # Reddish
                else:  # HUNTING
                    color_overlay = (200, 50, 50)  # Red
                
                # Apply color and alpha
                warden_copy = warden_img.copy()
                warden_copy.fill(color_overlay, special_flags=pygame.BLEND_RGBA_MULT)
                warden_copy.set_alpha(alpha)
                
                # Draw with a ghostly effect
                surface.blit(warden_copy, self.rect.topleft)
                
                # Add glowing eyes effect
                glow_radius = 5 + int(3 * math.sin(pygame.time.get_ticks() / 200))
                glow_color = (255, 200, 100, 150)
                
                # Create glow surfaces
                glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
                
                # Position eyes
                eye_offset_x = 8
                eye_offset_y = 10
                surface.blit(glow_surf, 
                           (self.rect.x + eye_offset_x - glow_radius, 
                            self.rect.y + eye_offset_y - glow_radius))
                surface.blit(glow_surf, 
                           (self.rect.x + self.rect.width - eye_offset_x - glow_radius, 
                            self.rect.y + eye_offset_y - glow_radius))
                
            except:
                # Fallback to simple rendering if sprite loading fails
                # Render differently based on state
                if self.state == "PATROLLING":
                    color = (100, 100, 150, 150)  # Bluish, semi-transparent
                elif self.state == "INVESTIGATING":
                    color = (150, 100, 100, 180)  # Reddish, more visible
                else:  # HUNTING
                    color = (200, 50, 50, 200)  # Red, very visible
                
                # Draw the Warden as a shadowy figure
                pygame.draw.rect(surface, color, self.rect)
                
                # Add glowing eyes effect
                eye_radius = 3 + int(2 * math.sin(pygame.time.get_ticks() / 200))
                eye_offset = 7
                pygame.draw.circle(surface, (255, 255, 200), 
                                  (int(self.rect.x + eye_offset), int(self.rect.y + 10)), 
                                  eye_radius)
                pygame.draw.circle(surface, (255, 255, 200), 
                                  (int(self.rect.x + self.rect.width - eye_offset), int(self.rect.y + 10)), 
                                  eye_radius)