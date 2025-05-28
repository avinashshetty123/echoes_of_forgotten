import pygame
import math
import os
from .constants import *

class AnimatedPlayer:
    def __init__(self, x, y, sound_manager):
        """Initialize the player character with animations."""
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = PLAYER_SPEED
        self.sound_manager = sound_manager
        self.last_sound_time = 0
        self.sound_cooldown = SOUND_COOLDOWN
        
        # Game stats
        self.score = 0
        self.health = 100
        self.max_health = 100
        
        # Animation state
        self.direction = "down"  # down, up, left, right
        self.moving = False
        self.frame = 0
        self.animation_speed = 0.15
        self.last_update = pygame.time.get_ticks()
        
        # Create sprite sheets
        self._create_animations()
    
    def _create_animations(self):
        """Create pixelated player animations."""
        # Create sprite sheet with different colored pixels
        self.sprites = {}
        
        # Create base sprite (16x16 pixels, scaled up to 32x32)
        base_sprite = pygame.Surface((16, 16), pygame.SRCALPHA)
        
        # Body color
        body_color = (50, 150, 200)  # Blue-ish
        
        # Down-facing sprite
        down_sprites = []
        for i in range(4):  # 4 animation frames
            sprite = base_sprite.copy()
            # Head
            pygame.draw.rect(sprite, body_color, (6, 2, 4, 4))
            # Body
            pygame.draw.rect(sprite, body_color, (4, 6, 8, 6))
            # Legs - animate walking
            leg_offset = abs((i % 4) - 2)
            pygame.draw.rect(sprite, body_color, (4, 12, 3, 4 - leg_offset))
            pygame.draw.rect(sprite, body_color, (9, 12, 3, 4 - (2 - leg_offset if leg_offset < 2 else 0)))
            # Scale up
            sprite = pygame.transform.scale(sprite, (self.width, self.height))
            down_sprites.append(sprite)
        self.sprites["down"] = down_sprites
        
        # Up-facing sprite
        up_sprites = []
        for i in range(4):
            sprite = base_sprite.copy()
            # Head
            pygame.draw.rect(sprite, body_color, (6, 2, 4, 4))
            # Body
            pygame.draw.rect(sprite, body_color, (4, 6, 8, 6))
            # Legs - animate walking
            leg_offset = abs((i % 4) - 2)
            pygame.draw.rect(sprite, body_color, (4, 12, 3, 4 - leg_offset))
            pygame.draw.rect(sprite, body_color, (9, 12, 3, 4 - (2 - leg_offset if leg_offset < 2 else 0)))
            # Scale up
            sprite = pygame.transform.scale(sprite, (self.width, self.height))
            up_sprites.append(sprite)
        self.sprites["up"] = up_sprites
        
        # Left-facing sprite
        left_sprites = []
        for i in range(4):
            sprite = base_sprite.copy()
            # Head
            pygame.draw.rect(sprite, body_color, (5, 2, 4, 4))
            # Body
            pygame.draw.rect(sprite, body_color, (4, 6, 6, 6))
            # Legs - animate walking
            leg_offset = abs((i % 4) - 2)
            pygame.draw.rect(sprite, body_color, (4, 12, 3, 4 - leg_offset))
            pygame.draw.rect(sprite, body_color, (7, 12, 3, 4 - (2 - leg_offset if leg_offset < 2 else 0)))
            # Scale up
            sprite = pygame.transform.scale(sprite, (self.width, self.height))
            left_sprites.append(sprite)
        self.sprites["left"] = left_sprites
        
        # Right-facing sprite (flip left sprites)
        right_sprites = []
        for sprite in left_sprites:
            right_sprites.append(pygame.transform.flip(sprite, True, False))
        self.sprites["right"] = right_sprites
    
    def update(self):
        """Update player position and animation based on keyboard input."""
        keys = pygame.key.get_pressed()
        
        # Reset movement state
        old_moving = self.moving
        self.moving = False
        old_direction = self.direction
        
        # Movement
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
            self.direction = "left"
            self.moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
            self.direction = "right"
            self.moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
            if not self.moving:  # Only change direction if not moving horizontally
                self.direction = "up"
            self.moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
            if not self.moving:  # Only change direction if not moving horizontally
                self.direction = "down"
            self.moving = True
        
        # Apply movement
        self.x += dx
        self.y += dy
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Update animation
        current_time = pygame.time.get_ticks()
        if self.moving and (current_time - self.last_update > 1000 * self.animation_speed):
            self.last_update = current_time
            self.frame = (self.frame + 1) % len(self.sprites[self.direction])
            
            # Play footstep sounds when moving
            if self.frame == 1 or self.frame == 3:
                self.sound_manager.play_sound("footstep", 0.2)
    
    def emit_sound(self):
        """Emit a sound for echolocation if cooldown has passed."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_sound_time > self.sound_cooldown:
            self.last_sound_time = current_time
            return True
        return False
    
    def take_damage(self, amount):
        """Take damage and return True if still alive."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return False
        return True
    
    def heal(self, amount):
        """Heal the player."""
        self.health = min(self.max_health, self.health + amount)
    
    def render(self, surface, camera_pos=(0, 0)):
        """Render the player character with animation."""
        # Calculate screen position
        screen_x = self.x - camera_pos[0]
        screen_y = self.y - camera_pos[1]
        
        # Draw the current animation frame
        current_sprite = self.sprites[self.direction][self.frame if self.moving else 0]
        surface.blit(current_sprite, (screen_x, screen_y))
        
        # Add a subtle glow effect
        if pygame.time.get_ticks() % 40 == 0:
            glow_size = 40
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            glow_color = (100, 150, 255, 30)
            pygame.draw.circle(glow_surf, glow_color, (glow_size//2, glow_size//2), glow_size//2)
            surface.blit(glow_surf, 
                       (screen_x + self.width//2 - glow_size//2, 
                        screen_y + self.height//2 - glow_size//2))