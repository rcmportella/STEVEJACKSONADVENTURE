# Sound Files for Text Adventure

This folder should contain your game's sound effects and music.

## Sound System

The game uses pygame.mixer to play sounds. If pygame is not installed or sound files are missing, the game will run normally without sound.

## Installation

```bash
pip install pygame
```

## Required Sound Files

Place the following files in this folder (WAV or MP3 format):

### Background Music
- **adventure_theme.mp3** - Main background music that loops during gameplay

### Sound Effects
- **combat_hit.wav** - Played when an attack hits
- **combat_miss.wav** - Played when an attack misses
- **victory.wav** - Played when winning a battle or the game
- **defeat.wav** - Played when losing a battle or dying
- **treasure.wav** - Played when finding treasure
- **healing.wav** - Played when using a healing potion
- **level_up.wav** - Played when character levels up
- **menu_select.wav** - Played when selecting menu options

## Sound File Recommendations

### Where to Get Free Sounds

1. **Freesound.org** - https://freesound.org/
   - Large library of free sound effects
   - Creative Commons licensed

2. **OpenGameArt.org** - https://opengameart.org/
   - Game-specific sounds and music
   - Many public domain options

3. **ZapSplat** - https://www.zapsplat.com/
   - Free for indie game developers

4. **Incompetech** (music) - https://incompetech.com/
   - Royalty-free background music
   - Perfect for game loops

### Format Guidelines

- **Music**: MP3 or OGG (smaller file size, good for loops)
- **Sound Effects**: WAV (instant playback, no decoding lag)
- **Volume**: Normalize all sounds to similar volumes
- **Length**: 
  - Music: 2-5 minutes (will loop)
  - Sound effects: 0.5-3 seconds

## Volume Control

You can adjust volumes in code:
```python
from sound_manager import sound_manager

# Set music volume (0.0 to 1.0)
sound_manager.set_music_volume(0.3)

# Set sound effects volume (0.0 to 1.0)
sound_manager.set_sfx_volume(0.5)
```

## Testing

The game will work without any sound files - it's fully optional!

Test your sounds by:
1. Adding at least one file to this folder
2. Running the game
3. Checking if sounds play at appropriate moments

## Notes

- All sound file names are case-sensitive on Linux/Mac
- Supported formats: WAV, MP3, OGG
- Place files directly in this folder (not in subfolders)
- The game automatically checks if files exist before trying to load them
