import pygame

class Keyboard:
    def __init__(self):
        self.keys = {}
        self.key_down_listeners = []
        self.key_up_listeners = []
        self.last_unicode = ""

    def add_key_down_listener(self, listener):
        self.key_down_listeners.append(listener)

    def add_key_up_listener(self, listener):
        self.key_up_listeners.append(listener)

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            self.keys[event.key] = True
            self.last_unicode = getattr(event, "unicode", "")
            for listener in self.key_down_listeners:
                listener(event.key)
        elif event.type == pygame.KEYUP:
            self.keys[event.key] = False
            for listener in self.key_up_listeners:
                listener(event.key)

    def is_key_pressed(self, key):
        return self.keys.get(key, False)
