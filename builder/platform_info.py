import platform
import sys


def current_platform() -> str:
    return f"{platform.system().lower()}-{platform.machine().lower()}"


def is_windows() -> bool:
    return sys.platform == "win32"


def artifact_binary_name(app_name: str) -> str:
    if is_windows():
        return f"{app_name}.exe"
    return app_name


def build_target_label() -> str:
    if is_windows():
        return "Windows executable (.exe)"
    return f"{platform.system()} native binary"
