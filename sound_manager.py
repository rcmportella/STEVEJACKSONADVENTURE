"""
Sound Manager for Text Adventure Game
Handles background music and sound effects using pygame
"""
import os

# Try to import pygame, but don't crash if it's not available
try:
    import pygame
    pygame.mixer.init()
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False
    print("Note: pygame not available. Running without sound.")
except Exception:
    SOUND_ENABLED = False
    print("Note: Could not initialize sound system. Running without sound.")


class SoundManager:
    """Manages game sounds and music"""
    
    def __init__(self, sounds_folder="sounds"):
        """
        Initialize the sound manager.
        
        Args:
            sounds_folder: Path to folder containing sound files
        """
        self.sounds_folder = sounds_folder
        self.enabled = SOUND_ENABLED
        self.music_volume = 0.3
        self.sfx_volume = 0.5
        self.sounds = {}
        self.music_playing = False
        
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)
            self._load_sounds()
    
    def _load_sounds(self):
        """Preload sound effects if they exist"""
        sound_files = {
            'combat_hit': 'combat_hit.wav',
            'combat_miss': 'combat_miss.wav',
            'victory': 'victory.wav',
            'defeat': 'defeat.wav',
            'treasure': 'treasure.wav',
            'healing': 'healing.wav',
            'level_up': 'level_up.wav',
            'menu_select': 'menu_select.wav',
        }
        
        for name, filename in sound_files.items():
            filepath = os.path.join(self.sounds_folder, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    self.sounds[name].set_volume(self.sfx_volume)
                except pygame.error:
                    pass  # Skip if file can't be loaded
    
    def play_music(self, filename, loops=-1):
        """
        Play background music.
        
        Args:
            filename: Name of music file in sounds folder
            loops: Number of times to loop (-1 = infinite)
        """
        if not self.enabled:
            return
        
        filepath = os.path.join(self.sounds_folder, filename)
        if os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play(loops)
                self.music_playing = True
            except pygame.error:
                pass
    
    def stop_music(self):
        """Stop background music"""
        if self.enabled and self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def play_sound(self, sound_name):
        """
        Play a sound effect.
        
        Args:
            sound_name: Name of the sound (e.g., 'combat_hit', 'victory')
        """
        if not self.enabled:
            return
        
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def set_music_volume(self, volume):
        """
        Set music volume (0.0 to 1.0).
        
        Args:
            volume: Volume level (0.0 = silent, 1.0 = max)
        """
        if self.enabled:
            self.music_volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """
        Set sound effects volume (0.0 to 1.0).
        
        Args:
            volume: Volume level (0.0 = silent, 1.0 = max)
        """
        if self.enabled:
            self.sfx_volume = max(0.0, min(1.0, volume))
            for sound in self.sounds.values():
                sound.set_volume(self.sfx_volume)
    
    def toggle_music(self):
        """Toggle music on/off"""
        if not self.enabled:
            return False
        
        if self.music_playing:
            pygame.mixer.music.pause()
            self.music_playing = False
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
        
        return self.music_playing
    
    def is_enabled(self):
        """Check if sound system is available"""
        return self.enabled


# Global sound manager instance
sound_manager = SoundManager()
