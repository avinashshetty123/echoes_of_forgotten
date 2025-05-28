import pygame
import sys
import os
import math
import random
from .player_animated import AnimatedPlayer
from .infinite_world_updated import InfiniteWorld
from .sound_manager import SoundManager
from .memory_fragment import MemoryFragmentManager
from .constants import *

class GameEngine:
    def __init__(self, warden_speed=1.5, level_data=None):
        """Initialize the game engine and all game components."""
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dark Ritual")
        
        # Set up the clock
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.game_state = "PLAYING"  # PLAYING, PAUSED, MEMORY, GAME_OVER, VICTORY
        
        # Level data
        self.level_data = level_data or {
            "name": "Default",
            "ritual_items_required": 5,
            "enemy_count": 4,
            "warden_speed_modifier": 1.0,
            "description": "Find ritual items to unlock the door."
        }
        
        # Initialize game components
        self.sound_manager = SoundManager()
        self.player = AnimatedPlayer(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.sound_manager)
        self.world = InfiniteWorld(self.sound_manager, warden_speed, 
                                  self.level_data["ritual_items_required"],
                                  self.level_data["enemy_count"])
        self.memory_manager = MemoryFragmentManager()
        
        # Initialize turret enemies and projectiles
        self.turrets = []
        self.projectiles = []
        
        # Create door indicator
        from .door_indicator import DoorIndicator
        self.door_indicator = DoorIndicator(self.world)
        
        # Camera position (centered on player)
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
        
        # Echo effect surface
        self.echo_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.echo_timer = 0
        self.echo_active = False
        
        # Load fonts
        try:
            fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    "game", "assets", "fonts")
            self.font = pygame.font.Font(None, 24)  # Smaller font
            self.title_font = pygame.font.Font(None, 36)
        except:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 36)
            
        # UI elements
        self.show_tutorial = True
        self.tutorial_timer = 0
        self.show_controls = False
    
    def handle_events(self):
        """Process all game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Player controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.game_state == "PLAYING":
                    # Emit sound/echolocation
                    if self.player.emit_sound():
                        self.echo_active = True
                        self.echo_timer = 0
                        # Play sound at higher volume
                        self.sound_manager.play_sound("echo", 0.8)
                elif self.game_state == "MEMORY":
                    # Any key press in memory state returns to playing
                    self.game_state = "PLAYING"
                elif event.key == pygame.K_SPACE and self.game_state == "VICTORY":
                    # Signal that we need to restart the game
                    self.game_state = "RESTART"
                elif event.key == pygame.K_r and self.game_state == "GAME_OVER":
                    # Signal that we need to restart the game
                    self.game_state = "RESTART"
    
    def update(self):
        """Update game state."""
        if self.game_state == "PLAYING":
            # Store previous position for collision handling
            prev_x, prev_y = self.player.x, self.player.y
            
            # Update player
            self.player.update()
            
            # Update camera to follow player
            self.camera_x = self.player.x - SCREEN_WIDTH // 2
            self.camera_y = self.player.y - SCREEN_HEIGHT // 2
            
            # Update active chunks based on player position
            self.world.update_active_chunks((self.player.x, self.player.y))
            
            # Track if player made a sound this frame
            sound_made = False
            if self.echo_active and self.echo_timer == 0:
                sound_made = True
            
            # Update all enemies
            self.world.update_enemies((self.player.x, self.player.y), sound_made)
            
            # Check for turret projectiles
            for chunk in self.world.active_chunks:
                for enemy in chunk.enemies:
                    if enemy["type"] == "turret" and enemy.get("has_fired", False):
                        # Create new projectile
                        from .projectile import Projectile
                        new_proj = Projectile(
                            enemy["x"] + 16, 
                            enemy["y"] + 16, 
                            enemy.get("target_x", self.player.x), 
                            enemy.get("target_y", self.player.y)
                        )
                        self.projectiles.append(new_proj)
                        enemy["has_fired"] = False
            
            # Update projectiles
            for proj in self.projectiles[:]:
                if not proj.update():
                    self.projectiles.remove(proj)
                elif proj.check_collision(self.player.rect):
                    # Player hit by projectile
                    if not self.player.take_damage(proj.damage):
                        self.game_state = "GAME_OVER"
                    else:
                        self.sound_manager.play_sound("obstacle_hit", 0.5)
                    self.projectiles.remove(proj)
            
            # Check for collisions with collectables
            collectable = self.world.check_collectable_collision(self.player.rect)
            if collectable == "ritual":
                self.player.score += 100
                # Play special sound
                self.sound_manager.play_sound("key_pickup")
                
                # Every 5 ritual items, increase health
                if self.world.ritual_items_collected % 5 == 0:
                    self.player.heal(20)
                    self.sound_manager.play_sound("victory")
            
            # Check for portal collision
            portal_dest = self.world.check_portal_collision(self.player.rect)
            if portal_dest:
                if portal_dest == "EXIT":
                    # Player has reached the exit with enough ritual items
                    self.game_state = "VICTORY"
                    self.player.score += 1000
                    self.sound_manager.play_sound("victory")
                else:
                    # Teleport player to a new location
                    self.player.x += portal_dest[0] * 1000
                    self.player.y += portal_dest[1] * 1000
                    self.player.rect.x = self.player.x
                    self.player.rect.y = self.player.y
                    self.sound_manager.play_sound("door_creak")
            
            # Update echo effect
            if self.echo_active:
                self.echo_timer += 1
                if self.echo_timer > ECHO_DURATION:
                    self.echo_active = False
            
            # Check for enemy collision
            enemy_hit = self.world.check_enemy_collision(self.player.rect)
            if enemy_hit:
                # Different enemies have different effects
                if enemy_hit == "warden":
                    # Warden does heavy damage
                    if not self.player.take_damage(40):
                        self.game_state = "GAME_OVER"
                    else:
                        # Push player back
                        self.player.x, self.player.y = prev_x - 50, prev_y - 50
                        self.player.rect.x, self.player.rect.y = self.player.x, self.player.y
                        self.sound_manager.play_sound("warden_groan", 0.8)
                elif enemy_hit == "crawler":
                    # Crawler damages player
                    if not self.player.take_damage(20):
                        self.game_state = "GAME_OVER"
                    else:
                        # Push player back
                        self.player.x, self.player.y = prev_x - 20, prev_y - 20
                        self.player.rect.x, self.player.rect.y = self.player.x, self.player.y
                        self.sound_manager.play_sound("obstacle_hit", 0.5)
                elif enemy_hit == "phantom":
                    # Phantom drains player's health
                    if not self.player.take_damage(10):
                        self.game_state = "GAME_OVER"
                    else:
                        self.sound_manager.play_sound("whisper1", 0.5)
            
            # Update high score
            if self.player.score > self.world.highest_score:
                self.world.highest_score = self.player.score
    
    def render(self):
        """Render the game screen."""
        if self.game_state == "PLAYING" or self.game_state == "VICTORY":
            # Render world with background
            self.world.render(self.screen, (self.camera_x, self.camera_y), 
                             50 if not self.echo_active else 200)
                             
            # Render door indicator
            self.door_indicator.render(self.screen, (self.camera_x, self.camera_y))
            
            # Render turrets and projectiles
            for turret in self.turrets:
                turret.render(self.screen, (self.camera_x, self.camera_y))
            
            # Render projectiles
            for proj in self.projectiles:
                proj.render(self.screen, (self.camera_x, self.camera_y))
            
            # Render echo effect - now used as a "reveal" ability
            if self.echo_active:
                # Calculate echo intensity based on timer
                intensity = 255 - int(255 * (self.echo_timer / ECHO_DURATION))
                
                # Clear echo surface
                self.echo_surface.fill((0, 0, 0, 0))
                
                # Draw expanding circle for echo effect
                radius = int(self.echo_timer * ECHO_SPEED)
                pygame.draw.circle(
                    self.echo_surface, 
                    (200, 50, 200, intensity), 
                    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 
                    radius, 
                    2
                )
                
                # Draw another circle for visual effect
                if radius > 10:
                    pygame.draw.circle(
                        self.echo_surface, 
                        (150, 50, 150, intensity // 2), 
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 
                        radius - 10, 
                        2
                    )
                
                # Blit echo surface onto screen
                self.screen.blit(self.echo_surface, (0, 0))
            
            # Always render player in center of screen
            self.player.render(self.screen, (self.camera_x, self.camera_y))
            
            # Show level info
            if self.show_tutorial:
                self.tutorial_timer += 1
                if self.tutorial_timer < 300:  # Show for 5 seconds
                    # Draw semi-transparent background
                    tutorial_bg = pygame.Surface((SCREEN_WIDTH, 120))
                    tutorial_bg.fill((0, 0, 0))
                    tutorial_bg.set_alpha(180)
                    self.screen.blit(tutorial_bg, (0, 0))
                    
                    # Draw level name
                    level_name = self.font.render(f"Level: {self.level_data['name']}", True, (200, 50, 200))
                    self.screen.blit(level_name, (SCREEN_WIDTH // 2 - level_name.get_width() // 2, 20))
                    
                    # Draw tutorial text
                    controls = self.font.render("WASD/Arrows: Move | SPACE: Reveal Spirits", True, WHITE)
                    self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, 50))
                    
                    objective = self.font.render(f"Collect {self.world.ritual_items_required} ritual items to unlock the exit door", True, WHITE)
                    self.screen.blit(objective, (SCREEN_WIDTH // 2 - objective.get_width() // 2, 80))
                else:
                    self.show_tutorial = False
            
            # Draw UI elements - reveal cooldown indicator
            cooldown_pct = min(1.0, (pygame.time.get_ticks() - self.player.last_sound_time) / self.player.sound_cooldown)
            pygame.draw.rect(self.screen, (50, 50, 50), (10, 10, 100, 20))
            pygame.draw.rect(self.screen, (200, 50, 200), (10, 10, 100 * cooldown_pct, 20))
            sound_text = self.font.render("Reveal", True, WHITE)
            self.screen.blit(sound_text, (120, 10))
            
            # Draw health bar
            health_pct = max(0, self.player.health / 100)
            pygame.draw.rect(self.screen, (50, 50, 50), (10, 40, 100, 20))
            health_color = (
                int(255 * (1 - health_pct)),  # Red increases as health decreases
                int(255 * health_pct),        # Green decreases as health decreases
                50
            )
            pygame.draw.rect(self.screen, health_color, (10, 40, 100 * health_pct, 20))
            health_text = self.font.render("Health", True, WHITE)
            self.screen.blit(health_text, (120, 40))
            
            # Draw score and ritual item counter
            score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
            self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 20, 10))
            
            # Draw high score
            if self.world.highest_score > 0:
                high_score_text = self.font.render(f"Best: {self.world.highest_score}", True, (200, 200, 100))
                self.screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 20, 40))
            
            # Draw ritual item counter with icon
            ritual_bg = pygame.Surface((120, 30), pygame.SRCALPHA)
            ritual_bg.fill((0, 0, 0, 128))
            self.screen.blit(ritual_bg, (SCREEN_WIDTH - 140, 70))
            
            ritual_text = self.font.render(f"Ritual: {self.world.ritual_items_collected}", True, (200, 50, 200))
            self.screen.blit(ritual_text, (SCREEN_WIDTH - 135, 75))
            
            # Show victory screen if player won
            if self.game_state == "VICTORY":
                # Semi-transparent overlay
                victory_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                victory_overlay.fill((0, 0, 0, 180))
                self.screen.blit(victory_overlay, (0, 0))
                
                # Victory message
                victory_text = self.title_font.render("RITUAL COMPLETE", True, (200, 50, 200))
                self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, 
                                              SCREEN_HEIGHT // 2 - 100))
                
                # Score display
                score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
                self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                            SCREEN_HEIGHT // 2 - 20))
                
                # High score display
                if self.player.score >= self.world.highest_score:
                    high_score_text = self.font.render("NEW HIGH SCORE!", True, (255, 215, 0))
                    self.screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 
                                                    SCREEN_HEIGHT // 2 + 20))
                
                # Continue prompt
                continue_text = self.font.render("Press SPACE to play again", True, WHITE)
                self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 
                                               SCREEN_HEIGHT // 2 + 80))
        
        elif self.game_state == "MEMORY":
            # Render memory fragment with a nice background
            memory_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            memory_bg.fill((20, 20, 40))
            self.screen.blit(memory_bg, (0, 0))
            
            # Draw a decorative frame
            pygame.draw.rect(self.screen, (100, 100, 180), (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 3)
            
            # Render the memory content
            self.memory_manager.render(self.screen)
            
            # Display prompt to continue with animation
            alpha = 128 + int(127 * abs(math.sin(pygame.time.get_ticks() / 500)))
            continue_text = self.font.render("Press any key to continue...", True, WHITE)
            self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 
                                           SCREEN_HEIGHT - 80))
        
        elif self.game_state == "GAME_OVER":
            # Game over screen with creepy background
            # Draw background texture first
            if hasattr(self.world, "background_texture") and self.world.background_texture:
                bg_width, bg_height = self.world.background_texture.get_size()
                for x in range(0, SCREEN_WIDTH, bg_width):
                    for y in range(0, SCREEN_HEIGHT, bg_height):
                        self.screen.blit(self.world.background_texture, (x, y))
            
            # Add red overlay that pulses
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pulse = int(40 + 20 * math.sin(pygame.time.get_ticks() / 200))
            overlay.fill((pulse, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            # Draw creepy symbols
            for i in range(10):
                x = SCREEN_WIDTH // 2 + int(200 * math.cos(i * math.pi / 5 + pygame.time.get_ticks() / 2000))
                y = SCREEN_HEIGHT // 2 + int(200 * math.sin(i * math.pi / 5 + pygame.time.get_ticks() / 2000))
                size = 10 + 5 * math.sin(pygame.time.get_ticks() / 500 + i)
                pygame.draw.circle(self.screen, (200, 0, 0), (int(x), int(y)), int(size))
            
            # Game over text with shadow and blood effect
            shadow_text = self.title_font.render("YOU ARE CONSUMED", True, BLACK)
            self.screen.blit(shadow_text, (SCREEN_WIDTH // 2 - shadow_text.get_width() // 2 + 2, 
                                         SCREEN_HEIGHT // 2 - 52))
            
            game_over_text = self.title_font.render("YOU ARE CONSUMED", True, (200, 0, 0))
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                            SCREEN_HEIGHT // 2 - 50))
            
            # Show score
            score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                                        SCREEN_HEIGHT // 2))
            
            # Restart prompt with animation
            alpha = 128 + int(127 * abs(math.sin(pygame.time.get_ticks() / 500)))
            restart_text = self.font.render("Press R to try again", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                          SCREEN_HEIGHT // 2 + 60))
        
        # Update the display
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        result = None
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
            
            # Check if we need to restart or victory
            if self.game_state == "RESTART":
                result = "RESTART"
                self.running = False
            elif self.game_state == "VICTORY":
                result = "VICTORY"
                self.running = False
                
        return result