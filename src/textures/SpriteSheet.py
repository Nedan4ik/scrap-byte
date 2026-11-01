from __future__ import annotations
import xml.etree.ElementTree as ET
from pathlib import Path
import pygame


class SpriteSheet:
    def __init__(self, xml_path: str | Path, image_path: str | Path | None = None):
        self.xml_path = Path(xml_path)
        self.frames: dict[str, pygame.Surface] = {}
        self.animations: dict[str, list[pygame.Surface]] = {}

        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        if image_path is None:
            image_name = root.attrib.get("imagePath", f"{self.xml_path.stem}.png")
            image_path = self.xml_path.parent / image_name

        sheet_image = pygame.image.load(str(image_path)).convert_alpha()

        for sub in root.findall("SubTexture"):
            name = sub.attrib["name"]
            x = int(sub.attrib["x"])
            y = int(sub.attrib["y"])
            w = int(sub.attrib["width"])
            h = int(sub.attrib["height"])

            rect = pygame.Rect(x, y, w, h)
            frame_surf = sheet_image.subsurface(rect).copy()
            self.frames[name] = frame_surf

            prefix = name.rsplit("_", 1)[0] if "_" in name else name
            if prefix not in self.animations:
                self.animations[prefix] = []
            self.animations[prefix].append(frame_surf)

    def get_frame(self, name: str) -> pygame.Surface | None:
        return self.frames.get(name)

    def get_animation(self, name: str) -> list[pygame.Surface]:
        return self.animations.get(name, [])


class AnimatedSprite:
    def __init__(self, spritesheet: SpriteSheet, default_anim: str = "idle", fps: float = 8.0):
        self.spritesheet = spritesheet
        self.current_anim = default_anim
        self.fps = fps
        self.frame_index = 0.0
        self.loop = True
        self.is_playing = True
        self.on_finish = None

    def play(self, anim_name: str, loop: bool = True, fps: float | None = None, on_finish=None):
        if self.current_anim != anim_name:
            self.current_anim = anim_name
            self.frame_index = 0.0
        self.loop = loop
        if fps is not None:
            self.fps = fps
        self.is_playing = True
        self.on_finish = on_finish

    def update(self, dt: float = 0.016):
        if not self.is_playing:
            return

        frames = self.spritesheet.get_animation(self.current_anim)
        if not frames:
            return

        self.frame_index += self.fps * dt
        if self.frame_index >= len(frames):
            if self.loop:
                self.frame_index %= len(frames)
            else:
                self.frame_index = len(frames) - 1
                self.is_playing = False
                if self.on_finish:
                    self.on_finish()

    def get_current_surface(self) -> pygame.Surface | None:
        frames = self.spritesheet.get_animation(self.current_anim)
        if not frames:
            return None
        idx = int(self.frame_index) % len(frames)
        return frames[idx]

    def render(self, screen: pygame.Surface, x: int, y: int, angle: float = 0.0, scale: float = 1.0):
        surf = self.get_current_surface()
        if not surf:
            return

        if scale != 1.0:
            sw = max(1, int(surf.get_width() * scale))
            sh = max(1, int(surf.get_height() * scale))
            surf = pygame.transform.scale(surf, (sw, sh))

        if angle != 0.0:
            surf = pygame.transform.rotate(surf, angle)

        rect = surf.get_rect(center=(x, y))
        screen.blit(surf, rect)
