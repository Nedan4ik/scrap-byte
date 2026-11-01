from __future__ import annotations
import math
import pygame
from screen.components.Widget import Widget
from coding.ExecutionResult import ExecutionResult


class CodeTab:
    def __init__(self, title: str = "Скрипт 1", content: str = ""):
        self.title = title
        self.lines: list[str] = content.split("\n") if content else [""]
        self.cursor_row: int = 0
        self.cursor_col: int = 0
        self.scroll_row: int = 0
        self.scroll_col: int = 0
        self.selection_start: tuple[int, int] | None = None

    def get_text(self) -> str:
        return "\n".join(self.lines)

    def set_text(self, text: str):
        self.lines = text.split("\n") if text else [""]
        self.cursor_row = min(self.cursor_row, len(self.lines) - 1)
        self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))
        self.clear_selection()

    def has_selection(self) -> bool:
        return self.selection_start is not None and self.selection_start != (self.cursor_row, self.cursor_col)

    def clear_selection(self):
        self.selection_start = None

    def select_all(self):
        self.selection_start = (0, 0)
        self.cursor_row = len(self.lines) - 1
        self.cursor_col = len(self.lines[self.cursor_row])

    def get_selection_range(self) -> tuple[tuple[int, int], tuple[int, int]] | None:
        if not self.has_selection():
            return None
        p1 = self.selection_start
        p2 = (self.cursor_row, self.cursor_col)
        return (p1, p2) if p1 < p2 else (p2, p1)

    def get_selected_text(self) -> str:
        sel = self.get_selection_range()
        if not sel:
            return ""
        (r1, c1), (r2, c2) = sel
        if r1 == r2:
            return self.lines[r1][c1:c2]
        res = [self.lines[r1][c1:]]
        for r in range(r1 + 1, r2):
            res.append(self.lines[r])
        res.append(self.lines[r2][:c2])
        return "\n".join(res)

    def delete_selection(self) -> bool:
        sel = self.get_selection_range()
        if not sel:
            return False
        (r1, c1), (r2, c2) = sel
        prefix = self.lines[r1][:c1]
        suffix = self.lines[r2][c2:]
        del self.lines[r1 : r2 + 1]
        self.lines.insert(r1, prefix + suffix)
        self.cursor_row = r1
        self.cursor_col = c1
        self.clear_selection()
        return True

    def insert_char(self, char: str):
        if self.has_selection():
            self.delete_selection()

        if "\n" in char:
            parts = char.split("\n")
            cur = self.lines[self.cursor_row]
            before = cur[: self.cursor_col]
            after = cur[self.cursor_col :]
            self.lines[self.cursor_row] = before + parts[0]
            for idx in range(1, len(parts)):
                self.lines.insert(self.cursor_row + idx, parts[idx])
            self.cursor_row += len(parts) - 1
            self.lines[self.cursor_row] += after
            self.cursor_col = len(self.lines[self.cursor_row]) - len(after)
            return

        cur = self.lines[self.cursor_row]
        self.lines[self.cursor_row] = cur[: self.cursor_col] + char + cur[self.cursor_col :]
        self.cursor_col += len(char)

    def backspace(self):
        if self.has_selection():
            self.delete_selection()
            return

        if self.cursor_col > 0:
            cur = self.lines[self.cursor_row]
            self.lines[self.cursor_row] = cur[: self.cursor_col - 1] + cur[self.cursor_col :]
            self.cursor_col -= 1
        elif self.cursor_row > 0:
            prev = self.lines[self.cursor_row - 1]
            cur = self.lines.pop(self.cursor_row)
            self.cursor_row -= 1
            self.cursor_col = len(prev)
            self.lines[self.cursor_row] = prev + cur

    def delete(self):
        if self.has_selection():
            self.delete_selection()
            return

        cur = self.lines[self.cursor_row]
        if self.cursor_col < len(cur):
            self.lines[self.cursor_row] = cur[: self.cursor_col] + cur[self.cursor_col + 1 :]
        elif self.cursor_row < len(self.lines) - 1:
            nxt = self.lines.pop(self.cursor_row + 1)
            self.lines[self.cursor_row] += nxt

    def newline(self):
        if self.has_selection():
            self.delete_selection()

        cur = self.lines[self.cursor_row]
        indent_len = len(cur) - len(cur.lstrip(" "))
        before = cur[: self.cursor_col]
        after = cur[self.cursor_col :]
        self.lines[self.cursor_row] = before
        extra_indent = 4 if before.rstrip().endswith(":") else 0
        indent_str = " " * (indent_len + extra_indent)
        self.lines.insert(self.cursor_row + 1, indent_str + after)
        self.cursor_row += 1
        self.cursor_col = len(indent_str)

    def tab(self):
        self.insert_char("    ")

    def move_up(self):
        if self.cursor_row > 0:
            self.cursor_row -= 1
            self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))

    def move_down(self):
        if self.cursor_row < len(self.lines) - 1:
            self.cursor_row += 1
            self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_row]))

    def move_left(self):
        if self.cursor_col > 0:
            self.cursor_col -= 1
        elif self.cursor_row > 0:
            self.cursor_row -= 1
            self.cursor_col = len(self.lines[self.cursor_row])

    def move_right(self):
        if self.cursor_col < len(self.lines[self.cursor_row]):
            self.cursor_col += 1
        elif self.cursor_row < len(self.lines) - 1:
            self.cursor_row += 1
            self.cursor_col = 0

    def move_home(self):
        cur = self.lines[self.cursor_row]
        indent = len(cur) - len(cur.lstrip(" "))
        self.cursor_col = 0 if self.cursor_col == indent else indent

    def move_end(self):
        self.cursor_col = len(self.lines[self.cursor_row])

    def move_word_left(self):
        cur = self.lines[self.cursor_row]
        col = self.cursor_col
        if col == 0:
            if self.cursor_row > 0:
                self.cursor_row -= 1
                self.cursor_col = len(self.lines[self.cursor_row])
            return
        while col > 0 and not (cur[col - 1].isalnum() or cur[col - 1] == "_"):
            col -= 1
        while col > 0 and (cur[col - 1].isalnum() or cur[col - 1] == "_"):
            col -= 1
        self.cursor_col = col

    def move_word_right(self):
        cur = self.lines[self.cursor_row]
        col = self.cursor_col
        n = len(cur)
        if col >= n:
            if self.cursor_row < len(self.lines) - 1:
                self.cursor_row += 1
                self.cursor_col = 0
            return
        while col < n and (cur[col].isalnum() or cur[col] == "_"):
            col += 1
        while col < n and not (cur[col].isalnum() or cur[col] == "_"):
            col += 1
        self.cursor_col = col

    def move_doc_start(self):
        self.cursor_row = 0
        self.cursor_col = 0

    def move_doc_end(self):
        self.cursor_row = len(self.lines) - 1
        self.cursor_col = len(self.lines[self.cursor_row])

    def delete_word_backspace(self):
        if self.has_selection():
            self.delete_selection()
            return
        cur = self.lines[self.cursor_row]
        start_col = self.cursor_col
        if start_col == 0:
            self.backspace()
            return
        col = start_col
        while col > 0 and not (cur[col - 1].isalnum() or cur[col - 1] == "_"):
            col -= 1
        while col > 0 and (cur[col - 1].isalnum() or cur[col - 1] == "_"):
            col -= 1
        self.lines[self.cursor_row] = cur[:col] + cur[start_col:]
        self.cursor_col = col

    def delete_word_delete(self):
        if self.has_selection():
            self.delete_selection()
            return
        cur = self.lines[self.cursor_row]
        start_col = self.cursor_col
        n = len(cur)
        if start_col >= n:
            self.delete()
            return
        col = start_col
        while col < n and (cur[col].isalnum() or cur[col] == "_"):
            col += 1
        while col < n and not (cur[col].isalnum() or cur[col] == "_"):
            col += 1
        self.lines[self.cursor_row] = cur[:start_col] + cur[col:]

    def ensure_cursor_visible(self, visible_rows: int, visible_cols: int):
        if self.cursor_row < self.scroll_row:
            self.scroll_row = self.cursor_row
        elif self.cursor_row >= self.scroll_row + visible_rows:
            self.scroll_row = self.cursor_row - visible_rows + 1

        if self.cursor_col < self.scroll_col:
            self.scroll_col = self.cursor_col
        elif self.cursor_col >= self.scroll_col + visible_cols:
            self.scroll_col = self.cursor_col - visible_cols + 1


class Renderer(Widget):
    KEYWORDS = {
        "def", "class", "if", "elif", "else", "for", "while", "return", "import",
        "from", "in", "and", "or", "not", "try", "except", "pass", "break", "continue",
        "as", "is", "with", "lambda", "yield", "raise", "finally",
    }
    BUILTINS = {
        "forward", "turn_left", "turn_right", "left", "right", "pickup", "pos", "heading", "heading_name",
        "front", "is_air", "is_obstacle", "can_forward", "front_is_obstacle", "front_is_air", "can_pickup", "has_trash",
        "print", "log", "len", "range", "int", "str", "float", "list",
    }
    CONSTANTS = {"True", "False", "None"}

    COLOR_BG = (18, 21, 28)
    COLOR_TAB_BAR = (14, 16, 23)
    COLOR_TAB_ACTIVE = (25, 29, 40)
    COLOR_TAB_INACTIVE = (17, 20, 28)
    COLOR_ACCENT = (78, 201, 176)
    COLOR_GUTTER = (14, 16, 23)
    COLOR_GUTTER_LINE = (32, 37, 50)
    COLOR_GUTTER_TEXT = (90, 100, 120)
    COLOR_CURRENT_LINE = (28, 33, 46)
    COLOR_SELECTION = (38, 79, 130)
    COLOR_STATUS_BG = (13, 15, 21)
    COLOR_BORDER = (46, 54, 72)
    COLOR_CONSOLE_BG = (10, 12, 17)
    COLOR_CONSOLE_HEADER = (14, 16, 23)

    COLOR_TEXT = (222, 230, 242)
    COLOR_KEYWORD = (205, 125, 240)
    COLOR_BUILTIN = (95, 180, 250)
    COLOR_CONST = (225, 160, 100)
    COLOR_STRING = (145, 215, 125)
    COLOR_NUMBER = (245, 205, 115)
    COLOR_COMMENT = (110, 122, 145)

    KEY_MAP = {
        pygame.K_SPACE: " ",
        pygame.K_EXCLAIM: "!",
        pygame.K_QUOTEDBL: '"',
        pygame.K_HASH: "#",
        pygame.K_DOLLAR: "$",
        pygame.K_AMPERSAND: "&",
        pygame.K_QUOTE: "'",
        pygame.K_LEFTPAREN: "(",
        pygame.K_RIGHTPAREN: ")",
        pygame.K_ASTERISK: "*",
        pygame.K_PLUS: "+",
        pygame.K_COMMA: ",",
        pygame.K_MINUS: "-",
        pygame.K_PERIOD: ".",
        pygame.K_SLASH: "/",
        pygame.K_COLON: ":",
        pygame.K_SEMICOLON: ";",
        pygame.K_LESS: "<",
        pygame.K_EQUALS: "=",
        pygame.K_GREATER: ">",
        pygame.K_QUESTION: "?",
        pygame.K_AT: "@",
        pygame.K_LEFTBRACKET: "[",
        pygame.K_BACKSLASH: "\\",
        pygame.K_RIGHTBRACKET: "]",
        pygame.K_CARET: "^",
        pygame.K_UNDERSCORE: "_",
        pygame.K_BACKQUOTE: "`",
    }

    SHIFT_DIGITS = {
        pygame.K_1: "!",
        pygame.K_2: "@",
        pygame.K_3: "#",
        pygame.K_4: "$",
        pygame.K_5: "%",
        pygame.K_6: "^",
        pygame.K_7: "&",
        pygame.K_8: "*",
        pygame.K_9: "(",
        pygame.K_0: ")",
        pygame.K_MINUS: "_",
        pygame.K_EQUALS: "+",
        pygame.K_LEFTBRACKET: "{",
        pygame.K_RIGHTBRACKET: "}",
        pygame.K_SEMICOLON: ":",
        pygame.K_QUOTE: '"',
        pygame.K_COMMA: "<",
        pygame.K_PERIOD: ">",
        pygame.K_SLASH: "?",
    }

    def __init__(
        self,
        x: int = 400,
        y: int = 20,
        width: int = 380,
        height: int = 560,
        interpretator=None,
        level=None,
        on_run=None,
        on_info=None,
        on_layout_change=None,
        on_execution_finish=None,
    ):
        super().__init__(x, y, width, height)
        self.interpretator = interpretator
        self.level = level if level is not None else getattr(interpretator, "level", None)
        self.on_run = on_run
        self.on_info = on_info
        self.on_layout_change = on_layout_change
        self.on_execution_finish = on_execution_finish
        self.custom_layout: bool = False

        try:
            pygame.key.set_repeat(300, 30)
        except Exception:
            pass

        self.tabs: list[CodeTab] = []
        self.active_tab_index: int = 0
        self.add_tab(title="Скрипт 1", content="forward()\nturn_right()\nforward()")

        self.font = None
        self.ui_font = None
        self.char_w = 8
        self.char_h = 14
        self.line_h = 20

        self.gutter_w = 46
        self.tab_bar_h = 32
        self.status_bar_h = 24
        self.grip_size = 18

        self.show_console = False
        self.console_h = 95
        self.console_logs: list[tuple[str, tuple[int, int, int]]] = []
        self.console_scroll = 0

        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.is_resizing = False
        self.resize_start_w = width
        self.resize_start_h = height
        self.resize_start_mx = 0
        self.resize_start_my = 0

        self.is_selecting_text = False
        self.held_key: int | None = None
        self.held_char: str = ""
        self.hold_time: float = 0.0
        self.repeat_time: float = 0.0

        self.cursor_blink_time = 0.0
        self.cursor_visible = True
        self.is_focused = True

        self.status_text = "Готов к работе"
        self.status_color = (150, 160, 180)
        self.is_executing = False
        self._clipboard_buffer = ""
        self.executing_line: int | None = None
        self.executing_tab_index: int | None = None
        self.anim_exec_line: float = 0.0
        self.anim_exec_alpha: float = 0.0
        self.anim_pulse_timer: float = 0.0

        if self.interpretator:
            self.interpretator.on_line_step = self._handle_line_step

    def _init_fonts(self):
        if self.font is None:
            try:
                self.font = pygame.font.SysFont("Consolas", 14, bold=True)
            except Exception:
                self.font = pygame.font.Font(None, 16)
                if hasattr(self.font, "set_bold"):
                    self.font.set_bold(True)
            size = self.font.size("M")
            self.char_w = max(6, size[0])
            self.char_h = max(12, size[1])
            self.line_h = max(18, self.char_h + 5)

        if self.ui_font is None:
            try:
                self.ui_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
            except Exception:
                self.ui_font = pygame.font.Font(None, 14)
                if hasattr(self.ui_font, "set_bold"):
                    self.ui_font.set_bold(True)

    def _set_clipboard(self, text: str):
        self._clipboard_buffer = text
        try:
            if pygame.scrap.get_init():
                pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
        except Exception:
            pass

    def _get_clipboard(self) -> str:
        try:
            if pygame.scrap.get_init():
                raw = pygame.scrap.get(pygame.SCRAP_TEXT)
                if raw:
                    return raw.decode("utf-8", errors="ignore").replace("\x00", "")
        except Exception:
            pass
        return getattr(self, "_clipboard_buffer", "")

    def add_tab(self, title: str | None = None, content: str = "") -> CodeTab:
        if not title:
            title = f"Скрипт {len(self.tabs) + 1}"
        tab = CodeTab(title=title, content=content)
        self.tabs.append(tab)
        self.active_tab_index = len(self.tabs) - 1
        return tab

    def close_tab(self, index: int) -> bool:
        if 0 <= index < len(self.tabs):
            self.tabs.pop(index)
            if not self.tabs:
                self.add_tab()
            elif self.active_tab_index >= len(self.tabs):
                self.active_tab_index = len(self.tabs) - 1
            return True
        return False

    def select_tab(self, index: int):
        if 0 <= index < len(self.tabs):
            self.active_tab_index = index

    def get_current_tab(self) -> CodeTab | None:
        if 0 <= self.active_tab_index < len(self.tabs):
            return self.tabs[self.active_tab_index]
        return None

    def get_current_code(self) -> str:
        tab = self.get_current_tab()
        return tab.get_text() if tab else ""

    def set_current_code(self, code: str):
        tab = self.get_current_tab()
        if tab:
            tab.set_text(code)

    def get_tab_count(self) -> int:
        return len(self.tabs)

    @property
    def info_open(self) -> bool:
        cur = self.get_current_tab()
        return bool(cur and cur.title == "Информация о уровне")

    @info_open.setter
    def info_open(self, val: bool):
        if not val:
            for idx, tab in enumerate(self.tabs):
                if tab.title == "Информация о уровне" and self.active_tab_index == idx:
                    self.select_tab(0)
                    break

    def _notify_layout_change(self):
        self.custom_layout = True
        if self.on_layout_change:
            try:
                self.on_layout_change(self.x, self.y, self.width, self.height)
            except Exception:
                pass

    def to_dict(self) -> dict:
        return {
            "x": int(self.x),
            "y": int(self.y),
            "w": int(self.width),
            "h": int(self.height),
            "custom_layout": getattr(self, "custom_layout", False),
            "tabs": [
                {"title": t.title, "content": t.get_text()}
                for t in self.tabs
            ],
            "active_tab": self.active_tab_index,
        }

    def load_dict(self, data: dict):
        if not isinstance(data, dict):
            return
        if "x" in data and "y" in data:
            self.setPosition(int(data["x"]), int(data["y"]))
        if "w" in data and "h" in data:
            self.setSize(int(data["w"]), int(data["h"]))
        if "custom_layout" in data:
            self.custom_layout = bool(data["custom_layout"])
        if "tabs" in data and data["tabs"]:
            self.tabs = [CodeTab(title=t.get("title", "Скрипт 1"), content=t.get("content", "")) for t in data["tabs"]]
            self.active_tab_index = min(max(0, data.get("active_tab", 0)), len(self.tabs) - 1)

    def set_status(self, text: str, color: tuple[int, int, int] = (150, 160, 180)):
        self.status_text = text
        self.status_color = color

    def show_level_info(self):
        target_title = "Информация о уровне"
        for idx, tab in enumerate(self.tabs):
            if tab.title == target_title:
                self.select_tab(idx)
                return

        lvl = self.level
        if not lvl and self.interpretator and hasattr(self.interpretator, "level"):
            lvl = self.interpretator.level

        content = ""
        if lvl:
            if hasattr(lvl, "get_level_info"):
                content = lvl.get_level_info()
            elif hasattr(lvl, "info"):
                content = str(lvl.info)

        if not content:
            content = "Информация о уровне отсутствует."

        self.add_tab(title=target_title, content=content)

    def toggle_info(self):
        self.show_level_info()
        if self.on_info:
            self.on_info()

    def run_code(self):
        if self.is_executing:
            return

        from sound.SoundManager import SoundManager
        SoundManager.get_instance().play_ui_click()

        tab = self.get_current_tab()
        if not tab:
            return

        code = tab.get_text()
        self.show_console = True
        self.console_logs.append(("▶ [Запуск скрипта...]", (78, 201, 176)))

        if self.on_run:
            self.on_run(code)

        if self.interpretator:
            self.is_executing = True
            self.executing_tab_index = self.active_tab_index
            self.executing_line = 0
            self.anim_exec_alpha = 0.0
            self.anim_exec_line = 0.0
            self.interpretator.on_line_step = self._handle_line_step
            self.set_status("Выполняется...", (241, 196, 15))

            def _on_finish(result: ExecutionResult):
                self.is_executing = False
                self.executing_line = None
                self.executing_tab_index = None
                if self.interpretator:
                    self.interpretator.on_line_step = None
                if result.output:
                    for l in result.output.strip().split("\n"):
                        if l:
                            self.console_logs.append((l, (212, 220, 235)))

                if result.success:
                    self.set_status("Успешно выполнено", (78, 201, 176))
                    self.console_logs.append(("✔ [Завершено успешно]", (78, 201, 176)))
                else:
                    err = str(result.error) if result.error else "Неизвестная ошибка"
                    if len(err) > 36:
                        short_err = err[:33] + "..."
                    else:
                        short_err = err
                    self.set_status(f"Ошибка: {short_err}", (244, 71, 71))
                    self.console_logs.append((f"✖ [Ошибка]: {err}", (244, 71, 71)))

                vis_lines = max(1, (self.console_h - 22) // 16)
                self.console_scroll = max(0, len(self.console_logs) - vis_lines)

                if self.on_execution_finish:
                    try:
                        self.on_execution_finish(result)
                    except Exception:
                        pass

            self.interpretator.run_async(code, on_complete=_on_finish)
        else:
            self.set_status("Скрипт отправлен", (78, 201, 176))
            self.console_logs.append(("✔ [Скрипт отправлен]", (78, 201, 176)))
            if self.on_execution_finish:
                try:
                    self.on_execution_finish(ExecutionResult(True, "", None, None))
                except Exception:
                    pass

    def _handle_line_step(self, line_no: int | None):
        self.executing_line = line_no
        if line_no is not None:
            if self.anim_exec_alpha < 0.08:
                self.anim_exec_line = float(line_no)
            tab = self.get_current_tab()
            if tab and self.active_tab_index == getattr(self, "executing_tab_index", self.active_tab_index):
                con_h = self.console_h if self.show_console else 0
                editor_h = self.height - self.tab_bar_h - self.status_bar_h - con_h
                visible_rows = max(1, editor_h // self.line_h)
                if line_no < tab.scroll_row:
                    tab.scroll_row = line_no
                elif line_no >= tab.scroll_row + visible_rows - 1:
                    tab.scroll_row = max(0, line_no - visible_rows + 2)

    @classmethod
    def highlight_line(cls, line: str) -> list[tuple[str, tuple[int, int, int]]]:
        if not line:
            return []
        tokens: list[tuple[str, tuple[int, int, int]]] = []
        idx = 0
        n = len(line)
        while idx < n:
            ch = line[idx]
            if ch == "#":
                tokens.append((line[idx:], cls.COLOR_COMMENT))
                break
            if ch in ("'", '"'):
                quote = ch
                start = idx
                idx += 1
                while idx < n and line[idx] != quote:
                    if line[idx] == "\\" and idx + 1 < n:
                        idx += 2
                    else:
                        idx += 1
                if idx < n:
                    idx += 1
                tokens.append((line[start:idx], cls.COLOR_STRING))
                continue
            if ch.isdigit():
                start = idx
                while idx < n and (line[idx].isdigit() or line[idx] == "."):
                    idx += 1
                tokens.append((line[start:idx], cls.COLOR_NUMBER))
                continue
            if ch.isalpha() or ch == "_":
                start = idx
                while idx < n and (line[idx].isalnum() or line[idx] == "_"):
                    idx += 1
                word = line[start:idx]
                if word in cls.KEYWORDS:
                    col = cls.COLOR_KEYWORD
                elif word in cls.BUILTINS:
                    col = cls.COLOR_BUILTIN
                elif word in cls.CONSTANTS:
                    col = cls.COLOR_CONST
                else:
                    col = cls.COLOR_TEXT
                tokens.append((word, col))
                continue
            start = idx
            while idx < n and not (line[idx].isalnum() or line[idx] in ("_", "#", "'", '"')):
                idx += 1
            tokens.append((line[start:idx], cls.COLOR_TEXT))
        return tokens

    def _get_title_bar_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.tab_bar_h)

    def _get_run_button_rect(self) -> pygame.Rect:
        btn_w = 26
        btn_h = 24
        bx = self.x + self.width - btn_w - 32 - 6
        by = self.y + (self.tab_bar_h - btn_h) // 2
        return pygame.Rect(bx, by, btn_w, btn_h)

    def _get_info_button_rect(self) -> pygame.Rect:
        btn_w = 26
        btn_h = 24
        bx = self.x + self.width - btn_w - 6
        by = self.y + (self.tab_bar_h - btn_h) // 2
        return pygame.Rect(bx, by, btn_w, btn_h)

    def _get_resize_grip_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x + self.width - self.grip_size,
            self.y + self.height - self.grip_size,
            self.grip_size,
            self.grip_size,
        )

    def _get_add_tab_rect(self, current_tabs_width: int) -> pygame.Rect:
        ax = self.x + 6 + current_tabs_width
        ay = self.y + (self.tab_bar_h - 22) // 2
        return pygame.Rect(ax, ay, 22, 22)

    def _get_tab_rects(self) -> list[tuple[pygame.Rect, pygame.Rect]]:
        rects = []
        cur_x = self.x + 6
        tab_y = self.y + 3
        tab_h = self.tab_bar_h - 3
        for tab in self.tabs:
            title_len = len(tab.title)
            tab_w = max(86, title_len * 9 + 30)
            tab_rect = pygame.Rect(cur_x, tab_y, tab_w, tab_h)
            close_rect = pygame.Rect(cur_x + tab_w - 18, tab_y + (tab_h - 14) // 2, 14, 14)
            rects.append((tab_rect, close_rect))
            cur_x += tab_w + 3
        return rects

    def _get_console_rect(self) -> pygame.Rect:
        top = self.y + self.height - self.status_bar_h - self.console_h
        return pygame.Rect(self.x, top, self.width, self.console_h)

    def _get_console_close_rect(self) -> pygame.Rect:
        top = self.y + self.height - self.status_bar_h - self.console_h
        return pygame.Rect(self.x + self.width - 20, top + 3, 14, 14)

    def _get_console_clear_rect(self) -> pygame.Rect:
        top = self.y + self.height - self.status_bar_h - self.console_h
        return pygame.Rect(self.x + self.width - 42, top + 3, 16, 14)

    def _update_cursor(self, mouseX: int, mouseY: int):
        try:
            if not self.visible:
                return

            if self.is_resizing or self._get_resize_grip_rect().collidepoint(mouseX, mouseY):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
                return

            if self.is_dragging:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
                return

            if not self.isHovered(mouseX, mouseY):
                return

            if (
                self._get_run_button_rect().collidepoint(mouseX, mouseY)
                or self._get_info_button_rect().collidepoint(mouseX, mouseY)
            ):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                return

            if self.show_console:
                if (
                    self._get_console_close_rect().collidepoint(mouseX, mouseY)
                    or self._get_console_clear_rect().collidepoint(mouseX, mouseY)
                ):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    return

            tab_rects = self._get_tab_rects()
            tot_tab_w = sum(tr[0].width + 3 for tr in tab_rects)
            if self._get_add_tab_rect(tot_tab_w).collidepoint(mouseX, mouseY):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                return

            for tr, cr in tab_rects:
                if tr.collidepoint(mouseX, mouseY):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    return

            con_h = self.console_h if self.show_console else 0
            editor_top = self.y + self.tab_bar_h
            editor_h = self.height - self.tab_bar_h - self.status_bar_h - con_h
            code_x = self.x + self.gutter_w
            code_rect = pygame.Rect(code_x, editor_top, self.width - self.gutter_w, editor_h)
            if code_rect.collidepoint(mouseX, mouseY):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                return

            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except Exception:
            pass

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        if not self.visible:
            return

        self._init_fonts()
        dt = 0.016

        self._update_cursor(mouseX, mouseY)

        if self.is_dragging:
            pressed = pygame.mouse.get_pressed()
            if not pressed[0]:
                self.is_dragging = False
                self._notify_layout_change()
            else:
                cur_mx, cur_my = pygame.mouse.get_pos()
                self.x = cur_mx - self.drag_offset_x
                self.y = cur_my - self.drag_offset_y

        if self.is_resizing:
            pressed = pygame.mouse.get_pressed()
            if not pressed[0]:
                self.is_resizing = False
                self._notify_layout_change()
            else:
                cur_mx, cur_my = pygame.mouse.get_pos()
                min_h = 240 if self.show_console else 190
                self.width = max(300, self.resize_start_w + (cur_mx - self.resize_start_mx))
                self.height = max(min_h, self.resize_start_h + (cur_my - self.resize_start_my))

        if self.is_focused and self.held_key is not None:
            self.hold_time += dt
            if self.hold_time >= 0.30:
                self.repeat_time += dt
                if self.repeat_time >= 0.03:
                    self.repeat_time = 0.0
                    self._process_key(self.held_key, self.held_char)

        self.cursor_blink_time += dt
        if self.cursor_blink_time >= 0.5:
            self.cursor_blink_time = 0.0
            self.cursor_visible = not self.cursor_visible

        self.anim_pulse_timer += dt * 4.5
        if self.is_executing and self.executing_line is not None:
            target_line = float(self.executing_line)
            self.anim_exec_line += (target_line - self.anim_exec_line) * min(1.0, 14.0 * dt)
            self.anim_exec_alpha += (1.0 - self.anim_exec_alpha) * min(1.0, 10.0 * dt)
        else:
            self.anim_exec_alpha += (0.0 - self.anim_exec_alpha) * min(1.0, 8.0 * dt)
            if self.anim_exec_alpha < 0.005:
                self.anim_exec_alpha = 0.0

        tab = self.get_current_tab()
        con_h = self.console_h if self.show_console else 0
        editor_top = self.y + self.tab_bar_h
        editor_h = self.height - self.tab_bar_h - self.status_bar_h - con_h
        editor_bottom = editor_top + editor_h
        code_x = self.x + self.gutter_w
        code_w = self.width - self.gutter_w

        if self.is_selecting_text and tab:
            pressed = pygame.mouse.get_pressed()
            if not pressed[0]:
                self.is_selecting_text = False
                if tab.selection_start == (tab.cursor_row, tab.cursor_col):
                    tab.clear_selection()
            else:
                cur_mx, cur_my = pygame.mouse.get_pos()
                drag_row = tab.scroll_row + (cur_my - editor_top) // self.line_h
                drag_col = tab.scroll_col + max(0, (cur_mx - code_x - 8) // self.char_w)
                tab.cursor_row = max(0, min(len(tab.lines) - 1, drag_row))
                tab.cursor_col = max(0, min(len(tab.lines[tab.cursor_row]), drag_col))

        visible_rows = max(1, editor_h // self.line_h)
        visible_cols = max(1, code_w // self.char_w)
        if tab:
            tab.ensure_cursor_visible(visible_rows, visible_cols)

        pygame.draw.rect(screen, (8, 10, 14), (self.x + 3, self.y + 3, self.width, self.height), border_radius=10)
        pygame.draw.rect(screen, self.COLOR_BG, (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(screen, self.COLOR_TAB_BAR, (self.x, self.y, self.width, self.tab_bar_h), border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.rect(screen, self.COLOR_BORDER, (self.x, self.y, self.width, self.height), width=1, border_radius=8)
        pygame.draw.line(screen, (28, 32, 44), (self.x, editor_top), (self.x + self.width, editor_top))

        tab_rects = self._get_tab_rects()
        tot_tab_w = sum(tr[0].width + 3 for tr in tab_rects)

        for idx, ((tab_rect, close_rect), t) in enumerate(zip(tab_rects, self.tabs)):
            is_active = idx == self.active_tab_index
            bg_col = self.COLOR_TAB_ACTIVE if is_active else self.COLOR_TAB_INACTIVE
            pygame.draw.rect(screen, bg_col, tab_rect, border_top_left_radius=6, border_top_right_radius=6)

            if is_active:
                pygame.draw.line(screen, self.COLOR_ACCENT, (tab_rect.x, tab_rect.y), (tab_rect.right - 1, tab_rect.y), 2)

            t_col = (255, 255, 255) if is_active else (145, 155, 175)
            rendered_title = self.ui_font.render(t.title, True, t_col)
            screen.blit(rendered_title, (tab_rect.x + 8, tab_rect.y + 6))

            hover_close = close_rect.collidepoint(mouseX, mouseY)
            ccx, ccy = close_rect.centerx, close_rect.centery
            c_col = (245, 80, 80) if hover_close else (115, 125, 145)
            pygame.draw.line(screen, c_col, (ccx - 3, ccy - 3), (ccx + 3, ccy + 3), 2)
            pygame.draw.line(screen, c_col, (ccx + 3, ccy - 3), (ccx - 3, ccy + 3), 2)

        add_rect = self._get_add_tab_rect(tot_tab_w)
        hover_add = add_rect.collidepoint(mouseX, mouseY)
        add_bg = (45, 52, 68) if hover_add else (28, 33, 44)
        pygame.draw.rect(screen, add_bg, add_rect, border_radius=4)
        pygame.draw.rect(screen, (55, 65, 85), add_rect, width=1, border_radius=4)
        acx, acy = add_rect.centerx, add_rect.centery
        plus_col = (230, 240, 255) if hover_add else (170, 185, 205)
        pygame.draw.line(screen, plus_col, (acx - 4, acy), (acx + 4, acy), 2)
        pygame.draw.line(screen, plus_col, (acx, acy - 4), (acx, acy + 4), 2)

        run_rect = self._get_run_button_rect()
        hover_run = run_rect.collidepoint(mouseX, mouseY)
        if self.is_executing:
            run_bg = (215, 145, 20)
            run_border = (255, 185, 50)
        else:
            run_bg = (45, 175, 80) if hover_run else (35, 145, 68)
            run_border = (65, 205, 105) if hover_run else (45, 165, 78)

        pygame.draw.rect(screen, run_bg, run_rect, border_radius=5)
        pygame.draw.rect(screen, run_border, run_rect, width=1, border_radius=5)
        rcx, rcy = run_rect.centerx, run_rect.centery
        if self.is_executing:
            pygame.draw.rect(screen, (255, 255, 255), (rcx - 4, rcy - 4, 8, 8), border_radius=1)
        else:
            tri = [(rcx - 4, rcy - 5), (rcx - 4, rcy + 5), (rcx + 5, rcy)]
            pygame.draw.polygon(screen, (255, 255, 255), tri)

        info_rect = self._get_info_button_rect()
        hover_info = info_rect.collidepoint(mouseX, mouseY)
        info_bg = (45, 115, 195) if hover_info else (32, 90, 160)
        info_border = (65, 145, 235) if hover_info else (45, 110, 190)
        pygame.draw.rect(screen, info_bg, info_rect, border_radius=5)
        pygame.draw.rect(screen, info_border, info_rect, width=1, border_radius=5)
        icx, icy = info_rect.centerx, info_rect.centery
        pygame.draw.circle(screen, (255, 255, 255), (icx, icy), 7, width=1)
        screen.set_at((icx, icy - 3), (255, 255, 255))
        screen.set_at((icx, icy - 4), (255, 255, 255))
        pygame.draw.line(screen, (255, 255, 255), (icx, icy - 1), (icx, icy + 3), 2)

        pygame.draw.rect(screen, self.COLOR_GUTTER, (self.x, editor_top, self.gutter_w, editor_h))
        pygame.draw.line(screen, self.COLOR_GUTTER_LINE, (code_x, editor_top), (code_x, editor_bottom))

        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(self.x, editor_top, self.width, editor_h))

        if tab:
            start_row = tab.scroll_row
            end_row = min(len(tab.lines), start_row + visible_rows + 1)
            sel_range = tab.get_selection_range()

            is_exec_tab = getattr(self, "executing_tab_index", None) in (None, self.active_tab_index)
            if is_exec_tab and self.anim_exec_alpha > 0.01:
                exec_y = editor_top + (self.anim_exec_line - tab.scroll_row) * self.line_h
                pulse = 0.88 + 0.12 * math.sin(self.anim_pulse_timer)
                bar_alpha = int(self.anim_exec_alpha * 55 * pulse)
                if bar_alpha > 0 and editor_top - self.line_h <= exec_y <= editor_bottom:
                    hl_surf = pygame.Surface((code_w, self.line_h), pygame.SRCALPHA)
                    hl_surf.fill((78, 201, 176, bar_alpha))
                    top_alpha = int(self.anim_exec_alpha * 135 * pulse)
                    bot_alpha = int(self.anim_exec_alpha * 70 * pulse)
                    pygame.draw.line(hl_surf, (78, 201, 176, top_alpha), (0, 0), (code_w, 0), 1)
                    pygame.draw.line(hl_surf, (78, 201, 176, bot_alpha), (0, self.line_h - 1), (code_w, self.line_h - 1), 1)
                    screen.blit(hl_surf, (code_x, int(round(exec_y))))

                    ind_surf = pygame.Surface((3, self.line_h), pygame.SRCALPHA)
                    ind_surf.fill((78, 201, 176, int(self.anim_exec_alpha * 245 * pulse)))
                    screen.blit(ind_surf, (code_x, int(round(exec_y))))

                arrow_alpha = int(self.anim_exec_alpha * 240 * pulse)
                if arrow_alpha > 0 and editor_top - self.line_h <= exec_y <= editor_bottom:
                    arrow_surf = pygame.Surface((12, self.line_h), pygame.SRCALPHA)
                    ay = self.line_h / 2.0
                    pygame.draw.polygon(arrow_surf, (78, 201, 176, arrow_alpha), [(1, int(ay - 4)), (8, int(ay)), (1, int(ay + 4))])
                    screen.blit(arrow_surf, (code_x - 12, int(round(exec_y))))

            for r_idx in range(start_row, end_row):
                ly = editor_top + (r_idx - start_row) * self.line_h

                if r_idx == tab.cursor_row and self.is_focused:
                    pygame.draw.rect(screen, self.COLOR_CURRENT_LINE, (code_x, ly, code_w, self.line_h))

                if sel_range:
                    (r1, c1), (r2, c2) = sel_range
                    if r1 <= r_idx <= r2:
                        line_len = len(tab.lines[r_idx])
                        if r1 == r2:
                            sc1, sc2 = c1, c2
                        elif r_idx == r1:
                            sc1, sc2 = c1, line_len + 1
                        elif r_idx == r2:
                            sc1, sc2 = 0, c2
                        else:
                            sc1, sc2 = 0, line_len + 1

                        if sc2 > tab.scroll_col:
                            sx1 = code_x + 8 + max(0, sc1 - tab.scroll_col) * self.char_w
                            sx2 = code_x + 8 + max(0, sc2 - tab.scroll_col) * self.char_w
                            sel_w = max(4, sx2 - sx1)
                            pygame.draw.rect(screen, self.COLOR_SELECTION, (sx1, ly, sel_w, self.line_h))

                num_str = str(r_idx + 1)
                is_active_exec = is_exec_tab and self.anim_exec_alpha > 0.3 and abs(r_idx - self.anim_exec_line) < 0.6
                if is_active_exec:
                    num_col = (110, 240, 215)
                elif r_idx == tab.cursor_row:
                    num_col = self.COLOR_ACCENT
                else:
                    num_col = self.COLOR_GUTTER_TEXT
                num_surf = self.font.render(num_str, True, num_col)
                num_x = code_x - 8 - num_surf.get_width()
                screen.blit(num_surf, (num_x, ly + 2))

                line_text = tab.lines[r_idx]
                tokens = self.highlight_line(line_text)
                cur_col = 0
                for tok_text, tok_col in tokens:
                    col_end = cur_col + len(tok_text)
                    if col_end > tab.scroll_col:
                        vis_start = max(0, tab.scroll_col - cur_col)
                        draw_substr = tok_text[vis_start:]
                        tx = code_x + 8 + (cur_col + vis_start - tab.scroll_col) * self.char_w
                        tsurf = self.font.render(draw_substr, True, tok_col)
                        screen.blit(tsurf, (tx, ly + 2))
                    cur_col = col_end

            if self.is_focused and self.cursor_visible:
                cx = code_x + 8 + (tab.cursor_col - tab.scroll_col) * self.char_w
                cy = editor_top + (tab.cursor_row - tab.scroll_row) * self.line_h
                if editor_top <= cy < editor_bottom:
                    pygame.draw.line(screen, (255, 255, 255), (cx, cy + 2), (cx, cy + self.line_h - 2), 2)

        screen.set_clip(old_clip)

        if self.show_console:
            self._render_console(screen, mouseX, mouseY)

        status_y = self.y + self.height - self.status_bar_h
        pygame.draw.rect(
            screen,
            self.COLOR_STATUS_BG,
            (self.x, status_y, self.width, self.status_bar_h),
            border_bottom_left_radius=8,
            border_bottom_right_radius=8,
        )
        pygame.draw.line(screen, (32, 36, 48), (self.x, status_y), (self.x + self.width, status_y))

        st_dot_col = (78, 201, 176) if not self.is_executing else (241, 196, 15)
        pygame.draw.circle(screen, st_dot_col, (self.x + 14, status_y + self.status_bar_h // 2), 3)
        st_surf = self.ui_font.render(self.status_text, True, self.status_color)
        screen.blit(st_surf, (self.x + 24, status_y + 4))

        if tab:
            pos_info = f"Стр {tab.cursor_row + 1}, Кол {tab.cursor_col + 1}"
            pos_surf = self.ui_font.render(pos_info, True, (130, 140, 160))
            screen.blit(pos_surf, (self.x + self.width - pos_surf.get_width() - 26, status_y + 4))

        grip_rect = self._get_resize_grip_rect()
        hover_grip = grip_rect.collidepoint(mouseX, mouseY) or self.is_resizing
        g_col = self.COLOR_ACCENT if hover_grip else (80, 92, 115)
        gx = self.x + self.width - 4
        gy = self.y + self.height - 4
        for off in (12, 8, 4):
            pygame.draw.line(screen, g_col, (gx - off, gy), (gx, gy - off), 1)

    def _render_console(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        con_rect = self._get_console_rect()
        pygame.draw.rect(screen, self.COLOR_CONSOLE_BG, con_rect)
        pygame.draw.line(screen, (38, 44, 58), (con_rect.x, con_rect.y), (con_rect.right, con_rect.y))

        con_header_h = 20
        pygame.draw.rect(screen, self.COLOR_CONSOLE_HEADER, (con_rect.x, con_rect.y, con_rect.w, con_header_h))
        pygame.draw.line(screen, (28, 33, 44), (con_rect.x, con_rect.y + con_header_h), (con_rect.right, con_rect.y + con_header_h))

        lbl = self.ui_font.render("КОНСОЛЬ ВЫВОДА", True, (120, 135, 160))
        screen.blit(lbl, (con_rect.x + 8, con_rect.y + 2))

        clr_rect = self._get_console_clear_rect()
        h_clr = clr_rect.collidepoint(mouseX, mouseY)
        clr_col = (200, 210, 230) if h_clr else (120, 130, 150)
        clr_surf = self.ui_font.render("⌫", True, clr_col)
        screen.blit(clr_surf, (clr_rect.x, clr_rect.y - 1))

        close_rect = self._get_console_close_rect()
        h_close = close_rect.collidepoint(mouseX, mouseY)
        c_col = (245, 80, 80) if h_close else (120, 130, 150)
        c_surf = self.ui_font.render("×", True, c_col)
        screen.blit(c_surf, (close_rect.x + 2, close_rect.y - 2))

        out_y = con_rect.y + con_header_h + 3
        out_h = con_rect.h - con_header_h - 4
        old_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(con_rect.x, out_y, con_rect.w, out_h))

        line_h = 16
        vis_lines = max(1, out_h // line_h)
        start_idx = max(0, min(self.console_scroll, len(self.console_logs) - 1)) if self.console_logs else 0
        end_idx = min(len(self.console_logs), start_idx + vis_lines + 1)

        for i in range(start_idx, end_idx):
            txt, col = self.console_logs[i]
            ly = out_y + (i - start_idx) * line_h
            surf = self.ui_font.render(txt, True, col)
            screen.blit(surf, (con_rect.x + 8, ly))

        screen.set_clip(old_clip)

    def mouseClicked(self, mouseX: int, mouseY: int, button: int) -> bool:
        if not self.visible or not self.enabled:
            return False

        if not self.isHovered(mouseX, mouseY):
            self.is_focused = False
            return False

        self.is_focused = True

        mods = pygame.key.get_mods()
        ctrl = bool(mods & pygame.KMOD_CTRL)

        if button == 1 and (ctrl or self._get_resize_grip_rect().collidepoint(mouseX, mouseY)):
            if self._get_resize_grip_rect().collidepoint(mouseX, mouseY):
                self.is_resizing = True
                self.resize_start_w = self.width
                self.resize_start_h = self.height
                self.resize_start_mx = mouseX
                self.resize_start_my = mouseY
                return True
            if ctrl:
                self.is_dragging = True
                self.drag_offset_x = mouseX - self.x
                self.drag_offset_y = mouseY - self.y
                return True

        if self.show_console:
            if self._get_console_close_rect().collidepoint(mouseX, mouseY):
                self.show_console = False
                return True
            if self._get_console_clear_rect().collidepoint(mouseX, mouseY):
                self.console_logs.clear()
                self.console_scroll = 0
                return True

        if self._get_run_button_rect().collidepoint(mouseX, mouseY):
            self.run_code()
            return True

        if self._get_info_button_rect().collidepoint(mouseX, mouseY):
            self.toggle_info()
            return True

        tab_rects = self._get_tab_rects()
        tot_tab_w = sum(tr[0].width + 3 for tr in tab_rects)

        if self._get_add_tab_rect(tot_tab_w).collidepoint(mouseX, mouseY):
            self.add_tab()
            return True

        for idx, (tab_rect, close_rect) in enumerate(tab_rects):
            if close_rect.collidepoint(mouseX, mouseY):
                self.close_tab(idx)
                return True
            if tab_rect.collidepoint(mouseX, mouseY):
                self.select_tab(idx)
                return True

        if button == 1 and mouseY < self.y + self.tab_bar_h:
            self.is_dragging = True
            self.drag_offset_x = mouseX - self.x
            self.drag_offset_y = mouseY - self.y
            return True

        con_h = self.console_h if self.show_console else 0
        editor_top = self.y + self.tab_bar_h
        editor_h = self.height - self.tab_bar_h - self.status_bar_h - con_h
        code_x = self.x + self.gutter_w

        if editor_top <= mouseY < editor_top + editor_h and self.x <= mouseX < self.x + self.width:
            tab = self.get_current_tab()
            if tab:
                click_row = tab.scroll_row + (mouseY - editor_top) // self.line_h
                click_col = tab.scroll_col + max(0, (mouseX - code_x - 8) // self.char_w)
                click_row = max(0, min(len(tab.lines) - 1, click_row))
                click_col = max(0, min(len(tab.lines[click_row]), click_col))

                if mods & pygame.KMOD_SHIFT:
                    if tab.selection_start is None:
                        tab.selection_start = (tab.cursor_row, tab.cursor_col)
                else:
                    tab.selection_start = (click_row, click_col)
                    self.is_selecting_text = True

                tab.cursor_row = click_row
                tab.cursor_col = click_col
                self.cursor_blink_time = 0.0
                self.cursor_visible = True
            return True

        return True

    def mouseReleased(self, mouseX: int, mouseY: int, button: int) -> bool:
        if button == 1:
            was_drag_or_resize = self.is_dragging or self.is_resizing
            self.is_dragging = False
            self.is_resizing = False
            self.is_selecting_text = False
            tab = self.get_current_tab()
            if tab and tab.selection_start == (tab.cursor_row, tab.cursor_col):
                tab.clear_selection()
            if was_drag_or_resize:
                self._notify_layout_change()
        self._update_cursor(mouseX, mouseY)
        return super().mouseReleased(mouseX, mouseY, button)

    def mouseScrolled(self, mouseX: int, mouseY: int, scrollY: int) -> bool:
        if not self.visible or not self.enabled or not self.isHovered(mouseX, mouseY):
            return False

        if self.show_console and self._get_console_rect().collidepoint(mouseX, mouseY):
            self.console_scroll = max(0, min(len(self.console_logs) - 1, self.console_scroll - scrollY * 2))
            return True

        tab = self.get_current_tab()
        if tab:
            tab.scroll_row = max(0, min(len(tab.lines) - 1, tab.scroll_row - scrollY * 3))
            return True
        return False

    def keyReleased(self, keyCode: int) -> bool:
        if self.held_key == keyCode:
            self.held_key = None
            self.held_char = ""
        return super().keyReleased(keyCode)

    def _process_key(self, keyCode: int, char: str = "") -> bool:
        tab = self.get_current_tab()
        if not tab:
            return False

        self.cursor_blink_time = 0.0
        self.cursor_visible = True

        mods = pygame.key.get_mods()
        ctrl = bool(mods & pygame.KMOD_CTRL)
        shift = bool(mods & (pygame.KMOD_SHIFT | pygame.KMOD_CAPS))

        if ctrl:
            if keyCode in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.run_code()
                return True
            if keyCode == pygame.K_t:
                self.add_tab()
                return True
            if keyCode == pygame.K_w:
                self.close_tab(self.active_tab_index)
                return True
            if keyCode == pygame.K_i:
                self.toggle_info()
                return True
            if keyCode == pygame.K_a:
                tab.select_all()
                return True
            if keyCode == pygame.K_c:
                if tab.has_selection():
                    self._set_clipboard(tab.get_selected_text())
                return True
            if keyCode == pygame.K_x:
                if tab.has_selection():
                    self._set_clipboard(tab.get_selected_text())
                    tab.delete_selection()
                return True
            if keyCode == pygame.K_v:
                clip = self._get_clipboard()
                if clip:
                    tab.insert_char(clip)
                return True
            if keyCode == pygame.K_LEFT:
                if shift and tab.selection_start is None:
                    tab.selection_start = (tab.cursor_row, tab.cursor_col)
                elif not shift:
                    tab.clear_selection()
                tab.move_word_left()
                return True
            if keyCode == pygame.K_RIGHT:
                if shift and tab.selection_start is None:
                    tab.selection_start = (tab.cursor_row, tab.cursor_col)
                elif not shift:
                    tab.clear_selection()
                tab.move_word_right()
                return True
            if keyCode == pygame.K_HOME:
                if shift and tab.selection_start is None:
                    tab.selection_start = (tab.cursor_row, tab.cursor_col)
                elif not shift:
                    tab.clear_selection()
                tab.move_doc_start()
                return True
            if keyCode == pygame.K_END:
                if shift and tab.selection_start is None:
                    tab.selection_start = (tab.cursor_row, tab.cursor_col)
                elif not shift:
                    tab.clear_selection()
                tab.move_doc_end()
                return True
            if keyCode == pygame.K_BACKSPACE:
                tab.delete_word_backspace()
                return True
            if keyCode == pygame.K_DELETE:
                tab.delete_word_delete()
                return True
            if keyCode == pygame.K_UP:
                tab.move_up()
                tab.scroll_row = max(0, tab.scroll_row - 1)
                return True
            if keyCode == pygame.K_DOWN:
                tab.move_down()
                tab.scroll_row = min(len(tab.lines) - 1, tab.scroll_row + 1)
                return True

        if shift and keyCode in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_HOME, pygame.K_END):
            if tab.selection_start is None:
                tab.selection_start = (tab.cursor_row, tab.cursor_col)
        elif not shift and keyCode in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_HOME, pygame.K_END):
            tab.clear_selection()

        if keyCode in (pygame.K_RETURN, pygame.K_KP_ENTER):
            tab.newline()
            return True
        if keyCode == pygame.K_BACKSPACE:
            tab.backspace()
            return True
        if keyCode == pygame.K_DELETE:
            tab.delete()
            return True
        if keyCode == pygame.K_TAB:
            tab.tab()
            return True
        if keyCode == pygame.K_UP:
            tab.move_up()
            return True
        if keyCode == pygame.K_DOWN:
            tab.move_down()
            return True
        if keyCode == pygame.K_LEFT:
            tab.move_left()
            return True
        if keyCode == pygame.K_RIGHT:
            tab.move_right()
            return True
        if keyCode == pygame.K_HOME:
            tab.move_home()
            return True
        if keyCode == pygame.K_END:
            tab.move_end()
            return True
        if keyCode == pygame.K_PAGEUP:
            tab.cursor_row = max(0, tab.cursor_row - 15)
            tab.cursor_col = min(tab.cursor_col, len(tab.lines[tab.cursor_row]))
            return True
        if keyCode == pygame.K_PAGEDOWN:
            tab.cursor_row = min(len(tab.lines) - 1, tab.cursor_row + 15)
            tab.cursor_col = min(tab.cursor_col, len(tab.lines[tab.cursor_row]))
            return True

        if char and char.isprintable():
            tab.insert_char(char)
            return True

        from game.Game import Game
        g = Game.getInstance()
        if g and hasattr(g, "keyboard") and g.keyboard:
            last_u = getattr(g.keyboard, "last_unicode", "")
            if last_u and last_u.isprintable():
                tab.insert_char(last_u)
                g.keyboard.last_unicode = ""
                return True

        if not ctrl:
            if pygame.K_a <= keyCode <= pygame.K_z:
                letter = chr(keyCode)
                tab.insert_char(letter.upper() if shift else letter)
                return True
            if shift and keyCode in self.SHIFT_DIGITS:
                tab.insert_char(self.SHIFT_DIGITS[keyCode])
                return True
            if pygame.K_0 <= keyCode <= pygame.K_9:
                tab.insert_char(chr(keyCode))
                return True
            if keyCode in self.KEY_MAP:
                tab.insert_char(self.KEY_MAP[keyCode])
                return True

        return False

    def keyPressed(self, keyCode: int, char: str = "") -> bool:
        if not self.visible or not self.enabled or not self.is_focused:
            return False

        self.held_key = keyCode
        self.held_char = char
        self.hold_time = 0.0
        self.repeat_time = 0.0

        return self._process_key(keyCode, char)
