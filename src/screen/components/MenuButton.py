from __future__ import annotations
import pygame
from screen.components.Widget import Widget


class MenuButton(Widget):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 280,
        height: int = 50,
        text: str = "",
        icon: str = "",
        onClick=None,
        accent_color: tuple[int, int, int] = (78, 201, 176),
        font_size: int = 18,
        is_locked: bool = False,
    ):
        super().__init__(x, y, width, height)
        self.text = text
        self.icon = icon
        self.onClick = onClick
        self.accent_color = accent_color
        self.font_size = font_size
        self.is_locked = is_locked

        self.hover_progress: float = 0.0
        self.is_pressed: bool = False
        self.depth: int = 5
        self._cached_icon_surf: pygame.Surface | None = None
        self._cached_icon_size: int = 0

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        if not self.visible:
            return

        hovered = self.isHovered(mouseX, mouseY) and self.enabled

        target_hover = 1.0 if hovered else 0.0
        self.hover_progress += (target_hover - self.hover_progress) * 0.28

        push_offset = self.depth if (self.is_pressed and hovered) else 0

        base_rect = pygame.Rect(self.x, self.y + self.depth, self.width, self.height - self.depth)
        pygame.draw.rect(screen, (10, 12, 16), base_rect, border_radius=9)
        pygame.draw.rect(screen, (22, 25, 32), base_rect, width=2, border_radius=9)

        cap_h = self.height - self.depth
        cap_y = self.y + push_offset
        cap_rect = pygame.Rect(self.x, cap_y, self.width, cap_h)

        r = int(32 + (46 - 32) * self.hover_progress)
        g = int(36 + (52 - 36) * self.hover_progress)
        b = int(46 + (64 - 46) * self.hover_progress)
        pygame.draw.rect(screen, (r, g, b), cap_rect, border_radius=8)

        hl_r = min(255, int(r * 1.5))
        hl_g = min(255, int(g * 1.5))
        hl_b = min(255, int(b * 1.5))
        if cap_rect.width > 20 and push_offset == 0:
            pygame.draw.line(
                screen,
                (hl_r, hl_g, hl_b),
                (cap_rect.x + 8, cap_rect.y + 2),
                (cap_rect.right - 8, cap_rect.y + 2),
                1,
            )

        if self.hover_progress > 0.02:
            br_r = int(55 + (self.accent_color[0] - 55) * self.hover_progress)
            br_g = int(60 + (self.accent_color[1] - 60) * self.hover_progress)
            br_b = int(72 + (self.accent_color[2] - 72) * self.hover_progress)
            pygame.draw.rect(screen, (br_r, br_g, br_b), cap_rect, width=2, border_radius=8)
        else:
            pygame.draw.rect(screen, (48, 54, 66), cap_rect, width=2, border_radius=8)

        from game.Game import Game
        game = Game.getInstance()

        if not game or not game.fontManager:
            return

        t_r = int(205 + (255 - 205) * self.hover_progress)
        t_g = int(210 + (255 - 210) * self.hover_progress)
        t_b = int(220 + (255 - 220) * self.hover_progress)

        icon_texture = None
        if self.icon and hasattr(game, "textureManager") and game.textureManager:
            tex = game.textureManager.getTexture(self.icon)
            if tex and tex.is_loaded:
                icon_texture = tex

        if icon_texture:
            icon_size = max(18, min(24, int(self.font_size * 1.2)))
            if self._cached_icon_surf is None or self._cached_icon_size != icon_size:
                self._cached_icon_surf = pygame.transform.smoothscale(icon_texture.image, (icon_size, icon_size))
                self._cached_icon_size = icon_size

            i_r = int(self.accent_color[0] * 0.85 + (255 - self.accent_color[0] * 0.85) * self.hover_progress)
            i_g = int(self.accent_color[1] * 0.85 + (255 - self.accent_color[1] * 0.85) * self.hover_progress)
            i_b = int(self.accent_color[2] * 0.85 + (255 - self.accent_color[2] * 0.85) * self.hover_progress)

            tinted_icon = self._cached_icon_surf.copy()
            tinted_icon.fill((i_r, i_g, i_b), special_flags=pygame.BLEND_RGB_MULT)

            shadow_icon = self._cached_icon_surf.copy()
            shadow_icon.fill((10, 12, 16), special_flags=pygame.BLEND_RGB_MULT)

            text_surf = game.fontManager.renderText(
                self.text,
                size=self.font_size,
                color=(t_r, t_g, t_b),
                font_name="Consolas",
            ) if self.text else None

            shadow_text = game.fontManager.renderText(
                self.text,
                size=self.font_size,
                color=(10, 12, 16),
                font_name="Consolas",
            ) if self.text else None

            gap = 10 if text_surf else 0
            text_w = text_surf.get_width() if text_surf else 0
            total_w = icon_size + gap + text_w
            start_x = cap_rect.centerx - total_w // 2

            icon_x = start_x
            icon_y = cap_rect.centery - icon_size // 2

            screen.blit(shadow_icon, (icon_x + 1, icon_y + 1))
            screen.blit(tinted_icon, (icon_x, icon_y))

            if text_surf and shadow_text:
                text_x = start_x + icon_size + gap
                text_y = cap_rect.centery - text_surf.get_height() // 2
                screen.blit(shadow_text, (text_x + 1, text_y + 1))
                screen.blit(text_surf, (text_x, text_y))
        else:
            display_text = f"{self.icon}  {self.text}".strip() if self.icon else self.text
            if display_text:
                shadow_surf = game.fontManager.renderText(
                    display_text,
                    size=self.font_size,
                    color=(10, 12, 16),
                    font_name="Consolas",
                )
                text_surf = game.fontManager.renderText(
                    display_text,
                    size=self.font_size,
                    color=(t_r, t_g, t_b),
                    font_name="Consolas",
                )

                text_rect = text_surf.get_rect(center=cap_rect.center)
                screen.blit(shadow_surf, (text_rect.x + 1, text_rect.y + 1))
                screen.blit(text_surf, text_rect)

        if self.is_locked:
            lx = cap_rect.x + 16
            ly = cap_rect.centery - 7
            pygame.draw.arc(screen, (160, 170, 190), pygame.Rect(lx + 2, ly, 10, 8), 0, 3.14159, 2)
            pygame.draw.rect(screen, (135, 145, 165), (lx, ly + 5, 14, 11), border_radius=2)
            pygame.draw.circle(screen, (24, 28, 38), (lx + 7, ly + 9), 2)
            pygame.draw.line(screen, (24, 28, 38), (lx + 7, ly + 9), (lx + 7, ly + 13), 1)

    def mouseClicked(self, mouseX: int, mouseY: int, button: int) -> bool:
        if not self.visible or not self.enabled:
            return False

        if button == 1 and self.isHovered(mouseX, mouseY):
            self.is_pressed = True
            return True

        return False

    def mouseReleased(self, mouseX: int, mouseY: int, button: int) -> bool:
        if not self.visible or not self.enabled:
            return False

        if self.is_pressed and button == 1:
            self.is_pressed = False
            if self.isHovered(mouseX, mouseY) and self.onClick:
                from sound.SoundManager import SoundManager
                SoundManager.get_instance().play_ui_click()
                self.onClick()
            return True

        self.is_pressed = False
        return False
