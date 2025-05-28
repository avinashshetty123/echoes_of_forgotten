# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Game settings
FPS = 60
PLAYER_SPEED = 3
WARDEN_SPEED = 2
WARDEN_DETECTION_RADIUS = 150
ECHO_DURATION = 60  # frames
ECHO_SPEED = 5  # pixels per frame

# Sound settings
SOUND_COOLDOWN = 1000  # milliseconds

# Memory fragment settings
MEMORY_TYPES = ["orphanage", "fire", "warden", "experiments"]

# Surface types and their echo properties
SURFACE_TYPES = {
    "wood": {"color": (139, 69, 19), "echo_intensity": 0.7},
    "metal": {"color": (192, 192, 192), "echo_intensity": 0.9},
    "flesh": {"color": (255, 182, 193), "echo_intensity": 0.5},
    "stone": {"color": (169, 169, 169), "echo_intensity": 0.8},
    "fabric": {"color": (210, 180, 140), "echo_intensity": 0.3}
}

# Game states
STATES = ["PLAYING", "PAUSED", "MEMORY", "GAME_OVER"]

# Endings
ENDINGS = ["REDEMPTION", "DENIAL", "POSSESSION"]