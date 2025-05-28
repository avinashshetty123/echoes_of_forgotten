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
        
    def generate_content(self, difficulty=1.0):
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
                "glow_dir": 1
            })
        
        # Generate enemies based on difficulty
        num_enemies = int(1 + difficulty)
        for i in range(num_enemies):
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
                "start_y": y
            })
        
        # Generate special features
        if random.random() < 0.3:  # 30% chance for a portal
            x = world_x + random.randint(200, self.chunk_size - 200)
            y = world_y + random.randint(200, self.chunk_size - 200)
            self.portals.append({
                "rect": pygame.Rect(x, y, 60, 60),
                "destination": (random.randint(-5, 5), random.randint(-5, 5)),
                "active": True
            })
        
        self.generated = True

class InfiniteWorld:
    def __init__(self, sound_manager):
        self.chunks = {}  # Dictionary of chunks indexed by (x,y) coordinates
        self.active_chunks = []  # List of currently active chunks
        self.sound_manager = sound_manager
        self.chunk_size = 1000
        self.view_distance = 2  # How many chunks to load in each direction
        self.ritual_items_collected = 0
        self.highest_score = 0
        self.difficulty = 1.0
        
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
        
        # Enemy textures with variations
        self.enemy_textures = {
            "warden": [self._create_warden_texture(i) for i in range(3)],
            "crawler": self._create_crawler_texture(),
            "phantom": self._create_phantom_texture()
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
    
    def get_or_create_chunk(self, chunk_x, chunk_y):
        """Get an existing chunk or create a new one"""
        chunk_key = (chunk_x, chunk_y)
        if chunk_key not in self.chunks:
            self.chunks[chunk_key] = Chunk(chunk_x, chunk_y, self.chunk_size)
            self.chunks[chunk_key].generate_content(self.difficulty)
        return self.chunks[chunk_key]
    
    def update_active_chunks(self, player_pos):
        """Update which chunks are active based on player position"""
        player_chunk_x = int(player_pos[0] // self.chunk_size)
        player_chunk_y = int(player_pos[1] // self.chunk_size)
        
        self.active_chunks = []
        for x in range(player_chunk_x - self.view_distance, player_chunk_x + self.view_distance + 1):
            for y in range(player_chunk_y - self.view_distance, player_chunk_y + self.view_distance + 1):
                chunk = self.get_or_create_chunk(x, y)
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
                    return portal["destination"]
        return None
    
    def check_enemy_collision(self, player_rect):
        """Check if player has collided with any enemy"""
        # Add a small grace period at the start of the game (3 seconds)
        if pygame.time.get_ticks() < 3000:
            return None
            
        for chunk in self.active_chunks:
            for enemy in chunk.enemies:
                enemy_rect = pygame.Rect(enemy["x"], enemy["y"], 32, 32)
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
                
                # Store previous position for smooth movement
                if "prev_x" not in enemy:
                    enemy["prev_x"] = enemy["x"]
                    enemy["prev_y"] = enemy["y"]
                    enemy["variant"] = random.randint(0, 2)  # Random warden variant
                
                # Different behavior based on enemy type
                if enemy["type"] == "phantom" and distance < 150:
                    # Phantom moves directly toward player
                    speed = 1.5
                    if distance > 0:
                        target_x = enemy["x"] + dx / distance * speed
                        target_y = enemy["y"] + dy / distance * speed
                        # Smooth movement
                        enemy["x"] = enemy["x"] * 0.9 + target_x * 0.1
                        enemy["y"] = enemy["y"] * 0.9 + target_y * 0.1
                
                elif enemy["type"] == "warden" and sound_made:
                    # Warden is attracted to sound from anywhere
                    speed = 1.2
                    if distance > 0:
                        target_x = enemy["x"] + dx / distance * speed
                        target_y = enemy["y"] + dy / distance * speed
                        # Smooth movement
                        enemy["x"] = enemy["x"] * 0.8 + target_x * 0.2
                        enemy["y"] = enemy["y"] * 0.8 + target_y * 0.2
                
                elif enemy["type"] == "crawler" and sound_made and distance < 300:
                    # Crawler is attracted to sound
                    speed = 1.0
                    if distance > 0:
                        target_x = enemy["x"] + dx / distance * speed
                        target_y = enemy["y"] + dy / distance * speed
                        # Smooth movement
                        enemy["x"] = enemy["x"] * 0.85 + target_x * 0.15
                        enemy["y"] = enemy["y"] * 0.85 + target_y * 0.15
                
                else:
                    # Default patrol behavior - smoother movement
                    speed = 1.0 if enemy["type"] == "crawler" else 1.2
                    
                    # Smooth patrol movement
                    angle = pygame.time.get_ticks() / 2000 + hash(str(enemy)) % 100
                    target_x = enemy["start_x"] + math.cos(angle) * enemy["patrol_radius"]
                    target_y = enemy["start_y"] + math.sin(angle) * enemy["patrol_radius"]
                    
                    # Apply smooth movement
                    enemy["x"] = enemy["x"] * 0.95 + target_x * 0.05
                    enemy["y"] = enemy["y"] * 0.95 + target_y * 0.05
                
                # Update previous position
                enemy["prev_x"] = enemy["x"]
                enemy["prev_y"] = enemy["y"]
    
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
        
        # Draw chunk boundaries (for debugging)
        # for chunk in self.active_chunks:
        #     world_x, world_y = chunk.get_world_position()
        #     screen_x = world_x - camera_pos[0]
        #     screen_y = world_y - camera_pos[1]
        #     pygame.draw.rect(screen, (50, 50, 50), 
        #                      (screen_x, screen_y, chunk.chunk_size, chunk.chunk_size), 1)
        
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
                        # Draw ritual item with glow effect
                        glow_size = 40 + item["glow"] // 2
                        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                        glow_color = (200, 50, 200, 100)
                        pygame.draw.circle(glow_surf, glow_color, (glow_size//2, glow_size//2), glow_size//2)
                        screen.blit(glow_surf, 
                                   (screen_x + 16 - glow_size//2, 
                                    screen_y + 16 - glow_size//2))
                        
                        # Draw the ritual item texture
                        if hasattr(self, 'ritual_texture') and self.ritual_texture:
                            screen.blit(self.ritual_texture, (screen_x, screen_y))
                        else:
                            pygame.draw.circle(screen, (200, 50, 200), (screen_x + 16, screen_y + 16), 15)
        
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
                    pygame.draw.circle(glow_surf, (*portal_color, 100), (glow_radius, glow_radius), glow_radius)
                    screen.blit(glow_surf, (screen_x + 30 - glow_radius, screen_y + 30 - glow_radius))
                    
                    # Draw portal
                    if hasattr(self, 'portal_texture') and self.portal_texture:
                        screen.blit(self.portal_texture, (screen_x, screen_y))
                    else:
                        pygame.draw.circle(screen, portal_color, (screen_x + 30, screen_y + 30), 30)
                        pygame.draw.circle(screen, (255, 255, 255), (screen_x + 30, screen_y + 30), 20, 2)
                # Check for exit door and draw indicator if off-screen
        exit_door = None
        exit_door_pos = None

        # Find exit door
        for chunk in self.active_chunks:
            for portal in chunk.portals:
                if portal.get("is_exit", False):
                    exit_door = portal
                    exit_door_pos = (portal["rect"].centerx, portal["rect"].centery)
                    break
            if exit_door:
                break

        # If exit door exists and is created, show indicator when off-screen
        if exit_door and self.exit_door_created:
            door_x = exit_door_pos[0] - camera_pos[0]
            door_y = exit_door_pos[1] - camera_pos[1]
            
            # If door is off-screen, show direction indicator
            if door_x < 0 or door_x > SCREEN_WIDTH or door_y < 0 or door_y > SCREEN_HEIGHT:
                # Calculate direction to exit door
                dx = exit_door_pos[0] - (camera_pos[0] + SCREEN_WIDTH // 2)
                dy = exit_door_pos[1] - (camera_pos[1] + SCREEN_HEIGHT // 2)
                angle = math.atan2(dy, dx)
                
                # Calculate position on screen edge
                edge_x = SCREEN_WIDTH // 2 + math.cos(angle) * (SCREEN_WIDTH // 2 - 30)
                edge_y = SCREEN_HEIGHT // 2 + math.sin(angle) * (SCREEN_HEIGHT // 2 - 30)
                
                # Clamp to screen edges
                edge_x = max(30, min(SCREEN_WIDTH - 30, edge_x))
                edge_y = max(30, min(SCREEN_HEIGHT - 30, edge_y))
                
                # Draw arrow pointing to exit
                arrow_color = (0, 255, 0) if self.ritual_items_collected >= self.ritual_items_required else (255, 255, 0)
                arrow_size = 15
                
                # Draw arrow head
                points = [
                    (edge_x + math.cos(angle) * arrow_size, edge_y + math.sin(angle) * arrow_size),
                    (edge_x + math.cos(angle + 2.5) * arrow_size, edge_y + math.sin(angle + 2.5) * arrow_size),
                    (edge_x + math.cos(angle - 2.5) * arrow_size, edge_y + math.sin(angle - 2.5) * arrow_size)
                ]
                pygame.draw.polygon(screen, arrow_color, [(int(x), int(y)) for x, y in points])
                
                # Draw "EXIT" text
                small_font = pygame.font.Font(None, 20)
                exit_text = small_font.render("EXIT", True, arrow_color)
                screen.blit(exit_text, (int(edge_x - exit_text.get_width() // 2), int(edge_y - 25)))
                
                # Draw ritual count
                count_text = small_font.render(f"{self.ritual_items_collected}/{self.ritual_items_required}", 
                                            True, arrow_color)
                screen.blit(count_text, (int(edge_x - count_text.get_width() // 2), int(edge_y + 15)))

        # Draw enemies
        for chunk in self.active_chunks:
            for enemy in chunk.enemies:
                # Calculate screen position
                screen_x = enemy["x"] - camera_pos[0]
                screen_y = enemy["y"] - camera_pos[1]
                
                # Only draw if on screen
                if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                    enemy_type = enemy["type"]
                    
                    if enemy_type == "warden":
                        # Warden is always visible
                        if enemy_type in self.enemy_textures:
                            # Add pulsing effect
                            pulse = int(20 + 10 * math.sin(pygame.time.get_ticks() / 200))
                            glow_surf = pygame.Surface((32 + pulse*2, 32 + pulse*2), pygame.SRCALPHA)
                            pygame.draw.circle(glow_surf, (100, 0, 0, 50), 
                                              (16 + pulse, 16 + pulse), 
                                              16 + pulse)
                            screen.blit(glow_surf, (screen_x - pulse, screen_y - pulse))
                            
                            # Draw the warden
                            screen.blit(self.enemy_textures[enemy_type], (screen_x, screen_y))
                        else:
                            # Fallback
                            pygame.draw.circle(screen, (200, 0, 0, 150), (screen_x + 16, screen_y + 16), 16)
                    
                    elif enemy_type == "crawler":
                        # Crawler is only visible during echo or when close
                        if echo_intensity > 100 and enemy_type in self.enemy_textures:
                            texture_copy = self.enemy_textures[enemy_type].copy()
                            texture_copy.set_alpha(min(255, echo_intensity))
                            screen.blit(texture_copy, (screen_x, screen_y))
                        else:
                            # Simple shape when no texture or low echo
                            pygame.draw.circle(screen, (200, 50, 50, min(255, echo_intensity)), 
                                              (screen_x + 16, screen_y + 16), 15)
                    
                    elif enemy_type == "phantom":
                        # Phantom is semi-transparent
                        alpha = 100 + 50 * math.sin(pygame.time.get_ticks() / 300)
                        if enemy_type in self.enemy_textures:
                            texture_copy = self.enemy_textures[enemy_type].copy()
                            texture_copy.set_alpha(int(alpha))
                            screen.blit(texture_copy, (screen_x, screen_y))
                        else:
                            # Simple shape
                            pygame.draw.circle(screen, (50, 50, 200, int(alpha)), 
                                              (screen_x + 16, screen_y + 16), 15)