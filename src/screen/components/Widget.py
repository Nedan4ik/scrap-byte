import pygame


class Widget:
    def __init__(self, x: int = 0, y: int = 0, width: int = 100, height: int = 40):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True

    def getRect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def isHovered(self, mouseX: int, mouseY: int) -> bool:
        return self.getRect().collidepoint(mouseX, mouseY)

    def setPosition(self, x: int, y: int):
        self.x = x
        self.y = y

    def setSize(self, width: int, height: int):
        self.width = width
        self.height = height

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        pass

    def mouseClicked(self, mouseX: int, mouseY: int, button: int) -> bool:
        return False

    def mouseReleased(self, mouseX: int, mouseY: int, button: int) -> bool:
        return False

    def keyPressed(self, keyCode: int) -> bool:
        return False

    def keyReleased(self, keyCode: int) -> bool:
        return False
