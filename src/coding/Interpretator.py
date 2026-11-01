from __future__ import annotations
import ast
from contextlib import redirect_stderr, redirect_stdout
import io
import math
import random
import threading
import time
import traceback
import sys
from typing import Any
from coding.ExecutionResult import ExecutionResult


class Interpretator:
    FEATURE_NODES = {
        "if": (ast.If, ast.IfExp),
        "for": (ast.For, ast.AsyncFor),
        "while": (ast.While,),
        "def": (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda),
        "function": (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda),
        "class": (ast.ClassDef,),
        "import": (ast.Import, ast.ImportFrom),
        "try": (ast.Try, ast.ExceptHandler, getattr(ast, "TryStar", ast.Try)),
        "except": (ast.ExceptHandler,),
        "comprehension": (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp),
    }

    LEVEL_BANS = {
        1: ["if", "for", "while", "def", "class", "import", "try", "except", "comprehension"],
        2: ["for", "while", "def", "class", "import", "try", "except", "comprehension"],
        3: ["while", "def", "class", "import", "try", "except", "comprehension"],
        4: ["def", "class", "import", "try", "except"],
    }

    ALL_DRONE_COMMANDS = {
        "forward", "turn_left", "turn_right", "left", "right", "pickup",
        "pos", "get_pos", "heading", "heading_name", "angle", "front",
        "is_air", "is_obstacle", "is_moving", "is_turning", "is_busy",
        "can_forward", "front_is_obstacle", "front_is_air", "can_pickup", "has_trash",
        "sleep", "wait", "wait_idle",
    }

    LEVEL_ALLOWED_COMMANDS = {
        1: {"forward", "turn_left", "turn_right", "left", "right", "pickup"},
        2: {
            "forward", "turn_left", "turn_right", "left", "right", "pickup",
            "can_forward", "front_is_obstacle", "front_is_air", "can_pickup", "has_trash",
            "is_obstacle", "is_air", "front", "pos", "get_pos", "heading", "heading_name",
        },
    }

    def __init__(self, context: dict | None = None, level_index: int | None = 1):
        self.game = None
        self.level = None
        self.drone = None
        self.level_index = level_index
        self.env: dict[str, Any] = {}
        self.output_history: list[str] = []
        self.disallowed_features: set[str] = set()
        self.disallowed_functions: set[str] = set()
        self.allowed_drone_commands: set[str] | None = None
        self._thread: threading.Thread | None = None
        self._stop_requested = False
        self.action_delay: float = 0.7
        self.current_line: int | None = None
        self.on_line_step: Any = None

        if level_index is not None:
            self.set_level_restrictions(level_index)
        self.set_context(**(context or {}))

    @property
    def globals(self) -> dict[str, Any]:
        return self.env

    @property
    def locals(self) -> dict[str, Any]:
        return self.env

    def disallow_feature(self, feature: str):
        self.disallowed_features.add(feature.lower())

    def allow_feature(self, feature: str):
        self.disallowed_features.discard(feature.lower())

    def disallow_function(self, name: str):
        self.disallowed_functions.add(name)

    def allow_function(self, name: str):
        self.disallowed_functions.discard(name)

    def set_disallowed_features(self, features: list[str] | set[str]):
        self.disallowed_features = {f.lower() for f in features}

    def set_disallowed_functions(self, functions: list[str] | set[str]):
        self.disallowed_functions = set(functions)

    def allow_all(self):
        self.level_index = None
        self.disallowed_features.clear()
        self.disallowed_functions.clear()
        self.allowed_drone_commands = None

    def set_level_restrictions(self, level: int):
        self.level_index = level
        self.set_disallowed_features(self.LEVEL_BANS.get(level, []))
        if level in self.LEVEL_ALLOWED_COMMANDS:
            self.allowed_drone_commands = set(self.LEVEL_ALLOWED_COMMANDS[level])
        else:
            self.allowed_drone_commands = None

    def validate_code(self, code: str) -> tuple[bool, str | None]:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Синтаксическая ошибка: {e}"

        for node in ast.walk(tree):
            for feat in self.disallowed_features:
                if isinstance(node, self.FEATURE_NODES.get(feat, ())):
                    line = getattr(node, "lineno", "?")
                    return False, f"Использование {feat} запрещено на этом уровне (строка {line})"

            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", None)
                if not name:
                    continue
                line = getattr(node, "lineno", "?")
                if self.disallowed_functions and name in self.disallowed_functions:
                    return False, f"Использование функции '{name}()' запрещено на этом уровне (строка {line})"
                if self.allowed_drone_commands is not None and name in self.ALL_DRONE_COMMANDS:
                    if name not in self.allowed_drone_commands:
                        return False, f"Команда '{name}()' недоступна на {self.level_index} уровне (строка {line}). Разрешены только: forward(), turn_left(), turn_right(), pickup()"

        return True, None

    def set_context(self, game=None, level=None, drone=None, **kwargs):
        if game is not None:
            self.game = game
        if level is not None:
            self.level = level
        self.drone = drone or (self.level.drone if self.level and hasattr(self.level, "drone") else self.drone)
        self._rebuild_environment(**kwargs)

    def _is_busy(self) -> bool:
        return bool(self.drone and (getattr(self.drone, "is_busy", False) or getattr(self.drone, "is_moving", False) or getattr(self.drone, "is_turning", False)))

    def _front_tile(self) -> tuple[int, int, bool]:
        if not self.drone or not self.level:
            return -1, -1, True
        dc, dr = self.drone.DIR_OFFSETS[self.drone.heading]
        fc, fr = self.drone.col + dc, self.drone.row + dr
        return fc, fr, self.level.is_air(fc, fr)

    def _front_is_obstacle(self) -> bool:
        if not self.drone or not self.level:
            return False
        dc, dr = self.drone.DIR_OFFSETS[self.drone.heading]
        fc, fr = self.drone.col + dc, self.drone.row + dr
        return bool(getattr(self.level, "is_obstacle", lambda c, r: False)(fc, fr))

    def _front_is_air(self) -> bool:
        if not self.drone or not self.level:
            return True
        dc, dr = self.drone.DIR_OFFSETS[self.drone.heading]
        fc, fr = self.drone.col + dc, self.drone.row + dr
        return bool(self.level.is_air(fc, fr))

    def _can_forward(self) -> bool:
        if not self.drone or not self.level or self._is_busy():
            return False
        dc, dr = self.drone.DIR_OFFSETS[self.drone.heading]
        fc, fr = self.drone.col + dc, self.drone.row + dr
        if self.level.is_air(fc, fr):
            return False
        if getattr(self.level, "is_obstacle", lambda c, r: False)(fc, fr):
            return False
        return True

    def _can_pickup(self) -> bool:
        if not self.drone or not self.level or not getattr(self.level, "trashItems", None):
            return False
        dc, dr = self.drone.col, self.drone.row
        for t in self.level.trashItems:
            if not t.collected:
                tc, tr = self.level.world_to_grid(t.x, t.y)
                if (tc, tr) == (dc, dr):
                    return True
        return False

    def _sleep(self, seconds: float):
        elapsed = 0.0
        while elapsed < seconds and not self._stop_requested:
            time.sleep(0.016)
            elapsed += 0.016

    def _cmd_forward(self) -> bool:
        if not self.drone or not self.level:
            return False
        res = self.drone.move_forward(self.level)
        if res and self.action_delay > 0:
            self._sleep(self.action_delay)
        return res

    def _cmd_left(self) -> bool:
        if not self.drone:
            return False
        self.drone.turn_left()
        if self.action_delay > 0:
            self._sleep(self.action_delay)
        return True

    def _cmd_right(self) -> bool:
        if not self.drone:
            return False
        self.drone.turn_right()
        if self.action_delay > 0:
            self._sleep(self.action_delay)
        return True

    def _cmd_pickup(self) -> bool:
        if not self.drone:
            return False
        self.drone.pickup()
        found = False
        if self.level and hasattr(self.level, "trashItems"):
            dc, dr = self.drone.col, self.drone.row
            for t in self.level.trashItems:
                if not t.collected:
                    tc, tr = self.level.world_to_grid(t.x, t.y)
                    if (tc, tr) == (dc, dr):
                        t.collected = True
                        found = True
                        break
        from sound.SoundManager import SoundManager
        sm = SoundManager.get_instance()
        if sm:
            if found:
                sm.play_pickup_success()
            else:
                sm.play_pickup_fail()
        if self.action_delay > 0:
            self._sleep(self.action_delay)
        return True

    def _wait_idle(self, timeout: float = 10.0):
        elapsed = 0.0
        while elapsed < timeout and not self._stop_requested and self._is_busy():
            time.sleep(0.016)
            elapsed += 0.016

    def _log(self, *args, sep: str = " "):
        text = sep.join(str(a) for a in args)
        print(text)
        self.output_history.append(text)

    def _rebuild_environment(self, **kwargs):
        self.env = {
            "math": math,
            "random": random,
            "time": time,
            "game": self.game,
            "level": self.level,
            "drone": self.drone,
            "blocks": self.level.blocks if self.level else None,
            "trash": self.level.trashItems if self.level else None,
            "forward": self._cmd_forward,
            "turn_left": self._cmd_left,
            "turn_right": self._cmd_right,
            "left": self._cmd_left,
            "right": self._cmd_right,
            "pickup": self._cmd_pickup,
            "pos": lambda: (self.drone.col, self.drone.row) if self.drone else (-1, -1),
            "get_pos": lambda: (self.drone.col, self.drone.row) if self.drone else (-1, -1),
            "heading": lambda: self.drone.heading if self.drone else 0,
            "heading_name": lambda: ("UP", "RIGHT", "DOWN", "LEFT")[(self.drone.heading if self.drone else 0) % 4],
            "angle": lambda: self.drone.angle if self.drone else 0.0,
            "is_moving": lambda: bool(self.drone and getattr(self.drone, "is_moving", False)),
            "is_turning": lambda: bool(self.drone and getattr(self.drone, "is_turning", False)),
            "is_busy": self._is_busy,
            "is_air": lambda c, r: self.level.is_air(c, r) if self.level else True,
            "is_obstacle": lambda c, r: self.level.is_obstacle(c, r) if self.level and hasattr(self.level, "is_obstacle") else False,
            "front": self._front_tile,
            "front_is_obstacle": self._front_is_obstacle,
            "front_is_air": self._front_is_air,
            "can_forward": self._can_forward,
            "can_pickup": self._can_pickup,
            "has_trash": self._can_pickup,
            "sleep": self._sleep,
            "wait": self._sleep,
            "wait_idle": self._wait_idle,
            "log": self._log,
        }
        self.env.update(kwargs)

    def execute(self, code: str) -> ExecutionResult:
        is_valid, err = self.validate_code(code)
        if not is_valid:
            return ExecutionResult(False, "", err, None)

        out_stream, err_stream = io.StringIO(), io.StringIO()
        res_val, err_msg, ok = None, None, True

        def _tracer(frame, event, arg):
            if event == "line" and frame.f_code.co_filename == "<user_code>":
                line_no = frame.f_lineno - 1
                self.current_line = line_no
                if self.on_line_step:
                    try:
                        self.on_line_step(line_no)
                    except Exception:
                        pass
            return _tracer

        old_trace = sys.gettrace()
        sys.settrace(_tracer)

        with redirect_stdout(out_stream), redirect_stderr(err_stream):
            try:
                try:
                    res_val = eval(compile(ast.parse(code, mode="eval"), "<user_code>", "eval"), self.env, self.env)
                except SyntaxError:
                    exec(compile(ast.parse(code, mode="exec"), "<user_code>", "exec"), self.env, self.env)
            except Exception as e:
                ok = False
                err_msg = f"{type(e).__name__}: {e}"
            finally:
                sys.settrace(old_trace)
                self.current_line = None
                if self.on_line_step:
                    try:
                        self.on_line_step(None)
                    except Exception:
                        pass

        stdout_val = out_stream.getvalue()
        stderr_val = err_stream.getvalue()
        combined_out = stdout_val + (f"\n{stderr_val}" if stderr_val else "")

        if combined_out:
            self.output_history.extend(combined_out.strip().split("\n"))

        return ExecutionResult(ok, combined_out, err_msg, res_val)

    def eval(self, expr: str) -> Any:
        return eval(compile(ast.parse(expr, mode="eval"), "<string>", "eval"), self.env, self.env)

    def get_variable(self, name: str, default: Any = None) -> Any:
        return self.env.get(name, default)

    def set_variable(self, name: str, value: Any):
        self.env[name] = value

    def run_async(self, code: str, on_complete: Any = None):
        self._stop_requested = False

        def _worker():
            res = self.execute(code)
            if on_complete:
                on_complete(res)

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_requested = True
