from screen.Screen import Screen


class LoadingScreen(Screen):
    def __init__(self):
        super().__init__()

    def render(self, screen, mouseX: int, mouseY: int):
        super().render(screen, mouseX, mouseY)
