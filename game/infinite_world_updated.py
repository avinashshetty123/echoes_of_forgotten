import pygame
import random
import math
import os
from .constants import *

class Chunk:
    def __init__(self, x, y, chunk_size=1000):
        self.x = x
        self.y = y
        self.chunk_size = chunk_size
        self.collectables = []
        self.enemies = []
        self.obstacles = []
        self.memory_fragments = []
        self.portals = []
        self.generated = False
        
    def get_world_position(self):
        return (self.x * self.chunk_size, self.y * self.chunk_size)
        
    def generate_content(self, difficulty=1.0, is_exit_chunk=False):
        """Generate random content for this chunk based on difficulty"""
        if self.generated:
            return
            
        world_x, world_y = self.get_world_position()
        
        # Generate collectables (ritual items)
        num_collectables = random.randint(1, 3)
        for i in range(num_collectables):
            x = world_x + random.randint(100, self.chunk_size - 100)
            y = world_y + random.randint(100, self.chunk_size - 100)
            self.collectables.append({
                "type": "ritual",
                "rect": pygame.Rect(x, y, 32, 32),
                "collected": False,
                "glow": random.randint(0, 50),
                "glow_dir": 1,
                "variant": random.randint(0, 2)  # Random variant for different textures
            })
        
        # Generate enemies based on difficulty
        num_enemies = int(1 + difficulty)
        for i in range(num_enemies):
            # Add turret enemies with 20% chance
            if random.random() < 0.2:
                enemy_type = "turret"
            else:
                enemy_type = random.choice(["crawler", "phantom", "warden"])
                
            x = world_x + random.randint(100, self.chunk_size - 100)
            y = world_y + random.randint(100, self.chunk_size - 100)
            patrol_radius = random.randint(80, 150)
            
            self.enemies.append({
                "type": enemy_type,
                "x": x,
                "y": y,
                "patrol_radius": patrol_radius,
                "start_x": x,
                "start_y": y,
                "variant": random.randint(0, 2),  # Random variant for warden
                "prev_x": x,
                "prev_y": y,
                "fire_cooldown": 120,  # For turrets
                "cooldown_timer": 0     # For turrets
            })
        
        # Generate exit door if this is the exit chunk
        if is_exit_chunk:
            door_x = world_x + self.chunk_size // 2
            door_y = world_y + self.chunk_size // 2
            self.portals.append({
                "rect": pygame.Rect(door_x, door_y, 80, 80),
                "destination": None,  # None means it's an exit door
                "active": True,
                "is_exit": True
            })
        # Generate special features
        elif random.random() < 0.3:  # 30% chance for a portal
            x = world_x + random.randint(200, self.chunk_size - 200)
            y = world_y + random.randint(200, self.chunk_size - 200)
            self.portals.append({
                "rect": pygame.Rect(x, y, 60, 60),
                "destination": (random.randint(-5, 5), random.randint(-5, 5)),
                "active": True,
                "is_exit": False
            })
        
        self.generated = True

class InfiniteWorld:
    def __init__(self, sound_manager, warden_speed=1.5, ritual_items_required=5, enemy_count=4):
        self.chunks = {}  # Dictionary of chunks indexed by (x,y) coordinates
        self.active_chunks = []  # List of currently active chunks
        self.sound_manager = sound_manager
        self.chunk_size = 1000
        self.view_distance = 2  # How many chunks to load in each direction
        self.ritual_items_collected = 0
        self.ritual_items_required = ritual_items_required
        self.enemy_count = enemy_count
        self.highest_score = 0
        self.difficulty = 1.0
        self.warden_speed = warden_speed  # Configurable warden speed
        self.exit_door_created = False
        
        # Create textures
        self._create_textures()
        
        # Create the starting chunk
        self.get_or_create_chunk(0, 0)
    
    def _create_textures(self):
        """Create game textures programmatically"""
        # Create different ritual item textures
        self.ritual_textures = []
        
        # Ritual item 1 - Crystal
        crystal = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Base crystal shape
        points = [(16, 4), (24, 12), (24, 20), (16, 28), (8, 20), (8, 12)]
        pygame.draw.polygon(crystal, (180, 50, 220, 220), points)
        # Inner glow
        pygame.draw.polygon(crystal, (220, 150, 255, 180), 
                          [(16, 8), (20, 12), (20, 20), (16, 24), (12, 20), (12, 12)])
        self.ritual_textures.append(crystal)
        
        # Ritual item 2 - Skull
        skull = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Skull shape
        pygame.draw.ellipse(skull, (220, 220, 220, 220), (8, 8, 16, 16))
        # Eye sockets
        pygame.draw.circle(skull, (10, 5, 15, 255), (12, 14), 3)
        pygame.draw.circle(skull, (10, 5, 15, 255), (20, 14), 3)
        # Jaw
        pygame.draw.ellipse(skull, (200, 200, 200, 220), (10, 18, 12, 8))
        self.ritual_textures.append(skull)
        
        # Ritual item 3 - Candle
        candle = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Candle base
        pygame.draw.rect(candle, (220, 220, 200, 220), (12, 16, 8, 12))
        # Flame
        pygame.draw.polygon(candle, (255, 200, 50, 220), 
                          [(16, 6), (20, 12), (16, 10), (12, 12)])
        # Glow
        pygame.draw.circle(candle, (255, 200, 50, 100), (16, 10), 8)
        self.ritual_textures.append(candle)
        
        # Portal texture
        self.portal_texture = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(self.portal_texture, (0, 200, 200, 150), (30, 30), 28)
        pygame.draw.circle(self.portal_texture, (100, 255, 255, 200), (30, 30), 20)
        pygame.draw.circle(self.portal_texture, (200, 255, 255, 255), (30, 30), 10)
        
        # Exit door texture (larger and more distinct)
        self.exit_door_texture = pygame.Surface((80, 80), pygame.SRCALPHA)
        # Door frame
        pygame.draw.rect(self.exit_door_texture, (150, 100, 50), (10, 0, 60, 80))
        # Door
        pygame.draw.rect(self.exit_door_texture, (100, 50, 0), (15, 5, 50, 70))
        # Doorknob
        pygame.draw.circle(self.exit_door_texture, (200, 200, 0), (55, 40), 5)
        # Glow when active
        self.exit_door_active_glow = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(self.exit_door_active_glow, (0, 255, 0, 100), (50, 50), 45)
        
        # Enemy textures with variations
        self.enemy_textures = {
            "warden": [self._create_warden_texture(i) for i in range(3)],
            "crawler": self._create_crawler_texture(),
            "phantom": self._create_phantom_texture(),
            "turret": self._create_turret_texture()
        }
        
        # Background texture
        self.background_texture = pygame.Surface((64, 64))
        self.background_texture.fill((10, 5, 15))
        for i in range(10):
            x, y = random.randint(0, 63), random.randint(0, 63)
            pygame.draw.circle(self.background_texture, (20, 10, 30), (x, y), random.randint(1, 3))
    
    def _create_warden_texture(self, variant=0):
        texture = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        if variant == 0:
            # Hooded figure
            # Body
            pygame.draw.rect(texture, (80, 0, 0, 220), (8, 12, 16, 16))
            # Hood
            pygame.draw.polygon(texture, (100, 0, 0, 220), 
                              [(8, 12), (16, 4), (24, 12), (16, 14)])
            # Eyes
            pygame.draw.circle(texture, (255, 255, 0, 255), (12, 10), 3)
            pygame.draw.circle(texture, (255, 255, 0, 255), (20, 10), 3)
            pygame.draw.circle(texture, (255, 0, 0, 255), (12, 10), 1)
            pygame.draw.circle(texture, (255, 0, 0, 255), (20, 10), 1)
        elif variant == 1:
            # Ghostly figure
            # Body
            pygame.draw.ellipse(texture, (100, 0, 0, 180), (8, 8, 16, 20))
            # Bottom wispy part
            pygame.draw.polygon(texture, (100, 0, 0, 150), 
                              [(8, 20), (12, 28), (16, 24), (20, 28), (24, 20)])
            # Eyes
            pygame.draw.circle(texture, (200, 200, 255, 255), (12, 14), 3)
            pygame.draw.circle(texture, (200, 200, 255, 255), (20, 14), 3)
        else:
            # Demonic figure
            # Body
            pygame.draw.rect(texture, (120, 0, 0, 220), (8, 12, 16, 16))
            # Horns
            pygame.draw.polygon(texture, (80, 0, 0, 220), 
                              [(8, 12), (4, 4), (12, 8)])
            pygame.draw.polygon(texture, (80, 0, 0, 220), 
                              [(24, 12), (28, 4), (20, 8)])
            # Eyes
            pygame.draw.circle(texture, (255, 0, 0, 255), (12, 16), 3)
            pygame.draw.circle(texture, (255, 0, 0, 255), (20, 16), 3)
            
        return texture
    
    def _create_crawler_texture(self):
        texture = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(texture, (200, 50, 50, 200), (16, 16), 14)
        pygame.draw.circle(texture, (255, 100, 100, 255), (16, 16), 8)
        return texture
    
    def _create_phantom_texture(self):
        texture = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(texture, (50, 50, 200, 150), (16, 16), 14)
        pygame.draw.circle(texture, (100, 100, 255, 200), (16, 16), 8)
        return texture
        
    def _create_turret_texture(self):
        texture = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(texture, (100, 100, 100, 220), (8, 16, 16, 16))
        pygame.draw.circle(texture, (150, 150, 150, 220), (16, 16), 10)
        pygame.draw.rect(texture, (80, 80, 80, 220), (16, 8, 4, 8))
        pygame.draw.circle(texture, (255, 0, 0, 255), (16, 16), 3)
        return texture
    
    
    def get_or_create_chunk(self, chunk_x, chunk_y, is_exit=False):
        """Get an existing chunk or create a new one"""
        chunk_key = (chunk_x, chunk_y)
        if chunk_key not in self.chunks:
            self.chunks[chunk_key] = Chunk(chunk_x, chunk_y, self.chunk_size)
            self.chunks[chunk_key].generate_content(self.difficulty, is_exit)
        return self.chunks[chunk_key]
    
    def update_active_chunks(self, player_pos):
        """Update which chunks are active based on player position"""
        player_chunk_x = int(player_pos[0] // self.chunk_size)
        player_chunk_y = int(player_pos[1] // self.chunk_size)
        
        self.active_chunks = []
        for x in range(player_chunk_x - self.view_distance, player_chunk_x + self.view_distance + 1):
            for y in range(player_chunk_y - self.view_distance, player_chunk_y + self.view_distance + 1):
                # Check if this should be the exit chunk
                is_exit = False
                if not self.exit_door_created and self.ritual_items_collected >= self.ritual_items_required // 2:
                    # Create exit door when player has collected half the required items
                    # Place it in a chunk that's not the current one but within view distance
                    if (x != player_chunk_x or y != player_chunk_y) and \
                       abs(x - player_chunk_x) <= 1 and abs(y - player_chunk_y) <= 1:
                        is_exit = True
                        self.exit_door_created = True
                
                chunk = self.get_or_create_chunk(x, y, is_exit)
                self.active_chunks.append(chunk)
        
        # Increase difficulty over time
        self.difficulty = min(3.0, 1.0 + self.ritual_items_collected / 20)
    
    def check_collectable_collision(self, player_rect):
        """Check if player has collided with any collectable"""
        for chunk in self.active_chunks:
            for item in chunk.collectables:
                if not item["collected"] and item["rect"].colliderect(player_rect):
                    item["collected"] = True
                    if item["type"] == "ritual":
                        self.ritual_items_collected += 1
                        self.sound_manager.play_sound("key_pickup")
                    return item["type"]
        return None
    
    def check_portal_collision(self, player_rect):
        """Check if player has entered a portal"""
        for chunk in self.active_chunks:
            for portal in chunk.portals:
                if portal["active"] and portal["rect"].colliderect(player_rect):
                    # Check if it's an exit door
                    if portal.get("is_exit", False):
                        # Only allow exit if enough ritual items collected
                        if self.ritual_items_collected >= self.ritual_items_required:
                            return "EXIT"
                    else:
                        # Regular portal
                        return portal["destination"]
        return None
    
    def check_enemy_collision(self, player_rect):
        """Check if player has collided with any enemy"""
        # Add a small grace period at the start of the game (3 seconds)
        if pygame.time.get_ticks() < 3000:
            return None
            
        for chunk in self.active_chunks:
            for enemy in chunk.enemies:
                # Use a slightly larger collision area for enemies
                enemy_rect = pygame.Rect(enemy["x"] - 5, enemy["y"] - 5, 42, 42)
                if enemy_rect.colliderect(player_rect):
                    return enemy["type"]
        return None
    
    def update_enemies(self, player_pos, sound_made=False):
        """Update all enemies in active chunks"""
        # Add a small grace period at the start of the game (3 seconds)
        if pygame.time.get_ticks() < 3000:
            return
            
        for chunk in self.active_chunks:
            for enemy in chunk.enemies:
                # Calculate distance to player
                dx = player_pos[0] - enemy["x"]
                dy = player_pos[1] - enemy["y"]
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Initialize enemy properties if needed
                if "detection_range" not in enemy:
                    enemy["variant"] = random.randint(0, 2)  # Random warden variant
                    
                    # Set detection range based on enemy type
                    if enemy["type"] == "warden":
                        enemy["detection_range"] = 200
                        enemy["speed"] = self.warden_speed  # Use configurable speed
                    elif enemy["type"] == "phantom":
                        enemy["detection_range"] = 150
                        enemy["speed"] = 1.2
                    elif enemy["type"] == "turret":
                        enemy["detection_range"] = 250
                        enemy["speed"] = 0
                        enemy["fire_cooldown"] = 120
                        enemy["cooldown_timer"] = 0
                    else:  # crawler
                        enemy["detection_range"] = 100
                        enemy["speed"] = 0.8
                
                # Simple enemy behavior
                if enemy["type"] == "warden":
                    # Warden follows player directly when close or when sound is made
                    if distance < enemy["detection_range"] or sound_made:
                        # Store player position
                        enemy["target_x"] = player_pos[0]
                        enemy["target_y"] = player_pos[1]
                        enemy["heard_sound"] = True
                    
                    # Move toward player or last heard position
                    if enemy.get("heard_sound", False):
                        target_x = enemy.get("target_x", enemy["x"])
                        target_y = enemy.get("target_y", enemy["y"])
                        
                        # Calculate distance to target
                        tx = target_x - enemy["x"]
                        ty = target_y - enemy["y"]
                        target_dist = math.sqrt(tx*tx + ty*ty)
                        
                        # Move toward target
                        if target_dist > 5:  # Stop when very close to target
                            speed = enemy["speed"]
                            enemy["x"] += tx / target_dist * speed
                            enemy["y"] += ty / target_dist * speed
                        
                        # Update target to player's current position if close enough
                        if distance < enemy["detection_range"]:
                            enemy["target_x"] = player_pos[0]
                            enemy["target_y"] = player_pos[1]
                
                elif enemy["type"] == "phantom":
                    # Phantom follows player if within range
                    if distance < enemy["detection_range"]:
                        if distance > 5:
                            speed = enemy["speed"]
                            enemy["x"] += dx / distance * speed
                            enemy["y"] += dy / distance * speed
                    else:
                        # Simple patrol in a small area
                        angle = pygame.time.get_ticks() / 5000
                        enemy["x"] = enemy["start_x"] + math.cos(angle) * 50
                        enemy["y"] = enemy["start_y"] + math.sin(angle) * 50
                
                elif enemy["type"] == "turret":
                    # Turret behavior - stationary but fires at player
                    if distance < enemy["detection_range"]:
                        # Update cooldown timer
                        if enemy["cooldown_timer"] > 0:
                            enemy["cooldown_timer"] -= 1
                        
                        # Fire projectile if cooldown is ready
                        if enemy["cooldown_timer"] == 0:
                            # Signal that this enemy has fired a projectile
                            enemy["has_fired"] = True
                            enemy["target_x"] = player_pos[0]
                            enemy["target_y"] = player_pos[1]
                            enemy["cooldown_timer"] = enemy["fire_cooldown"]
                    
                elif enemy["type"] == "crawler":
                    # Crawler is attracted to sound
                    if sound_made and distance < 300:
                        if distance > 5:
                            speed = enemy["speed"]
                            enemy["x"] += dx / distance * speed
                            enemy["y"] += dy / distance * speed
                    else:
                        # Simple patrol in a small area
                        angle = pygame.time.get_ticks() / 4000 + hash(str(enemy)) % 100
                        enemy["x"] = enemy["start_x"] + math.cos(angle) * 30
                        enemy["y"] = enemy["start_y"] + math.sin(angle) * 30
    
    def render(self, screen, camera_pos, echo_intensity=0):
        """Render the visible world"""
        # Draw background
        if hasattr(self, 'background_texture') and self.background_texture:
            # Tile the background texture
            bg_width, bg_height = self.background_texture.get_size()
            start_x = int(camera_pos[0] / bg_width) * bg_width - camera_pos[0]
            start_y = int(camera_pos[1] / bg_height) * bg_height - camera_pos[1]
            
            for x in range(start_x, SCREEN_WIDTH, bg_width):
                for y in range(start_y, SCREEN_HEIGHT, bg_height):
                    screen.blit(self.background_texture, (x, y))
        
        # Draw collectables
        for chunk in self.active_chunks:
            for item in chunk.collectables:
                if not item["collected"]:
                    # Update glow effect
                    item["glow"] += item["glow_dir"] * 2
                    if item["glow"] > 50:
                        item["glow_dir"] = -1
                    elif item["glow"] < 0:
                        item["glow_dir"] = 1
                    
                    # Calculate screen position
                    screen_x = item["rect"].x - camera_pos[0]
                    screen_y = item["rect"].y - camera_pos[1]
                    
                    # Only draw if on screen
                    if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                        # Determine visibility based on echo intensity and distance
                        distance_to_center = math.sqrt((SCREEN_WIDTH/2 - screen_x)**2 + (SCREEN_HEIGHT/2 - screen_y)**2)
                        visibility = echo_intensity - distance_to_center / 5
                        
                        if visibility > 20:  # Only show if somewhat visible
                            # Draw ritual item with glow effect
                            glow_size = 40 + item["glow"] // 2
                            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                            glow_color = (200, 50, 200, min(100, int(visibility)))
                            pygame.draw.circle(glow_surf, glow_color, (glow_size//2, glow_size//2), glow_size//2)
                            screen.blit(glow_surf, 
                                       (screen_x + 16 - glow_size//2, 
                                        screen_y + 16 - glow_size//2))
                            
                            # Draw the ritual item texture based on variant
                            variant = item.get("variant", 0) % len(self.ritual_textures)
                            if hasattr(self, 'ritual_textures') and len(self.ritual_textures) > variant:
                                texture_copy = self.ritual_textures[variant].copy()
                                texture_copy.set_alpha(min(255, int(visibility) + 50))
                                screen.blit(texture_copy, (screen_x, screen_y))
                            else:
                                # Fallback
                                pygame.draw.circle(screen, (200, 50, 200, min(255, int(visibility))), 
                                                  (screen_x + 16, screen_y + 16), 15)
        
        # Draw portals
        for chunk in self.active_chunks:
            for portal in chunk.portals:
                # Calculate screen position
                screen_x = portal["rect"].x - camera_pos[0]
                screen_y = portal["rect"].y - camera_pos[1]
                
                # Only draw if on screen
                if -60 < screen_x < SCREEN_WIDTH + 60 and -60 < screen_y < SCREEN_HEIGHT + 60:
                    # Portal animation
                    glow_radius = 40 + 10 * math.sin(pygame.time.get_ticks() / 300)
                    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    portal_color = (0, 200, 200)
                    pygame.draw.circle(glow_surf, (portal_color[0], portal_color[1], portal_color[2], 100), 
                                      (glow_radius, glow_radius), glow_radius)
                    screen.blit(glow_surf, (screen_x + 30 - glow_radius, screen_y + 30 - glow_radius))
                    
                    # Draw portal
                    if hasattr(self, 'portal_texture') and self.portal_texture:
                        screen.blit(self.portal_texture, (screen_x, screen_y))
                    else:
                        pygame.draw.circle(screen, portal_color, (screen_x + 30, screen_y + 30), 30)
                        pygame.draw.circle(screen, (255, 255, 255), (screen_x + 30, screen_y + 30), 20, 2)
        
        # Draw enemies
        for chunk in self.active_chunks:
            for enemy in chunk.enemies:
                # Calculate screen position
                screen_x = enemy["x"] - camera_pos[0]
                screen_y = enemy["y"] - camera_pos[1]
                
                # Only draw if on screen
                if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                    enemy_type = enemy["type"]
                    variant = enemy.get("variant", 0)
                    
                    if enemy_type == "warden":
                        # Warden is always visible
                        if enemy_type in self.enemy_textures and len(self.enemy_textures[enemy_type]) > variant:
                            # Draw detection range circle
                            detection_range = enemy.get("detection_range", 200)
                            range_surf = pygame.Surface((detection_range*2, detection_range*2), pygame.SRCALPHA)
                            pygame.draw.circle(range_surf, (200, 0, 0, 30), 
                                             (detection_range, detection_range), detection_range)
                            pygame.draw.circle(range_surf, (200, 0, 0, 50), 
                                             (detection_range, detection_range), detection_range, 2)
                            screen.blit(range_surf, (screen_x + 16 - detection_range, screen_y + 16 - detection_range))
                            
                            # Draw the warden with variant
                            screen.blit(self.enemy_textures[enemy_type][variant], (screen_x, screen_y))
                        else:
                            # Fallback
                            pygame.draw.circle(screen, (200, 0, 0, 150), (screen_x + 16, screen_y + 16), 16)
                            # Draw detection range
                            detection_range = enemy.get("detection_range", 200)
                            pygame.draw.circle(screen, (200, 0, 0, 30), (screen_x + 16, screen_y + 16), 
                                             detection_range, 2)
                    
                    elif enemy_type == "crawler":
                        # Crawler is only visible during echo or when close
                        distance_visibility = max(0, 255 - int(math.sqrt((SCREEN_WIDTH/2 - screen_x)**2 + 
                                                                        (SCREEN_HEIGHT/2 - screen_y)**2) / 2))
                        visibility = max(echo_intensity, distance_visibility)
                        
                        if visibility > 50 and enemy_type in self.enemy_textures:
                            texture_copy = self.enemy_textures[enemy_type].copy()
                            texture_copy.set_alpha(min(255, visibility))
                            screen.blit(texture_copy, (screen_x, screen_y))
                        elif visibility > 20:
                            # Simple shape when no texture or low echo
                            pygame.draw.circle(screen, (200, 50, 50, min(255, visibility)), 
                                              (screen_x + 16, screen_y + 16), 15)
                    
                    elif enemy_type == "turret":
                        # Turret is always visible
                        if enemy_type in self.enemy_textures:
                            # Draw detection range
                            detection_range = enemy.get("detection_range", 250)
                            range_surf = pygame.Surface((detection_range*2, detection_range*2), pygame.SRCALPHA)
                            pygame.draw.circle(range_surf, (255, 0, 0, 20), 
                                             (detection_range, detection_range), detection_range)
                            pygame.draw.circle(range_surf, (255, 0, 0, 40), 
                                             (detection_range, detection_range), detection_range, 2)
                            screen.blit(range_surf, (screen_x + 16 - detection_range, screen_y + 16 - detection_range))
                            
                            # Draw turret
                            screen.blit(self.enemy_textures[enemy_type], (screen_x, screen_y))
                        else:
                            # Fallback
                            pygame.draw.rect(screen, (150, 150, 150), (screen_x, screen_y, 32, 32))
                            pygame.draw.circle(screen, (255, 0, 0), (screen_x + 16, screen_y + 16), 5)
                    
                    elif enemy_type == "phantom":
                        # Phantom is semi-transparent
                        alpha = 100 + 50 * math.sin(pygame.time.get_ticks() / 300)
                        if enemy_type in self.enemy_textures:
                            # Draw detection range
                            detection_range = enemy.get("detection_range", 150)
                            range_surf = pygame.Surface((detection_range*2, detection_range*2), pygame.SRCALPHA)
                            pygame.draw.circle(range_surf, (50, 50, 200, 20), 
                                             (detection_range, detection_range), detection_range)
                            screen.blit(range_surf, (screen_x + 16 - detection_range, screen_y + 16 - detection_range))
                            
                            # Draw phantom
                            texture_copy = self.enemy_textures[enemy_type].copy()
                            texture_copy.set_alpha(int(alpha))
                            screen.blit(texture_copy, (screen_x, screen_y))
                        else:
                            # Simple shape
                            pygame.draw.circle(screen, (50, 50, 200, int(alpha)), 
                                              (screen_x + 16, screen_y + 16), 15)
