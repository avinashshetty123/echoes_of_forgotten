import pygame
from .constants import *

class MemoryFragmentManager:
    def __init__(self):
        """Initialize the memory fragment manager."""
        self.current_memory = None
        self.display_timer = 0
        self.display_duration = 300  # frames (5 seconds)
        self.fade_in = 30  # frames for fade in
        self.fade_out = 30  # frames for fade out
        
        # Load font
        self.font = pygame.font.Font(None, 28)
        
        # Memory content
        self.memories = {
            "orphanage": {
                "text": "I remember the nursery... the sound of music boxes and children crying in the night.",
                "image": None,
                "audio": "memory_nursery.wav"
            },
            "fire": {
                "text": "The flames... they were everywhere. I couldn't see, but I could feel the heat. I heard the screams.",
                "image": None,
                "audio": "memory_fire.wav"
            },
            "warden": {
                "text": "The Warden's footsteps... always heavy, always angry. We learned to be silent when he approached.",
                "image": None,
                "audio": "memory_warden.wav"
            },
            "experiments": {
                "text": "They blindfolded us for the tests. 'Listen carefully,' they'd say. 'Tell us what you hear.' Some children never returned.",
                "image": None,
                "audio": "memory_experiments.wav"
            }
        }
    
    def trigger_memory(self, memory_fragment):
        """Trigger a memory fragment display."""
        self.current_memory = memory_fragment
        self.display_timer = 0
    
    def update(self):
        """Update the memory display."""
        if self.current_memory:
            self.display_timer += 1
            
            # Check if display time is over
            if self.display_timer >= self.display_duration:
                self.current_memory = None
    
    def render(self, surface):
        """Render the current memory fragment."""
        if self.current_memory:
            # Calculate alpha based on fade in/out
            if self.display_timer < self.fade_in:
                alpha = int(255 * (self.display_timer / self.fade_in))
            elif self.display_timer > self.display_duration - self.fade_out:
                alpha = int(255 * ((self.display_duration - self.display_timer) / self.fade_out))
            else:
                alpha = 255
            
            # Create a semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))
            
            # Get memory content
            memory_type = self.current_memory.type
            memory_data = self.memories.get(memory_type, {"text": "A forgotten memory...", "image": None, "audio": None})
            
            # Render memory text
            text = memory_data["text"]
            
            # Word wrap the text
            words = text.split(' ')
            lines = []
            line = ""
            for word in words:
                test_line = line + word + " "
                # Check if the line is too long
                if self.font.size(test_line)[0] < SCREEN_WIDTH - 100:
                    line = test_line
                else:
                    lines.append(line)
                    line = word + " "
            lines.append(line)  # Add the last line
            
            # Render each line
            y_offset = SCREEN_HEIGHT // 2 - (len(lines) * 30) // 2
            for line in lines:
                text_surface = self.font.render(line, True, (255, 255, 255, alpha))
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                surface.blit(text_surface, text_rect)
                y_offset += 30
            
            # If there's an image, render it
            if memory_data["image"]:
                # This would load and display an image in a real implementation
                pass
    
    def get_collected_memories(self):
        """Return a list of collected memory types."""
        return [memory.type for memory in self.collected_memories]