# Echoes of the Forgotten

A 2D psychological horror puzzle game built with Pygame, centered around sound-based navigation (echolocation) and a layered mystery-horror narrative.

## Game Concept

You play as Elara, a blind girl who wakes up in a decrepit orphanage with no memory of how she got there. Using sound to navigate the pitch-black world, you must solve puzzles, avoid "The Warden," and collect memory fragments to uncover the truth about your past.

## Core Mechanics

### Echolocation Navigation
- The screen is mostly black
- Emit sound (spacebar) to reveal the environment momentarily through radial ripples
- Different surfaces return different echo patterns (metal, wood, flesh, stone)

### Sound-Based Puzzles
- Reproduce rhythms
- Identify sound directions
- Solve voice-based riddles
- Interpret reversed audio clues

### The Warden (AI Enemy)
- Invisible ghost-like enemy that reacts to sound
- Must strategically distract it by making noise elsewhere
- Different states: patrolling, investigating, hunting

### Memory Fragments
- Scattered throughout the orphanage
- Reveal partial flashbacks in audio + visuals
- Non-linear and affect the ending based on collection order

## Story Outline

Elara was one of the orphanage children. A fire broke out years ago, which she may have caused. The "Warden" is the ghost of the cruel caretaker. The orphanage was hiding twisted experiments on children with sensory gifts.

## Endings

- **Redemption Ending**: Collect all memories, accept trauma and escape
- **Denial Ending**: Collect partial memories, escape but the Warden follows
- **Possession Ending**: Find no core memories, become the next Warden

## Controls

- **WASD/Arrow Keys**: Move
- **Spacebar**: Emit sound/echolocation
- **ESC**: Pause/Quit

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python main.py`

## Development Notes

This project demonstrates:
- Sound-based gameplay mechanics
- Atmospheric horror through limited visibility
- AI enemy with different behavior states
- Branching narrative based on player exploration
- Dynamic echo visualization effects

## Future Enhancements

- Additional levels beyond the nursery
- More complex puzzles
- Voice acting for memory fragments
- Enhanced sound design with true 3D audio
- Visual effects for memory flashbacks