import pygame
import random
import math
import os
from .constants import *

class Surface:
    def __init__(self, rect, surface_type):
        """Initialize a surface with specific echo properties."""
        self.rect = rect
        self.type = surface_type
        self.properties = SURFACE_TYPES[surface_type]
        self.color = self.properties["color"]
        self.echo_intensity = self.properties["echo_intensity"]

class MemoryFragment:
    def __init__(self, x, y, memory_type, content):
        """Initialize a memory fragment."""
        self.rect = pygame.Rect(x, y, 20, 20)
        self.type = memory_type
        self.content = content
        self.collected = False
        self.glow_value = 0
        self.glow_direction = 1

    def update(self):
        """Update the memory fragment's visual effect."""
        # Pulsing glow effect
        self.glow_value += self.glow_direction * 2
        if self.glow_value >= 100:
            self.glow_value = 100
            self.glow_direction = -1
        elif self.glow_value <= 0:
            self.glow_value = 0
            self.glow_direction = 1

    def render(self, surface):
        """Render the memory fragment."""
        # Draw a glowing orb
        glow_radius = 15 + (self.glow_value / 10)
        glow_color = (200, 200, 255, 50 + self.glow_value)
        
        # Create a surface for the glow
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
        
        # Blit the glow surface
        surface.blit(glow_surface, (self.rect.centerx - glow_radius, self.rect.centery - glow_radius))
        
        # Draw the core
        pygame.draw.circle(surface, (255, 255, 255), self.rect.center, 5)

class Enemy:
    def __init__(self, x, y, enemy_type, patrol_radius=100):
        self.x = x
        self.y = y
        self.type = enemy_type  # "warden", "crawler", "phantom"
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = 1.0 if enemy_type == "crawler" else 1.5 if enemy_type == "phantom" else 1.2
        self.patrol_radius = patrol_radius
        self.start_x = x
        self.start_y = y
        self.direction = pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize()
        self.state = "patrolling"  # patrolling, hunting, investigating
        self.detection_radius = 100  # Reduced detection radius
        self.texture = None
        self.last_state_change = 0
        self.target_x = None
        self.target_y = None
        
    def update(self, player_pos, sound_made=False, obstacles=None):
        # Calculate distance to player
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # State transitions
        current_time = pygame.time.get_ticks()
        
        # Phantom can see through walls
        if self.type == "phantom" and distance < self.detection_radius:
            self.state = "hunting"
            self.last_state_change = current_time
        
        # Crawler is attracted to sound
        elif self.type == "crawler" and sound_made and distance < self.detection_radius * 1.5:
            self.state = "investigating"
            self.target_x, self.target_y = player_pos
            self.last_state_change = current_time
        
        # Return to patrolling after some time
        elif self.state != "patrolling" and current_time - self.last_state_change > 5000:
            self.state = "patrolling"
        
        # Movement based on state
        if self.state == "patrolling":
            # Random movement within patrol radius
            self.x += self.direction.x * self.speed
            self.y += self.direction.y * self.speed
            
            # Change direction if going too far from start point
            current_distance = math.sqrt((self.x - self.start_x)**2 + (self.y - self.start_y)**2)
            if current_distance > self.patrol_radius:
                # Head back toward start point
                to_start = pygame.Vector2(self.start_x - self.x, self.start_y - self.y).normalize()
                self.direction = to_start
            
            # Randomly change direction occasionally
            if random.random() < 0.02:
                self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                
        elif self.state == "investigating":
            # Move toward last heard position
            if self.target_x is not None:
                to_target = pygame.Vector2(self.target_x - self.x, self.target_y - self.y)
                if to_target.length() > 0:
                    to_target = to_target.normalize()
                    self.x += to_target.x * self.speed
                    self.y += to_target.y * self.speed
                else:
                    # Reached target, go back to patrolling
                    self.state = "patrolling"
                    
        elif self.state == "hunting":
            # Move directly toward player
            if distance > 0:
                to_player = pygame.Vector2(dx, dy).normalize()
                self.x += to_player.x * self.speed * 1.2  # Move faster when hunting
                self.y += to_player.y * self.speed * 1.2
        
        # Update rectangle position
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Avoid obstacles if provided
        if obstacles:
            for obstacle in obstacles:
                if self.rect.colliderect(obstacle):
                    # Back up and change direction
                    self.x -= self.direction.x * self.speed * 2
                    self.y -= self.direction.y * self.speed * 2
                    self.rect.x = self.x
                    self.rect.y = self.y
                    
                    # Choose a new direction
                    self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        
        # Keep within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.x
            self.direction.x *= -1
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.x = self.rect.x
            self.direction.x *= -1
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.y
            self.direction.y *= -1
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.y = self.rect.y
            self.direction.y *= -1

class Level:
    def __init__(self, level_name, sound_manager):
        """Initialize a level with surfaces and memory fragments."""
        self.name = level_name
        self.sound_manager = sound_manager
        self.surfaces = []
        self.memory_fragments = []
        self.doors = []
        self.collectables = []
        self.enemies = []
        self.exit = None
        self.ritual_items_required = 5
        self.ritual_items_collected = 0
        self.highest_score = 0
        
        # Create simple surfaces instead of loading textures
        try:
            # Memory texture (blue glow)
            self.memory_texture = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.memory_texture, (100, 100, 255, 200), (16, 16), 14)
            pygame.draw.circle(self.memory_texture, (200, 200, 255, 255), (16, 16), 8)
            
            # Ritual texture (purple glow)
            self.ritual_texture = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.ritual_texture, (150, 50, 200, 200), (16, 16), 14)
            pygame.draw.circle(self.ritual_texture, (200, 100, 255, 255), (16, 16), 8)
            
            # Exit texture (portal)
            self.exit_texture = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(self.exit_texture, (0, 200, 200, 150), (30, 30), 28)
            pygame.draw.circle(self.exit_texture, (100, 255, 255, 200), (30, 30), 20)
            pygame.draw.circle(self.exit_texture, (200, 255, 255, 255), (30, 30), 10)
            
            # Background texture (dark pattern)
            self.background_texture = pygame.Surface((64, 64))
            self.background_texture.fill((10, 5, 15))
            for i in range(10):
                x, y = random.randint(0, 63), random.randint(0, 63)
                pygame.draw.circle(self.background_texture, (20, 10, 30), (x, y), random.randint(1, 3))
            
            # Crawler texture (red enemy)
            self.crawler_texture = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.crawler_texture, (200, 50, 50, 200), (16, 16), 14)
            pygame.draw.circle(self.crawler_texture, (255, 100, 100, 255), (16, 16), 8)
            
            # Phantom texture (blue enemy)
            self.phantom_texture = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.phantom_texture, (50, 50, 200, 150), (16, 16), 14)
            pygame.draw.circle(self.phantom_texture, (100, 100, 255, 200), (16, 16), 8)
            
            # Warden texture (main enemy)
            self.warden_texture = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.warden_texture, (100, 0, 0, 200), (16, 16), 15)
            # Eyes
            pygame.draw.circle(self.warden_texture, (255, 255, 0, 255), (10, 10), 4)
            pygame.draw.circle(self.warden_texture, (255, 255, 0, 255), (22, 10), 4)
            pygame.draw.circle(self.warden_texture, (255, 0, 0, 255), (10, 10), 2)
            pygame.draw.circle(self.warden_texture, (255, 0, 0, 255), (22, 10), 2)
            
        except Exception as e:
            print(f"Error creating textures: {e}")
            self.memory_texture = None
            self.ritual_texture = None
            self.exit_texture = None
            self.background_texture = None
            self.crawler_texture = None
            self.phantom_texture = None
            self.warden_texture = None
        
        # Load level data
        self._load_level()
    
    def _load_level(self):
        """Load level data from file or generate procedurally."""
        # For this example, we'll generate a simple room procedurally
        if self.name == "room1":
            self._generate_nursery_room()
        elif self.name == "room2":
            self._generate_dining_room()
        else:
            self._generate_default_room()
    
    def _generate_nursery_room(self):
        """Generate a haunted orphanage room."""
        # Create a ritual circle in the center
        circle_x = SCREEN_WIDTH // 2
        circle_y = SCREEN_HEIGHT // 2
        circle_radius = 200
        
        # Add ritual items (collectables) in specific positions to avoid enemies
        ritual_positions = [
            (100, 100),
            (700, 100),
            (100, 500),
            (700, 500),
            (SCREEN_WIDTH // 2, 100)
        ]
        
        for i, pos in enumerate(ritual_positions[:self.ritual_items_required]):
            self.collectables.append({
                "type": "ritual",
                "rect": pygame.Rect(pos[0], pos[1], 32, 32),
                "collected": False,
                "glow": 0,
                "glow_dir": 1
            })
        
        # Add memory fragments in specific locations
        memory_positions = [(150, 150), (650, 150), (150, 450), (650, 450)]
        memory_types = ["orphanage", "fire", "warden", "experiments"]
        memory_texts = [
            "The orphanage was built on ancient burial grounds. The children always felt watched.",
            "The ritual must be completed before dawn, or the spirits will claim another soul.",
            "The Warden was performing dark rituals in the basement. We were the sacrifices.",
            "Only by collecting all ritual items can you banish the evil that haunts this place."
        ]
        
        for i, (pos, mem_type, text) in enumerate(zip(memory_positions, memory_types, memory_texts)):
            memory_content = {
                "text": text,
                "image": None,
                "audio": f"memory_{mem_type}.wav"
            }
            self.memory_fragments.append(
                MemoryFragment(pos[0], pos[1], mem_type, memory_content)
            )
        
        # Add different types of enemies - position them away from the player start
        # Warden - patrols away from center
        self.enemies.append(Enemy(100, 300, "warden", patrol_radius=100))
        
        # Crawlers - move slowly but are attracted to sound
        self.enemies.append(Enemy(600, 200, "crawler", patrol_radius=80))
        self.enemies.append(Enemy(600, 400, "crawler", patrol_radius=80))
        
        # Phantoms - move through walls and are faster
        self.enemies.append(Enemy(400, 500, "phantom", patrol_radius=100))
        
        # Add exit portal
        exit_width = 60
        exit_height = 60
        exit_x = circle_x - exit_width // 2
        exit_y = circle_y - exit_height // 2
        self.exit = pygame.Rect(exit_x, exit_y, exit_width, exit_height)
    
    def _generate_dining_room(self):
        """Generate a dining room layout."""
        # Similar structure to nursery but with different furniture
        # This would be implemented in a full game
        pass
    
    def _generate_default_room(self):
        """Generate a default room layout."""
        # Simple empty room
        wall_thickness = 20
        self.surfaces.append(Surface(pygame.Rect(0, 0, SCREEN_WIDTH, wall_thickness), "stone"))  # Top wall
        self.surfaces.append(Surface(pygame.Rect(0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness), "stone"))  # Bottom wall
        self.surfaces.append(Surface(pygame.Rect(0, 0, wall_thickness, SCREEN_HEIGHT), "stone"))  # Left wall
        self.surfaces.append(Surface(pygame.Rect(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT), "stone"))  # Right wall
        
        # Floor
        floor_rect = pygame.Rect(wall_thickness, wall_thickness, 
                                SCREEN_WIDTH - 2 * wall_thickness, 
                                SCREEN_HEIGHT - 2 * wall_thickness)
        self.surfaces.append(Surface(floor_rect, "wood"))
    
    def check_memory_collision(self, player_rect):
        """Check if player has collided with a memory fragment."""
        for memory in self.memory_fragments:
            if not memory.collected and memory.rect.colliderect(player_rect):
                memory.collected = True
                self.sound_manager.play_sound("memory_trigger")
                return memory
        return None
        
    def check_collectable_collision(self, player_rect):
        """Check if player has collided with a collectable item."""
        for item in self.collectables:
            if not item["collected"] and item["rect"].colliderect(player_rect):
                item["collected"] = True
                if item["type"] == "ritual":
                    self.ritual_items_collected += 1
                    self.sound_manager.play_sound("key_pickup")
                return item["type"]
        return None
        
    def check_enemy_collision(self, player_rect):
        """Check if player has collided with any enemy."""
        # Add a small grace period at the start of the game (3 seconds)
        if pygame.time.get_ticks() < 3000:
            return None
            
        for enemy in self.enemies:
            if enemy.rect.colliderect(player_rect):
                return enemy.type
        return None
        
    def check_exit_collision(self, player_rect):
        """Check if player has reached the exit with enough ritual items."""
        if self.exit and self.exit.colliderect(player_rect):
            if self.ritual_items_collected >= self.ritual_items_required:
                return True
        return False
        
    def update_enemies(self, player_pos, sound_made=False):
        """Update all enemies in the level."""
        # Add a small grace period at the start of the game (3 seconds)
        if pygame.time.get_ticks() < 3000:
            return
            
        for enemy in self.enemies:
            enemy.update(player_pos, sound_made)
    
    def render(self, screen, echo_surface, echo_intensity):
        """Render the level with echo effect."""
        # Draw textured background
        if hasattr(self, 'background_texture') and self.background_texture:
            # Tile the background texture
            bg_width, bg_height = self.background_texture.get_size()
            for x in range(0, SCREEN_WIDTH, bg_width):
                for y in range(0, SCREEN_HEIGHT, bg_height):
                    screen.blit(self.background_texture, (x, y))
        
        # Draw ritual circle in the center
        circle_x = SCREEN_WIDTH // 2
        circle_y = SCREEN_HEIGHT // 2
        circle_radius = 200
        
        # Draw outer circle
        pygame.draw.circle(screen, (50, 0, 0), (circle_x, circle_y), circle_radius, 3)
        
        # Draw inner circle
        pygame.draw.circle(screen, (80, 0, 0), (circle_x, circle_y), circle_radius - 20, 2)
        
        # Draw ritual symbols
        for i in range(5):
            angle = i * (2 * math.pi / 5)
            x = circle_x + (circle_radius - 10) * math.cos(angle)
            y = circle_y + (circle_radius - 10) * math.sin(angle)
            pygame.draw.circle(screen, (100, 0, 0), (int(x), int(y)), 10)
        
        # Render exit portal
        if self.exit:
            if self.ritual_items_collected >= self.ritual_items_required:
                # Portal is active - show bright colors
                portal_color = (0, 200, 200)
                glow_intensity = 150 + 50 * math.sin(pygame.time.get_ticks() / 200)
            else:
                # Portal is inactive - show dim colors
                portal_color = (50, 50, 100)
                glow_intensity = 50
                
            # Draw portal glow
            glow_radius = 40 + 10 * math.sin(pygame.time.get_ticks() / 300)
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (portal_color[0], portal_color[1], portal_color[2], 100), 
                              (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (self.exit.centerx - glow_radius, self.exit.centery - glow_radius))
            
            # Draw portal
            if hasattr(self, 'exit_texture') and self.exit_texture:
                screen.blit(self.exit_texture, self.exit.topleft)
            else:
                pygame.draw.circle(screen, portal_color, self.exit.center, 30)
                pygame.draw.circle(screen, (255, 255, 255), self.exit.center, 20, 2)
        
        # Render collectables (ritual items)
        for item in self.collectables:
            if not item["collected"]:
                # Update glow effect
                item["glow"] += item["glow_dir"] * 2
                if item["glow"] > 50:
                    item["glow_dir"] = -1
                elif item["glow"] < 0:
                    item["glow_dir"] = 1
                
                # Always make collectables visible
                glow_intensity = 100 + item["glow"]
                
                if item["type"] == "ritual" and hasattr(self, 'ritual_texture') and self.ritual_texture:
                    # Draw ritual item with glow effect
                    glow_size = 40 + item["glow"] // 2
                    glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                    glow_color = (200, 50, 200, 100)
                    pygame.draw.circle(glow_surf, glow_color, (glow_size//2, glow_size//2), glow_size//2)
                    screen.blit(glow_surf, 
                               (item["rect"].centerx - glow_size//2, 
                                item["rect"].centery - glow_size//2))
                    
                    # Draw the ritual item texture
                    screen.blit(self.ritual_texture, item["rect"].topleft)
                else:
                    # Fallback to simple shape
                    pygame.draw.circle(screen, (200, 50, 200), item["rect"].center, 15)
        
        # Render memory fragments
        for memory in self.memory_fragments:
            if not memory.collected:
                # Update the memory fragment
                memory.update()
                
                if hasattr(self, 'memory_texture') and self.memory_texture:
                    # Draw with texture
                    glow_radius = 15 + (memory.glow_value / 10)
                    glow_color = (200, 200, 255, 50 + memory.glow_value)
                    
                    # Create a surface for the glow
                    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                    
                    # Blit the glow surface
                    screen.blit(glow_surface, (memory.rect.centerx - glow_radius, memory.rect.centery - glow_radius))
                    
                    # Draw the memory texture
                    screen.blit(self.memory_texture, memory.rect.topleft)
                else:
                    # Use default rendering
                    memory.render(screen)
        
        # Render enemies
        for enemy in self.enemies:
            if enemy.type == "warden":
                # Warden is always slightly visible
                if hasattr(self, "warden_texture") and self.warden_texture:
                    # Add pulsing effect
                    pulse = int(20 + 10 * math.sin(pygame.time.get_ticks() / 200))
                    glow_surf = pygame.Surface((enemy.rect.width + pulse*2, enemy.rect.height + pulse*2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (100, 0, 0, 50), 
                                      (enemy.rect.width//2 + pulse, enemy.rect.height//2 + pulse), 
                                      enemy.rect.width//2 + pulse)
                    screen.blit(glow_surf, (enemy.rect.x - pulse, enemy.rect.y - pulse))
                    
                    # Draw the warden
                    screen.blit(self.warden_texture, enemy.rect.topleft)
                else:
                    # Fallback to simple shape
                    pygame.draw.circle(screen, (200, 0, 0, 150), enemy.rect.center, 16)
                    # Add glowing eyes
                    eye_radius = 3 + int(2 * math.sin(pygame.time.get_ticks() / 200))
                    pygame.draw.circle(screen, (255, 255, 0), 
                                      (int(enemy.rect.x + 10), int(enemy.rect.y + 10)), 
                                      eye_radius)
                    pygame.draw.circle(screen, (255, 255, 0), 
                                      (int(enemy.rect.x + enemy.rect.width - 10), int(enemy.rect.y + 10)), 
                                      eye_radius)
            
            elif enemy.type == "crawler":
                # Crawler is only visible during echo or when close
                if echo_intensity > 100 and hasattr(self, 'crawler_texture') and self.crawler_texture:
                    texture_copy = self.crawler_texture.copy()
                    texture_copy.set_alpha(min(255, echo_intensity))
                    screen.blit(texture_copy, enemy.rect.topleft)
                else:
                    # Simple shape when no texture
                    pygame.draw.circle(screen, (200, 50, 50, min(255, echo_intensity)), 
                                      enemy.rect.center, 15)
            
            elif enemy.type == "phantom":
                # Phantom is semi-transparent
                alpha = 100 + 50 * math.sin(pygame.time.get_ticks() / 300)
                if hasattr(self, 'phantom_texture') and self.phantom_texture:
                    texture_copy = self.phantom_texture.copy()
                    texture_copy.set_alpha(int(alpha))
                    screen.blit(texture_copy, enemy.rect.topleft)
                else:
                    # Simple shape when no texture
                    pygame.draw.circle(screen, (50, 50, 200, int(alpha)), 
                                      enemy.rect.center, 15)