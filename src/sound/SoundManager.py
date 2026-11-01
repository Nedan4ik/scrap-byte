from __future__ import annotations
import os
from pathlib import Path
import pygame


class SoundManager:
    _instance: SoundManager | None = None

    def __init__(self, sounds_dir: str | Path | None = None):
        self.enabled: bool = True
        self.sfx_volume: float = 0.8
        self.ambient_volume: float = 0.35
        self.initialized: bool = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.drone_channel: pygame.mixer.Channel | None = None
        self.ambient_playing: bool = False

        if sounds_dir:
            self.sounds_dir = Path(sounds_dir)
        else:
            self.sounds_dir = Path("assets/sounds")

        self.init()

    @classmethod
    def get_instance(cls) -> SoundManager:
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def init(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.initialized = True
            except Exception:
                self.initialized = False
                return
        else:
            self.initialized = True

        self._preload_sounds()

    def _preload_sounds(self):
        if not self.initialized:
            return

        sound_files = {
            "drone_move": "drone_move.ogg",
            "drone_turn": "drone_turn.wav",
            "pickup_success": "pickup_success.ogg",
            "pickup_fail": "pickup_fail.wav",
            "obstacle_hit": "obstacle_hit.ogg",
            "level_win": "level_win.ogg",
            "ui_click": "ui_click.wav",
        }

        for key, fname in sound_files.items():
            path = self.sounds_dir / fname
            if path.exists():
                try:
                    snd = pygame.mixer.Sound(str(path))
                    self.sounds[key] = snd
                except Exception:
                    pass

    def is_sound_enabled(self) -> bool:
        return self.enabled

    def set_sound_enabled(self, enabled: bool):
        self.enabled = bool(enabled)
        if not self.enabled:
            self.stop_all()
        else:
            self.play_ambient()

    def toggle_sound(self) -> bool:
        self.set_sound_enabled(not self.enabled)
        return self.enabled

    def play_sound(self, name: str, volume: float = 1.0) -> pygame.mixer.Channel | None:
        if not self.enabled or not self.initialized:
            return None

        snd = self.sounds.get(name)
        if not snd:
            path = self.sounds_dir / f"{name}.ogg"
            if not path.exists():
                path = self.sounds_dir / f"{name}.wav"
            if path.exists():
                try:
                    snd = pygame.mixer.Sound(str(path))
                    self.sounds[name] = snd
                except Exception:
                    return None
            else:
                return None

        try:
            snd.set_volume(max(0.0, min(1.0, volume * self.sfx_volume)))
            return snd.play()
        except Exception:
            return None

    def play_ambient(self, loop: bool = True):
        if not self.enabled or not self.initialized:
            return

        ambient_path = self.sounds_dir / "ambient.mp3"
        if not ambient_path.exists():
            ambient_path = self.sounds_dir / "ambient.ogg"

        if not ambient_path.exists():
            return

        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(str(ambient_path))
                pygame.mixer.music.set_volume(self.ambient_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.ambient_playing = True
        except Exception:
            self.ambient_playing = False

    def stop_ambient(self):
        if not self.initialized:
            return
        try:
            pygame.mixer.music.stop()
            self.ambient_playing = False
        except Exception:
            pass

    def play_drone_move(self):
        if not self.enabled or not self.initialized:
            return

        snd = self.sounds.get("drone_move")
        if not snd:
            return

        try:
            if self.drone_channel and self.drone_channel.get_busy():
                return
            snd.set_volume(0.65 * self.sfx_volume)
            self.drone_channel = snd.play()
        except Exception:
            pass

    def stop_drone_move(self):
        if self.drone_channel:
            try:
                self.drone_channel.fadeout(120)
            except Exception:
                pass
            self.drone_channel = None

    def play_drone_turn(self):
        self.play_sound("drone_turn", volume=0.5)

    def play_pickup_success(self):
        self.play_sound("pickup_success", volume=0.85)

    def play_pickup_fail(self):
        self.play_sound("pickup_fail", volume=0.7)

    def play_obstacle_hit(self):
        self.play_sound("obstacle_hit", volume=0.75)

    def play_level_win(self):
        self.play_sound("level_win", volume=0.85)

    def play_ui_click(self):
        self.play_sound("ui_click", volume=0.45)

    def stop_all(self):
        if not self.initialized:
            return
        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            self.drone_channel = None
            self.ambient_playing = False
        except Exception:
            pass
