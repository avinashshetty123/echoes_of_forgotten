import pygame
import os
import random
import math
from .constants import *

class SoundManager:
    def __init__(self):
        """Initialize the sound manager."""
        # Ensure pygame mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Load sound effects
        self._load_sounds()
        
        # Ambient sound settings
        self.ambient_sounds = []
        self.current_ambient = None
        self.ambient_timer = 0
        self.ambient_interval = random.randint(10000, 20000)  # 10-20 seconds
    
    def _load_sounds(self):
        """Load all sound effects."""
        # Define sound paths (these files don't exist yet, but will be placeholders)
        sound_files = {
            "echo": "echo_ping.wav",
            "footstep": "footstep.wav",
            "warden_groan": "warden_groan.wav",
            "door_creak": "door_creak.wav",
            "memory_trigger": "memory_trigger.wav",
            "heartbeat": "heartbeat.wav",
            "whisper1": "whisper1.wav",
            "whisper2": "whisper2.wav",
            "whisper3": "whisper3.wav",
            "key_pickup": "key_pickup.wav",
            "obstacle_hit": "obstacle_hit.wav",
            "victory": "victory.wav",
        }
        
        # Create assets directory if it doesn't exist
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "game", "assets", "audio")
        os.makedirs(assets_dir, exist_ok=True)
        
        # Load each sound or create placeholder
        for sound_name, file_name in sound_files.items():
            file_path = os.path.join(assets_dir, file_name)
            
            # Check if file exists
            if os.path.exists(file_path):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                except pygame.error:
                    # If file exists but is invalid, create a placeholder sound
                    self.sounds[sound_name] = self._create_placeholder_sound(sound_name)
            else:
                # Create a placeholder sound (will be replaced with actual sounds later)
                self.sounds[sound_name] = self._create_placeholder_sound(sound_name)
        
        # Set up ambient sounds
        self.ambient_sounds = ["whisper1", "whisper2", "whisper3", "warden_groan"]
    
    def _create_placeholder_sound(self, sound_name):
        """Create a placeholder sound effect."""
        # Create a simple sound based on the type
        if sound_name == "echo":
            # High-pitched ping
            return self._generate_tone(440, 0.2)
        elif sound_name == "footstep":
            # Low thud
            return self._generate_tone(100, 0.1)
        elif sound_name == "warden_groan":
            # Low, eerie sound
            return self._generate_tone(80, 0.5)
        elif sound_name == "door_creak":
            # Medium pitch noise
            return self._generate_tone(220, 0.3)
        elif sound_name == "memory_trigger":
            # High, shimmering sound
            return self._generate_tone(660, 0.4)
        elif sound_name == "heartbeat":
            # Low, rhythmic sound
            return self._generate_tone(60, 0.2)
        elif "whisper" in sound_name:
            # Mid-range hiss
            return self._generate_tone(300, 0.3)
        else:
            # Generic beep
            return self._generate_tone(440, 0.1)
    
    def _generate_tone(self, frequency, duration):
        """Generate a simple tone as a placeholder sound."""
        # This is a simplified version - in a real game, you'd use actual sound files
        sample_rate = 44100
        n_samples = int(round(duration * sample_rate))
        
        # Generate a simple sine wave
        buf = bytearray(n_samples)
        for i in range(n_samples):
            # Simple fade in/out
            if i < n_samples * 0.1:
                amplitude = i / (n_samples * 0.1)
            elif i > n_samples * 0.9:
                amplitude = (n_samples - i) / (n_samples * 0.1)
            else:
                amplitude = 1.0
                
            buf[i] = 128 + int(amplitude * 127 * (0.5 if i % (sample_rate // frequency) < (sample_rate // frequency // 2) else -0.5))
        
        # Create a Sound object from the buffer
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        return sound
    
    def _save_placeholder_sound(self, sound_name, file_path):
        """Save placeholder sound to file for future use."""
        # In a real implementation, this would save the generated sound
        # For now, we'll skip saving placeholder files
        pass
    
    def play_sound(self, sound_name, volume=1.0):
        """Play a sound effect."""
        if sound_name in self.sounds:
            try:
                # Set volume and ensure channel is available
                self.sounds[sound_name].set_volume(volume)
                channel = pygame.mixer.find_channel(True)  # Force find a channel
                if channel:
                    channel.set_volume(volume)
                    channel.play(self.sounds[sound_name])
                else:
                    # Fallback to normal play
                    self.sounds[sound_name].play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")
    
    def play_spatial_sound(self, sound_name, source_pos, listener_pos, max_distance=300):
        """Play a sound with volume based on distance from listener."""
        if sound_name in self.sounds:
            # Calculate distance
            dx = source_pos[0] - listener_pos[0]
            dy = source_pos[1] - listener_pos[1]
            distance = (dx**2 + dy**2)**0.5
            
            # Calculate volume based on distance
            if distance >= max_distance:
                volume = 0.0
            else:
                volume = 1.0 - (distance / max_distance)
            
            # Calculate stereo panning (-1.0 to 1.0)
            if abs(dx) > 0.1:  # Avoid division by zero
                pan = max(-1.0, min(1.0, dx / (max_distance / 2)))
            else:
                pan = 0.0
            
            # Play sound with calculated volume
            self.sounds[sound_name].set_volume(volume)
            
            # Note: Pygame doesn't support true stereo panning natively
            # In a real game, you'd use a more advanced audio library
            # This is a simplified version
            self.sounds[sound_name].play()
    
    def update_ambient_sounds(self, player_pos):
        """Update ambient sounds based on time and player position."""
        current_time = pygame.time.get_ticks()
        
        # Check if it's time to play a new ambient sound
        if current_time - self.ambient_timer > self.ambient_interval:
            # Reset timer and set new interval
            self.ambient_timer = current_time
            self.ambient_interval = random.randint(10000, 20000)  # 10-20 seconds
            
            # Choose a random ambient sound
            sound_name = random.choice(self.ambient_sounds)
            
            # Generate a random position for the sound
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(100, 200)
            sound_pos = (
                player_pos[0] + distance * math.cos(angle),
                player_pos[1] + distance * math.sin(angle)
            )
            
            # Play the spatial sound
            self.play_spatial_sound(sound_name, sound_pos, player_pos)