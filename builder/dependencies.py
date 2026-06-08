import importlib.util
import logging
import subprocess
import sys
from pathlib import Path

from builder.config import BUILDER_REQUIREMENTS

logger = logging.getLogger(__name__)


def _pip_executable() -> str:
    return str(Path(sys.executable).parent / ("pip.exe" if sys.platform == "win32" else "pip"))


def _is_installed(spec: str) -> bool:
    module = spec.split("==")[0].split("[")[0]
    if module.lower() == "pyinstaller":
        module = "PyInstaller"
    return importlib.util.find_spec(module) is not None


def _missing_packages(packages: tuple[str, ...]) -> list[str]:
    return [spec for spec in packages if not _is_installed(spec)]


def ensure_packages(packages: tuple[str, ...], label: str) -> None:
    missing = _missing_packages(packages)
    if not missing:
        logger.info("%s dependencies already satisfied", label)
        return

    logger.info("installing %s: %s", label, ", ".join(missing))
    cmd = [_pip_executable(), "install", *missing]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"pip install failed:\n{result.stderr or result.stdout}")


def ensure_builder_ready() -> None:
    ensure_packages(BUILDER_REQUIREMENTS, "builder")


def venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _bootstrap_venv(venv_dir: Path) -> None:
    python = venv_python(venv_dir)
    cmd = [
        str(python),
        "-m",
        "pip",
        "install",
        "-q",
        "-U",
        "pip",
        "setuptools",
        "wheel",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"venv bootstrap failed:\n{result.stderr or result.stdout}")


def create_build_venv(work_dir: Path) -> Path:
    venv_dir = work_dir / "venv"
    work_dir.mkdir(parents=True, exist_ok=True)

    if not venv_dir.exists():
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"venv creation failed:\n{result.stderr or result.stdout}")

    _bootstrap_venv(venv_dir)
    return venv_dir


def install_project_requirements(project_dir: Path, venv_dir: Path) -> None:
    requirements_file = project_dir / "requirements.txt"
    if not requirements_file.is_file():
        logger.warning("no requirements.txt in %s", project_dir)
        return

    python = venv_python(venv_dir)
    pip = [str(python), "-m", "pip", "install", "-r", str(requirements_file)]
    result = subprocess.run(pip, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"project requirements install failed:\n{result.stderr or result.stdout}")

    # pyinstaller/altgraph still need pkg_resources (removed in setuptools 82+)
    fix = [str(python), "-m", "pip", "install", "-q", "setuptools<81"]
    subprocess.run(fix, capture_output=True, text=True)


def install_pyinstaller_in_venv(venv_dir: Path) -> None:
    python = venv_python(venv_dir)
    cmd = [str(python), "-m", "pip", "install", *BUILDER_REQUIREMENTS]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"pyinstaller install in venv failed:\n{result.stderr or result.stdout}")
