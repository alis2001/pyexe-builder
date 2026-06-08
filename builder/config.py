import os
from pathlib import Path

BUILDER_REQUIREMENTS = (
    "pyinstaller==6.11.1",
)

DEFAULT_HOST = os.environ.get("PYEXE_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("PYEXE_PORT", "5080"))
WORK_ROOT = Path(os.environ.get("PYEXE_WORK_ROOT", ".build"))

DEFAULT_PYINSTALLER_ARGS = (
    "--onedir",
    "--noconfirm",
    "--clean",
)
