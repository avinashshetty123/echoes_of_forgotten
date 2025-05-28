import os

# Base directory
base_dir = os.path.join(os.getcwd(), "echoes_of_forgotten")
os.makedirs(base_dir, exist_ok=True)

# Create subdirectories
dirs = [
    os.path.join(base_dir, "game"),
    os.path.join(base_dir, "game", "assets"),
    os.path.join(base_dir, "game", "assets", "audio"),
    os.path.join(base_dir, "game", "assets", "images"),
    os.path.join(base_dir, "game", "assets", "fonts"),
]

for directory in dirs:
    os.makedirs(directory, exist_ok=True)

print("Project structure created successfully!")