import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from builder.config import WORK_ROOT
from builder.platform_info import artifact_binary_name, build_target_label, current_platform
from builder.dependencies import (
    create_build_venv,
    ensure_builder_ready,
    install_project_requirements,
    install_pyinstaller_in_venv,
    venv_python,
)

logger = logging.getLogger(__name__)


@dataclass
class BuildRequest:
    project_dir: Path
    entry_point: str = "main.py"
    name: str | None = None
    output_dir: Path | None = None
    work_dir: Path | None = None
    onefile: bool = False
    extra_args: list[str] = field(default_factory=list)
    data_files: list[str] = field(default_factory=list)
    hidden_imports: list[str] = field(default_factory=list)
    use_isolated_venv: bool = True


@dataclass
class BuildResult:
    success: bool
    artifact_dir: Path | None
    binary_path: Path | None
    platform: str
    message: str


def _resolve_name(request: BuildRequest) -> str:
    if request.name:
        return request.name
    return request.project_dir.name


def _validate_request(request: BuildRequest) -> Path:
    project_dir = request.project_dir.resolve()
    if not project_dir.is_dir():
        raise FileNotFoundError(f"project directory not found: {project_dir}")

    entry = project_dir / request.entry_point
    if not entry.is_file():
        raise FileNotFoundError(f"entry point not found: {entry}")

    return project_dir


def _pyinstaller_binary(python: Path) -> Path:
    if sys.platform == "win32":
        return python.parent / "pyinstaller.exe"
    return python.parent / "pyinstaller"


def _build_data_args(data_files: list[str], project_dir: Path) -> list[str]:
    sep = ";" if sys.platform == "win32" else ":"
    args = []
    for item in data_files:
        if sep in item:
            args.extend(["--add-data", item])
            continue
        src = Path(item)
        if not src.is_absolute():
            src = project_dir / src
        args.extend(["--add-data", f"{src}{sep}."])
    return args


def _run_pyinstaller(
    python: Path,
    project_dir: Path,
    entry_point: Path,
    name: str,
    work_dir: Path,
    request: BuildRequest,
) -> subprocess.CompletedProcess:
    pyinstaller = _pyinstaller_binary(python)
    if not pyinstaller.is_file():
        pyinstaller = python.parent / "pyinstaller"

    cmd = [
        str(pyinstaller),
        *([] if request.onefile else ["--onedir"]),
        *(["--onefile"] if request.onefile else []),
        "--noconfirm",
        "--clean",
        "--name",
        name,
        "--distpath",
        str(work_dir / "dist"),
        "--workpath",
        str(work_dir / "work"),
        "--specpath",
        str(work_dir / "spec"),
    ]

    for hidden in request.hidden_imports:
        cmd.extend(["--hidden-import", hidden])

    cmd.extend(_build_data_args(request.data_files, project_dir))
    cmd.extend(request.extra_args)
    cmd.append(str(entry_point))

    logger.info("running: %s", " ".join(cmd))
    return subprocess.run(
        cmd,
        cwd=str(project_dir),
        capture_output=True,
        text=True,
    )


def build_executable(request: BuildRequest) -> BuildResult:
    platform_label = current_platform()
    project_dir = _validate_request(request)
    name = _resolve_name(request)

    logger.info("build target: %s", build_target_label())
    work_dir = (request.work_dir or WORK_ROOT / platform_label / name).resolve()
    output_dir = (request.output_dir or work_dir / "dist").resolve()

    ensure_builder_ready()

    if request.use_isolated_venv:
        venv_dir = create_build_venv(work_dir)
        install_pyinstaller_in_venv(venv_dir)
        install_project_requirements(project_dir, venv_dir)
        python = venv_python(venv_dir)
    else:
        python = Path(sys.executable)
        req = project_dir / "requirements.txt"
        if req.is_file():
            proc = subprocess.run(
                [str(python), "-m", "pip", "install", "-r", str(req)],
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    f"project requirements install failed:\n{proc.stderr or proc.stdout}"
                )

    entry = project_dir / request.entry_point
    result = _run_pyinstaller(python, project_dir, entry, name, work_dir, request)

    if result.returncode != 0:
        log_tail = (result.stderr or result.stdout)[-4000:]
        return BuildResult(
            success=False,
            artifact_dir=None,
            binary_path=None,
            platform=platform_label,
            message=f"pyinstaller failed:\n{log_tail}",
        )

    artifact = work_dir / "dist" / name
    binary = artifact / artifact_binary_name(name)
    if output_dir != artifact.parent and artifact.exists():
        target = output_dir / name
        if target.exists():
            shutil.rmtree(target)
        output_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(artifact, target)
        artifact = target

    if not artifact.exists() or not binary.is_file():
        return BuildResult(
            success=False,
            artifact_dir=None,
            binary_path=None,
            platform=platform_label,
            message="build finished but binary was not found",
        )

    return BuildResult(
        success=True,
        artifact_dir=artifact,
        binary_path=binary,
        platform=platform_label,
        message=f"build complete: {binary}",
    )
