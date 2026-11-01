from pathlib import Path
from resources.Resource import Resource

class ResourceLoader:
    def __init__(self, game, consumer):
        self.game = game
        self.consumer = consumer
        self.resources = []

        self.tryLoadResources()

    def tryLoadResources(self):
        assets_dir = Path.cwd() / "assets"

        if not assets_dir.exists():
            if self.game.debug:
                print(f"Директория assets не найдена по пути: {assets_dir}")
            return

        try:
            for resource in assets_dir.rglob("*"):
                if resource.is_file():
                    with open(resource, "rb") as f:
                        content = f.read()
                        res = Resource(resource.name, content, resource)
                        self.resources.append(res)
                        self.consumer(res)
        except Exception as e:
            if self.game.debug:
                print(f"Ошибка при загрузке ресурсов: {e}")

    def getResourceByName(self, name: str) -> Resource | None:
        for resource in self.resources:
            if resource.name == name:
                return resource
        return None

    def getResources(self):
        return self.resources
