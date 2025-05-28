import pygame
import sys
import os
from game.engine_new import GameEngine
from game.start_screen import StartScreen
from game.story import StoryScreen
from game.level_system import LevelSystem, LevelTransitionScreen

def main():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Create screen
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dark Ritual")
    
    # Initialize level system
    level_system = LevelSystem()
    
    # Start with the start screen
    start_screen = StartScreen(screen)
    clock = pygame.time.Clock()
    running = True
    
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Handle start screen
        action = start_screen.handle_events(events)
        if action == "START":
            # Show story screen first
            story_screen = StoryScreen(screen)
            story_done = False
            
            while not story_done and running:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        running = False
                
                story_done = story_screen.handle_events(events)
                story_screen.update()
                story_screen.render()
                pygame.display.flip()
                clock.tick(60)
            
            # Show level transition screen
            if running:
                level_data = level_system.get_current_level_data()
                transition_screen = LevelTransitionScreen(screen, level_data)
                transition_done = False
                
                while not transition_done and running:
                    events = pygame.event.get()
                    for event in events:
                        if event.type == pygame.QUIT:
                            running = False
                    
                    transition_done = transition_screen.handle_events(events)
                    transition_screen.update()
                    transition_screen.render()
                    pygame.display.flip()
                    clock.tick(60)
            
            # Start the game with configured warden speed and level data
            if running:
                warden_speed = start_screen.warden_speed * level_data["warden_speed_modifier"]
                game = GameEngine(warden_speed, level_data)
                game_result = game.run()
                
                if game_result == "VICTORY":
                    # Update high score
                    level_system.update_high_score(level_system.current_level, game.player.score)
                    
                    # Advance to next level if possible
                    if level_system.advance_level():
                        # Continue to next level
                        continue
                    else:
                        # Game completed
                        running = False
                elif game_result == "RESTART":
                    # Return to start screen
                    start_screen = StartScreen(screen)
                else:
                    # Quit
                    running = False
        elif action == "QUIT":
            running = False
        
        # Update and render start screen
        start_screen.update()
        start_screen.render()
        
        pygame.display.flip()
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()