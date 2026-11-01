import pygame


class Mouse:
    def __init__(self):
        self.mouseX = 0
        self.mouseY = 0
        self.button_down_listeners = []
        self.button_up_listeners = []
        self.scroll_listeners = []

    def add_button_down_listener(self, listener):
        self.button_down_listeners.append(listener)

    def add_button_up_listener(self, listener):
        self.button_up_listeners.append(listener)

    def add_scroll_listener(self, listener):
        self.scroll_listeners.append(listener)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEWHEEL:
            for listener in self.scroll_listeners:
                listener(event.y, self.mouseX, self.mouseY)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouseX, self.mouseY = event.pos
            if event.button == 4:
                for listener in self.scroll_listeners:
                    listener(1, self.mouseX, self.mouseY)
            elif event.button == 5:
                for listener in self.scroll_listeners:
                    listener(-1, self.mouseX, self.mouseY)
            else:
                for listener in self.button_down_listeners:
                    listener(event.button, self.mouseX, self.mouseY)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouseX, self.mouseY = event.pos
            if event.button not in (4, 5):
                for listener in self.button_up_listeners:
                    listener(event.button, self.mouseX, self.mouseY)
        elif event.type == pygame.MOUSEMOTION:
            self.mouseX, self.mouseY = event.pos
