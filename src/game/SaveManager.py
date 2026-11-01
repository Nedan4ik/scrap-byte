from __future__ import annotations
import os
import pickle
from datetime import datetime
from pathlib import Path


class SaveManager:
    def __init__(self, filename: str = "save.bin", base_dir: Path | str | None = None, local_dir: Path | str | None = None):
        if base_dir is not None:
            self.save_dir = Path(base_dir)
        else:
            appdata = os.environ.get("APPDATA")
            if appdata:
                self.save_dir = Path(appdata) / "scrap-byte"
            else:
                self.save_dir = Path.home() / ".scrap-byte"

        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.save_path = self.save_dir / filename
        self.levels_dir = self.save_dir / "levels"
        self.levels_dir.mkdir(parents=True, exist_ok=True)
        self.local_levels_dir = Path(local_dir) if local_dir is not None else Path("levels")
        try:
            self.local_levels_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def get_level_path(self, level_index: int) -> Path:
        return self.levels_dir / f"{level_index}.bin"

    def save_level(self, level_index: int, data: dict) -> bool:
        try:
            payload = dict(data)
            payload["level_index"] = level_index
            payload["saved_at"] = datetime.now().isoformat()
            target_path = self.get_level_path(level_index)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "wb") as f:
                pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

            try:
                self.local_levels_dir.mkdir(parents=True, exist_ok=True)
                with open(self.local_levels_dir / f"{level_index}.bin", "wb") as f_local:
                    pickle.dump(payload, f_local, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception:
                pass
            return True
        except Exception as e:
            print(f"[SaveManager] Error saving level {level_index}: {e}")
            return False

    def load_level(self, level_index: int) -> dict | None:
        local_file = self.local_levels_dir / f"{level_index}.bin"
        appdata_file = self.get_level_path(level_index)
        target = appdata_file if appdata_file.exists() else local_file
        if not target.exists():
            return None
        try:
            with open(target, "rb") as f:
                data = pickle.load(f)
            return data if isinstance(data, dict) else None
        except Exception as e:
            print(f"[SaveManager] Error loading level {level_index}: {e}")
            return None

    def is_level_completed(self, level_index: int) -> bool:
        data = self.load_level(level_index)
        return bool(data and data.get("completed", False))

    def is_level_unlocked(self, level_index: int) -> bool:
        if level_index <= 1:
            return True
        prev = self.load_level(level_index - 1)
        return bool(prev and prev.get("completed", False))

    def delete_level(self, level_index: int) -> bool:
        deleted = False
        target = self.get_level_path(level_index)
        if target.exists():
            try:
                target.unlink()
                deleted = True
            except Exception:
                pass
        local_file = self.local_levels_dir / f"{level_index}.bin"
        if local_file.exists():
            try:
                local_file.unlink()
                deleted = True
            except Exception:
                pass
        return deleted

    def save(self, data: dict) -> bool:
        try:
            payload = dict(data)
            payload["saved_at"] = datetime.now().isoformat()

            with open(self.save_path, "wb") as f:
                pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        except Exception as e:
            print(f"[SaveManager] Error saving data: {e}")
            return False

    def load(self) -> dict | None:
        if not self.save_path.exists():
            return None
        try:
            with open(self.save_path, "rb") as f:
                data = pickle.load(f)
            return data if isinstance(data, dict) else None
        except Exception as e:
            print(f"[SaveManager] Error loading data: {e}")
            return None

    def exists(self) -> bool:
        return self.save_path.exists()

    def delete(self) -> bool:
        if self.save_path.exists():
            try:
                self.save_path.unlink()
                return True
            except Exception:
                return False
        return False
