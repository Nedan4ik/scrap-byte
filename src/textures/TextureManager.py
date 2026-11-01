import pygame

class TextureManager:
    def __init__(self):
        self.textures = {}

    def getTexture(self, name: str) -> "Texture | None":
        if name not in self.textures:
            texture = Texture(name)

            if texture.is_loaded:
                self.textures[name] = texture
            else:
                return None

        return self.textures.get(name)


class Texture:
    def __init__(self, name: str):
        self.name = name
        from game.Game import Game

        self.resource = (
            Game.getInstance().resourceLoader.getResourceByName(name)
        )
        self.image: pygame.Surface | None = None

        if not self.resource:
            if Game.getInstance().debug:
                print(f"[Texture] Ресурс с именем '{name}' не найден.")
            return

        if not self.resource.is_image:
            if Game.getInstance().debug:
                print(
                    f"[Texture] Отмена: ресурс '{name}' не является изображением (расширение: {self.resource.extension})"
                )
            return

        try:
            self.image = pygame.image.load(
                self.resource.to_stream()
            ).convert_alpha()
            self._scaled_cache = {}
        except Exception as e:
            if Game.getInstance().debug:
                print(
                    f"[Texture] Ошибка при чтении картинки '{self.name}': {e}"
                )

    @property
    def is_loaded(self) -> bool:
        return self.image is not None

    @property
    def width(self) -> int:
        return self.image.get_width() if self.image else 0

    @property
    def height(self) -> int:
        return self.image.get_height() if self.image else 0

    def render(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        width: int | None = None,
        height: int | None = None,
    ):
        if not self.image:
            return
        
        if width is not None and height is not None:
            if (
                width == self.image.get_width()
                and height == self.image.get_height()
            ):
                screen.blit(self.image, (x, y))
                return
            size_key = (int(width), int(height))
            if size_key not in self._scaled_cache:
                self._scaled_cache[size_key] = pygame.transform.scale(
                    self.image, size_key
                )
            screen.blit(self._scaled_cache[size_key], (x, y))
        else:
            screen.blit(self.image, (x, y))