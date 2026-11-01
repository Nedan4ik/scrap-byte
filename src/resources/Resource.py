import io
import json
from pathlib import Path


class Resource:
    def __init__(
        self,
        name: str,
        content: bytes,
        path: Path | str | None = None,
        extension: str | None = None,
    ):
        name_path = Path(name)
        self.name: str = name_path.stem
        self.bytes: bytes = content
        self.path: Path | None = Path(path) if path else None

        if extension:
            self.extension = (
                extension if extension.startswith(".") else f".{extension}"
            )
        elif self.path:
            self.extension = self.path.suffix.lower()
        else:
            self.extension = Path(name).suffix.lower() if "." in name else ""

    @property
    def size(self) -> int:
        return len(self.bytes)

    def to_stream(self) -> io.BytesIO:
        return io.BytesIO(self.bytes)

    def to_text(self, encoding: str = "utf-8") -> str:
        return self.bytes.decode(encoding)

    def to_json(self) -> dict | list:
        return json.loads(self.to_text())

    @property
    def is_image(self) -> bool:
        return self.extension in (".png", ".jpg", ".jpeg", ".bmp")

    @property
    def is_audio(self) -> bool:
        return self.extension in (".wav", ".ogg", ".mp3")

    @property
    def is_config(self) -> bool:
        return self.extension in (".json", ".yaml", ".toml", ".ini", ".txt")

    @property
    def is_font(self) -> bool:
        return self.extension in (".ttf", ".otf")
