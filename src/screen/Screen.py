from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from screen.components.Widget import Widget


class Screen:
    def __init__(self):
        from game.Game import Game
        self.game = Game.getInstance()
        self.widgets: list[Widget] = []

    def addWidget(self, widget: Widget) -> Widget:
        self.widgets.append(widget)
        return widget

    def removeWidget(self, widget: Widget):
        if widget in self.widgets:
            self.widgets.remove(widget)

    def clearWidgets(self):
        self.widgets.clear()

    add_widget = addWidget
    remove_widget = removeWidget
    clear_widgets = clearWidgets

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        for widget in self.widgets:
            if widget.visible:
                widget.render(screen, mouseX, mouseY)

    def mouseClicked(self, mouseX: int, mouseY: int, button: int):
        for widget in reversed(self.widgets):
            if widget.visible and widget.enabled:
                if widget.mouseClicked(mouseX, mouseY, button):
                    break

    def mouseReleased(self, mouseX: int, mouseY: int, button: int):
        for widget in reversed(self.widgets):
            if widget.visible and widget.enabled:
                if widget.mouseReleased(mouseX, mouseY, button):
                    break

    def mouseScrolled(self, mouseX: int, mouseY: int, scrollY: int):
        for widget in reversed(self.widgets):
            if widget.visible and widget.enabled and hasattr(widget, "mouseScrolled"):
                if widget.mouseScrolled(mouseX, mouseY, scrollY):
                    break

    def keyPressed(self, keyCode: int):
        for widget in self.widgets:
            if widget.visible and widget.enabled:
                widget.keyPressed(keyCode)

    def keyReleased(self, keyCode: int):
        for widget in self.widgets:
            if widget.visible and widget.enabled:
                widget.keyReleased(keyCode)
