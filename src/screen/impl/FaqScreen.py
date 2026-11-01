from __future__ import annotations
import pygame
from screen.Screen import Screen
from screen.components.Panorama import Panorama
from screen.components.MenuButton import MenuButton
from screen.components.Panel import Panel
from screen.components.Label import Label


class FaqScreen(Screen):
    FAQ_ITEMS = [
        {
            "tag": "СЮЖЕТ И КОНЦЕПЦИЯ",
            "color": (78, 201, 176),
            "question": "Что такое ScrapByte и какова цель игры?",
            "answer": (
                "ScrapByte — это научно-фантастическая игра-головоломка в жанре «программируемый дрон». "
                "Вы выступаете в роли инженера-оператора сервисного дрона-утилизатора. "
                "Ваша задача — исследовать заброшенные технологические платформы и очищать секторы "
                "от ценного техногенного мусора: микрочипов, материнских плат и энергоядер."
            ),
        },
        {
            "tag": "УПРАВЛЕНИЕ ДРОНОМ",
            "color": (86, 156, 214),
            "question": "Как управлять дроном через код?",
            "answer": (
                "Дрон выполняет команды, написанные во встроенном редакторе кода:\n"
                "• forward() — перемещение на 1 клетку вперед по курсу\n"
                "• turn_left() — поворот дрона на 90 градусов влево\n"
                "• turn_right() — поворот дрона на 90 градусов вправо\n"
                "• pickup() — сбор ценной детали прямо под дроном\n"
                "• front_is_clear() — проверка: True, если впереди нет барьера или обрыва"
            ),
        },
        {
            "tag": "ПРАВИЛА И ОГРАНИЧЕНИЯ",
            "color": (220, 180, 80),
            "question": "Какие опасности подстерегают на платформе?",
            "answer": (
                "• Защитные барьеры (оранжевые блоки) абсолютно непроходимы — столкновение с ними вызовет ошибку аварии.\n"
                "• Обрывы платформы (пустота космоса): не вылетайте за границы сектора.\n"
                "• Уровень считается успешно завершенным только тогда, когда весь мусор в секторе собран."
            ),
        },
        {
            "tag": "АЛГОРИТМЫ И УСЛОВИЯ",
            "color": (140, 120, 240),
            "question": "Поддерживаются ли циклы и условия?",
            "answer": (
                "Да! Встроенный интерпретатор поддерживает Python-подобные конструкции:\n"
                "• Условия: if front_is_clear(): ... else: ...\n"
                "• Циклы: while front_is_clear(): ...\n"
                "Вы можете сочетать проверки с сенсорами дрона для автоматического прохождения сложных лабиринтов!"
            ),
        },
        {
            "tag": "КАМЕРА И ИНТЕРФЕЙС",
            "color": (245, 160, 60),
            "question": "Как управлять камерой и окном?",
            "answer": (
                "• Навигация по карте: зажмите правую кнопку мыши (ПКМ) и перемещайте мышь (или клавиши стрелок).\n"
                "• Масштабирование: крутите колесико мыши над картой сектора.\n"
                "• Запуск программы дрона: зеленая кнопка (▶) в терминале редактора.\n"
                "• Полноэкранный режим: клавиша F11 или кнопка в Настройках.\n"
                "• Выход / назад: клавиша ESC."
            ),
        },
    ]

    def __init__(self):
        super().__init__()
        self.last_screen_size: tuple[int, int] = (0, 0)
        self.panorama = Panorama(texture_name="background")

        self.panel = self.addWidget(
            Panel(
                x=0,
                y=0,
                width=720,
                height=560,
                bg_color=(20, 23, 30),
                border_color=(45, 50, 64),
                border_radius=14,
                border_width=2,
            )
        )

        self.title_label = self.addWidget(
            Label(x=0, y=0, text="ЧаВо // База Знаний", size=30, color=(220, 180, 80), font_name="Consolas")
        )

        self.subtitle_label = self.addWidget(
            Label(
                x=0,
                y=0,
                text="СПРАВОЧНИК И ИНФОРМАЦИЯ ОБ ИГРЕ SCRAPBYTE",
                size=12,
                color=(120, 135, 155),
                font_name="Consolas",
            )
        )

        self.btn_back = self.addWidget(
            MenuButton(
                icon="icon_back",
                text="Назад в меню",
                accent_color=(244, 75, 86),
                onClick=self.on_back,
                width=260,
                height=46,
                font_size=16,
            )
        )

        self.scroll_y: float = 0.0
        self.max_scroll: float = 0.0
        self.content_rect = pygame.Rect(0, 0, 0, 0)
        self.is_dragging_scrollbar = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0.0

    def _update_layout(self, w: int, h: int):
        panel_w = min(740, max(520, w - 40))
        panel_h = min(580, max(440, h - 40))
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2

        self.panel.setPosition(panel_x, panel_y)
        self.panel.setSize(panel_w, panel_h)

        font_title = self.game.fontManager.getFont("Consolas", 30)
        title_w, _ = font_title.size(self.title_label.text)
        self.title_label.setPosition(panel_x + (panel_w - title_w) // 2, panel_y + 20)

        font_sub = self.game.fontManager.getFont("Consolas", 12)
        sub_w, _ = font_sub.size(self.subtitle_label.text)
        self.subtitle_label.setPosition(panel_x + (panel_w - sub_w) // 2, panel_y + 56)

        btn_y = panel_y + panel_h - 58
        self.btn_back.setPosition(panel_x + (panel_w - self.btn_back.width) // 2, btn_y)

        # Content area for cards
        clip_top = panel_y + 80
        clip_h = btn_y - clip_top - 12
        self.content_rect = pygame.Rect(panel_x + 20, clip_top, panel_w - 40, clip_h)

    def on_back(self):
        from screen.impl.MainMenuScreen import MainMenuScreen
        self.game.openScreen(MainMenuScreen())

    def mouseScrolled(self, mouseX: int, mouseY: int, scrollY: int) -> bool:
        if self.content_rect.collidepoint(mouseX, mouseY):
            self.scroll_y = max(0.0, min(self.max_scroll, self.scroll_y - scrollY * 34))
            return True
        return False

    def keyPressed(self, keyCode: int):
        if keyCode == pygame.K_ESCAPE:
            self.on_back()
            return
        elif keyCode == pygame.K_UP:
            self.scroll_y = max(0.0, self.scroll_y - 40)
        elif keyCode == pygame.K_DOWN:
            self.scroll_y = min(self.max_scroll, self.scroll_y + 40)
        elif keyCode == pygame.K_PAGEUP:
            self.scroll_y = max(0.0, self.scroll_y - 200)
        elif keyCode == pygame.K_PAGEDOWN:
            self.scroll_y = min(self.max_scroll, self.scroll_y + 200)
        super().keyPressed(keyCode)

    def mouseClicked(self, mouseX: int, mouseY: int, button: int) -> bool:
        if button == 1 and self.max_scroll > 0:
            sb_x = self.content_rect.right - 10
            if sb_x <= mouseX <= sb_x + 8 and self.content_rect.top <= mouseY <= self.content_rect.bottom:
                self.is_dragging_scrollbar = True
                self.drag_start_y = mouseY
                self.drag_start_scroll = self.scroll_y
                return True
        return super().mouseClicked(mouseX, mouseY, button)

    def mouseReleased(self, mouseX: int, mouseY: int, button: int) -> bool:
        if button == 1 and self.is_dragging_scrollbar:
            self.is_dragging_scrollbar = False
            return True
        return super().mouseReleased(mouseX, mouseY, button)

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        w, h = screen.get_size()

        if (w, h) != self.last_screen_size:
            self.last_screen_size = (w, h)
            self._update_layout(w, h)

        self.panorama.update(0.016)
        self.panorama.render(screen, mouseX, mouseY)

        # Draw panel and labels first
        super().render(screen, mouseX, mouseY)

        # Handle scrollbar dragging
        if self.is_dragging_scrollbar and self.max_scroll > 0:
            delta_y = mouseY - self.drag_start_y
            track_h = self.content_rect.height
            scroll_ratio = delta_y / max(1, track_h)
            self.scroll_y = max(0.0, min(self.max_scroll, self.drag_start_scroll + scroll_ratio * self.max_scroll))

        # Render FAQ items inside content_rect with clipping
        clip = self.content_rect
        if clip.width <= 0 or clip.height <= 0:
            return

        fm = self.game.fontManager
        font_tag = fm.getFont("Consolas", 11)
        font_q = fm.getFont("Consolas", 15)
        font_a = fm.getFont("Consolas", 13)

        card_w = clip.width - 18 if self.max_scroll > 0 else clip.width
        card_inner_w = card_w - 28

        # Calculate layout and wrap lines
        curr_y = clip.y + 4 - int(self.scroll_y)

        old_clip = screen.get_clip()
        screen.set_clip(clip)

        card_gap = 14
        total_h = 4

        for item in self.FAQ_ITEMS:
            # Word wrap the answer lines
            answer_paragraphs = item["answer"].split("\n")
            wrapped_lines: list[str] = []
            for p in answer_paragraphs:
                if not p:
                    wrapped_lines.append("")
                    continue
                words = p.split(" ")
                cur_line = words[0]
                for word in words[1:]:
                    test = f"{cur_line} {word}"
                    if font_a.size(test)[0] <= card_inner_w:
                        cur_line = test
                    else:
                        wrapped_lines.append(cur_line)
                        cur_line = word
                wrapped_lines.append(cur_line)

            card_h = 32 + 20 + len(wrapped_lines) * 18 + 14
            card_rect = pygame.Rect(clip.x, curr_y, card_w, card_h)

            if card_rect.bottom >= clip.top and card_rect.top <= clip.bottom:
                # Background of card
                pygame.draw.rect(screen, (24, 28, 38), card_rect, border_radius=8)
                pygame.draw.rect(screen, (40, 48, 62), card_rect, width=1, border_radius=8)

                # Tag badge
                tag_surf = font_tag.render(f"// {item['tag']}", True, item["color"])
                screen.blit(tag_surf, (card_rect.x + 14, card_rect.y + 10))

                # Question
                q_surf = font_q.render(item["question"], True, (240, 245, 255))
                screen.blit(q_surf, (card_rect.x + 14, card_rect.y + 28))

                # Divider
                pygame.draw.line(
                    screen,
                    (36, 42, 54),
                    (card_rect.x + 14, card_rect.y + 50),
                    (card_rect.right - 14, card_rect.y + 50),
                    1,
                )

                # Answer lines
                line_y = card_rect.y + 58
                for line in wrapped_lines:
                    if line:
                        color = (130, 210, 190) if line.startswith("•") else (185, 195, 215)
                        a_surf = font_a.render(line, True, color)
                        screen.blit(a_surf, (card_rect.x + 14, line_y))
                    line_y += 18

            curr_y += card_h + card_gap
            total_h += card_h + card_gap

        screen.set_clip(old_clip)

        self.max_scroll = max(0.0, float(total_h - clip.height))
        if self.scroll_y > self.max_scroll:
            self.scroll_y = self.max_scroll

        # Draw scrollbar if content exceeds viewport
        if self.max_scroll > 0:
            track_rect = pygame.Rect(clip.right - 8, clip.top, 6, clip.height)
            pygame.draw.rect(screen, (28, 33, 44), track_rect, border_radius=3)

            thumb_ratio = max(0.12, min(1.0, clip.height / float(total_h)))
            thumb_h = int(clip.height * thumb_ratio)
            scroll_fraction = self.scroll_y / self.max_scroll
            thumb_y = clip.top + int((clip.height - thumb_h) * scroll_fraction)
            thumb_rect = pygame.Rect(clip.right - 8, thumb_y, 6, thumb_h)

            thumb_color = (220, 180, 80) if self.is_dragging_scrollbar else (120, 140, 170)
            pygame.draw.rect(screen, thumb_color, thumb_rect, border_radius=3)
