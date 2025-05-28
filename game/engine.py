import pygame
import sys
import os
import math
import random
from .player_animated import AnimatedPlayer
from .infinite_world import InfiniteWorld
from .sound_manager import SoundManager
from .memory_fragment import MemoryFragmentManager
from .constants import *

class GameEngine:
    def __init__(self):
        """Initialize the game engine and all game components."""
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dark Ritual")
        
        # Set up the clock
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.game_state = "PLAYING"  # PLAYING, PAUSED, MEMORY, GAME_OVER, VICTORY
        
        # Initialize game components
        self.sound_manager = SoundManager()
        self.player = AnimatedPlayer(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.sound_manager)
        self.world = InfiniteWorld(self.sound_manager)
        self.memory_manager = MemoryFragmentManager()
        
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
                    self.player.emit_sound()
                    self.echo_active = True
                    self.echo_timer = 0
                    self.sound_manager.play_sound("echo")
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
            
            # Track if player made a sound this frame
            sound_made = False
            if self.echo_active and self.echo_timer == 0:
                sound_made = True
            
            # Update all enemies
            self.level.update_enemies((self.player.x, self.player.y), sound_made)
            
            # Check for collisions with memory fragments
            fragment = self.level.check_memory_collision(self.player.rect)
            if fragment:
                self.game_state = "MEMORY"
                self.memory_manager.trigger_memory(fragment)
                self.player.score += 200
            
            # Check for collisions with collectables
            collectable = self.level.check_collectable_collision(self.player.rect)
            if collectable == "ritual":
                self.player.score += 100
                # Play special sound when all items collected
                if self.level.ritual_items_collected >= self.level.ritual_items_required:
                    self.sound_manager.play_sound("victory")
            
            # Check if player has reached the exit with enough ritual items
            if self.level.check_exit_collision(self.player.rect):
                self.game_state = "VICTORY"
                self.player.score += 1000
                
                # Check for high score
                if self.player.score > self.level.highest_score:
                    self.level.highest_score = self.player.score
            
            # Update echo effect
            if self.echo_active:
                self.echo_timer += 1
                if self.echo_timer > ECHO_DURATION:
                    self.echo_active = False
            
            # Check for enemy collision
            enemy_hit = self.level.check_enemy_collision(self.player.rect)
            if enemy_hit:
                # Different enemies have different effects
                if enemy_hit == "warden":
                    # Warden is instant game over
                    self.game_state = "GAME_OVER"
                elif enemy_hit == "crawler":
                    # Crawler damages player
                    self.player.health -= 20
                    # Push player back
                    self.player.x, self.player.y = prev_x, prev_y
                    self.player.rect.x, self.player.rect.y = prev_x, prev_y
                    self.sound_manager.play_sound("obstacle_hit", 0.5)
                elif enemy_hit == "phantom":
                    # Phantom drains player's health
                    self.player.health -= 10
                    self.sound_manager.play_sound("whisper1", 0.5)
                
                # Check if player is dead
                if self.player.health <= 0:
                    self.game_state = "GAME_OVER"
    
    def render(self):
        """Render the game screen."""
        if self.game_state == "PLAYING" or self.game_state == "VICTORY":
            # Render level with background
            self.level.render(self.screen, self.echo_surface, 50 if not self.echo_active else 200)
            
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
                    (self.player.rect.centerx, self.player.rect.centery), 
                    radius, 
                    2
                )
                
                # Draw another circle for visual effect
                if radius > 10:
                    pygame.draw.circle(
                        self.echo_surface, 
                        (150, 50, 150, intensity // 2), 
                        (self.player.rect.centerx, self.player.rect.centery), 
                        radius - 10, 
                        2
                    )
                
                # Blit echo surface onto screen
                self.screen.blit(self.echo_surface, (0, 0))
            
            # Always render player
            self.player.render(self.screen)
            
            # Show tutorial
            if self.show_tutorial:
                self.tutorial_timer += 1
                if self.tutorial_timer < 600:  # Show for 10 seconds
                    # Draw semi-transparent background
                    tutorial_bg = pygame.Surface((SCREEN_WIDTH, 150))
                    tutorial_bg.fill((0, 0, 0))
                    tutorial_bg.set_alpha(180)
                    self.screen.blit(tutorial_bg, (0, SCREEN_HEIGHT - 150))
                    
                    # Draw tutorial text
                    title = self.title_font.render("Dark Ritual", True, (200, 50, 200))
                    self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT - 140))
                    
                    controls = self.font.render("WASD/Arrows: Move | SPACE: Reveal Spirits", True, WHITE)
                    self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 100))
                    
                    objective = self.font.render("Collect ritual items and avoid the spirits", True, WHITE)
                    self.screen.blit(objective, (SCREEN_WIDTH // 2 - objective.get_width() // 2, SCREEN_HEIGHT - 60))
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
            if self.level.highest_score > 0:
                high_score_text = self.font.render(f"Best: {self.level.highest_score}", True, (200, 200, 100))
                self.screen.blit(high_score_text, (SCREEN_WIDTH - high_score_text.get_width() - 20, 40))
            
            # Draw ritual item counter with icon
            ritual_bg = pygame.Surface((120, 30), pygame.SRCALPHA)
            ritual_bg.fill((0, 0, 0, 128))
            self.screen.blit(ritual_bg, (SCREEN_WIDTH - 140, 70))
            
            ritual_text = self.font.render(f"Ritual: {self.level.ritual_items_collected}/{self.level.ritual_items_required}", True, (200, 50, 200))
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
                if self.player.score >= self.level.highest_score:
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
            continue_text = self.font.render("Press any key to continue...", True, (255, 255, 255, alpha))
            self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 
                                           SCREEN_HEIGHT - 80))
        
        elif self.game_state == "GAME_OVER":
            # Game over screen with creepy background
            # Draw background texture first
            if hasattr(self.level, "background_texture") and self.level.background_texture:
                bg_width, bg_height = self.level.background_texture.get_size()
                for x in range(0, SCREEN_WIDTH, bg_width):
                    for y in range(0, SCREEN_HEIGHT, bg_height):
                        self.screen.blit(self.level.background_texture, (x, y))
            
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
                pygame.draw.circle(self.screen, (200, 0, 0), (x, y), size)
            
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
            restart_text = self.font.render("Press R to try again", True, (255, 255, 255, alpha))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                          SCREEN_HEIGHT // 2 + 60))
        
        # Update the display
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        restart_game = False
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
            
            # Check if we need to restart
            if self.game_state == "RESTART":
                restart_game = True
                self.running = False
                
        return restart_game