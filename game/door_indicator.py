import pygame
import math

class DoorIndicator:
    def __init__(self, world):
        self.world = world
        self.font = pygame.font.Font(None, 20)
    
    def render(self, screen, camera_pos):
        # Find exit door in active chunks
        exit_door = None
        for chunk in self.world.active_chunks:
            for portal in chunk.portals:
                if portal.get("is_exit", False):
                    exit_door = portal
                    break
            if exit_door:
                break
        
        if not exit_door:
            return
        
        # Calculate screen position of exit door
        door_x = exit_door["rect"].x - camera_pos[0]
        door_y = exit_door["rect"].y - camera_pos[1]
        
        # If door is on screen, just show the ritual count
        if -60 < door_x < pygame.display.get_surface().get_width() + 60 and -60 < door_y < pygame.display.get_surface().get_height() + 60:
            # Draw ritual count above door
            count_text = self.font.render(f"{self.world.ritual_items_collected}/{self.world.ritual_items_required}", 
                                        True, (255, 255, 255))
            screen.blit(count_text, (door_x + 40 - count_text.get_width() // 2, door_y - 20))
            return
        
        # Door is off-screen, show direction indicator
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        
        # Calculate direction to exit door
        player_x = screen_width // 2
        player_y = screen_height // 2
        dx = exit_door["rect"].centerx - (camera_pos[0] + player_x)
        dy = exit_door["rect"].centery - (camera_pos[1] + player_y)
        angle = math.atan2(dy, dx)
        
        # Calculate position on screen edge
        edge_x = player_x + math.cos(angle) * (min(screen_width, screen_height) // 2 - 40)
        edge_y = player_y + math.sin(angle) * (min(screen_width, screen_height) // 2 - 40)
        
        # Clamp to screen edges
        edge_x = max(30, min(screen_width - 30, edge_x))
        edge_y = max(30, min(screen_height - 30, edge_y))
        
        # Draw arrow pointing to exit
        arrow_color = (0, 255, 0) if self.world.ritual_items_collected >= self.world.ritual_items_required else (255, 255, 0)
        arrow_size = 15
        
        # Draw arrow head
        points = [
            (edge_x + math.cos(angle) * arrow_size, edge_y + math.sin(angle) * arrow_size),
            (edge_x + math.cos(angle + 2.5) * arrow_size, edge_y + math.sin(angle + 2.5) * arrow_size),
            (edge_x + math.cos(angle - 2.5) * arrow_size, edge_y + math.sin(angle - 2.5) * arrow_size)
        ]
        pygame.draw.polygon(screen, arrow_color, points)
        
        # Draw "EXIT" text
        exit_text = self.font.render("EXIT", True, arrow_color)
        screen.blit(exit_text, (edge_x - exit_text.get_width() // 2, edge_y - 25))
        
        # Draw ritual count
        count_text = self.font.render(f"{self.world.ritual_items_collected}/{self.world.ritual_items_required}", 
                                    True, arrow_color)
        screen.blit(count_text, (edge_x - count_text.get_width() // 2, edge_y + 15))