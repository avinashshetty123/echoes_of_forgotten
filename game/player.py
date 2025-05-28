import pygame
import time
import os
import math
from .constants import *

class Player:
    def __init__(self, x, y, sound_manager):
        """Initialize the player character (Elara)."""
        self.x = x
        self.y = y
        
        # Load player sprite
        try:
            player_img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                          "game", "assets", "images", "player.png")
            self.image = pygame.image.load(player_img_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))
        except:
            # Fallback if image loading fails
            self.image = None
        
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = PLAYER_SPEED
        self.sound_manager = sound_manager
        self.last_sound_time = 0
        self.sound_cooldown = SOUND_COOLDOWN  # milliseconds
        self.memories_collected = {memory_type: False for memory_type in MEMORY_TYPES}
        
        # Animation state
        self.facing = "right"
        self.moving = False
        
        # Game stats
        self.score = 0
        self.health = 100
        self.keys_collected = 0
    
    def update(self):
        """Update player position based on keyboard input."""
        keys = pygame.key.get_pressed()
        
        # Reset movement state
        self.moving = False
        
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            self.facing = "left"
            self.moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            self.facing = "right"
            self.moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
            self.moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            self.moving = True
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.x
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.x = self.rect.x
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.y
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.y = self.rect.y
            
        # Play footstep sounds when moving
        if self.moving and pygame.time.get_ticks() % 20 == 0:
            self.sound_manager.play_sound("footstep", 0.2)
    
    def emit_sound(self):
        """Emit a sound for echolocation if cooldown has passed."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_sound_time > self.sound_cooldown:
            self.last_sound_time = current_time
            return True
        return False
    
    def collect_memory(self, memory_type):
        """Mark a memory fragment as collected."""
        self.memories_collected[memory_type] = True
    
    def get_ending(self):
        """Determine the ending based on collected memories."""
        # Count collected memories
        collected_count = sum(self.memories_collected.values())
        
        if collected_count == len(MEMORY_TYPES):
            return "REDEMPTION"
        elif collected_count >= len(MEMORY_TYPES) // 2:
            return "DENIAL"
        else:
            return "POSSESSION"
    
    def render(self, surface):
        """Render the player character."""
        if self.image:
            # Use sprite if available
            # Apply a slight pulsing effect when moving
            if self.moving:
                pulse = int(10 * abs(math.sin(pygame.time.get_ticks() / 200)))
                glow_surf = pygame.Surface((self.rect.width + pulse*2, self.rect.height + pulse*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (100, 200, 255, 50), 
                                  (self.rect.width//2 + pulse, self.rect.height//2 + pulse), 
                                  self.rect.width//2 + pulse)
                surface.blit(glow_surf, (self.rect.x - pulse, self.rect.y - pulse))
            
            # Flip the image based on facing direction
            if self.facing == "left":
                flipped_image = pygame.transform.flip(self.image, True, False)
                surface.blit(flipped_image, self.rect)
            else:
                surface.blit(self.image, self.rect)
        else:
            # Fallback to a more visible player representation
            pygame.draw.circle(surface, (100, 200, 255), self.rect.center, 10)
            # Draw a direction indicator
            direction_x = self.rect.centerx + (10 if self.facing == "right" else -10)
            pygame.draw.circle(surface, (255, 255, 255), (direction_x, self.rect.centery), 4)