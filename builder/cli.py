import argparse
import logging
import sys
from pathlib import Path

from builder import __version__
from builder.config import DEFAULT_HOST, DEFAULT_PORT
from builder.dependencies import ensure_builder_ready
from builder.executable import BuildRequest, build_executable
from builder.platform_info import build_target_label, current_platform, is_windows
from builder.server import create_app


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def _pyinstaller_extra_args(args: argparse.Namespace) -> list[str]:
    extra = list(args.extra or [])
    for package in args.collect_all or []:
        extra.extend(["--collect-all", package])
    return extra


def cmd_check(_args: argparse.Namespace) -> int:
    ensure_builder_ready()
    print("builder dependencies are ready")
    return 0


def cmd_info(_args: argparse.Namespace) -> int:
    print(f"host platform: {current_platform()}")
    print(f"build output:  {build_target_label()}")
    if not is_windows():
        print("note: Windows .exe requires running build on Windows or GitLab Windows runner")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    project_dir = Path(args.project).resolve()

    request = BuildRequest(
        project_dir=project_dir,
        entry_point=args.entry,
        name=args.name,
        output_dir=Path(args.output).resolve() if args.output else None,
        work_dir=Path(args.work_dir).resolve() if args.work_dir else None,
        onefile=args.onefile,
        hidden_imports=args.hidden_import or [],
        data_files=args.data or [],
        extra_args=_pyinstaller_extra_args(args),
        use_isolated_venv=not args.no_venv,
    )

    try:
        result = build_executable(request)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if result.success:
        print(result.message)
        print(f"platform: {result.platform}")
        print(f"artifact: {result.artifact_dir}")
        return 0

    print(result.message, file=sys.stderr)
    return 1


def cmd_serve(args: argparse.Namespace) -> int:
    ensure_builder_ready()
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyexe-builder",
        description="build windows/linux executables from python projects",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("-v", "--verbose", action="store_true")

    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="verify builder dependencies")
    check.set_defaults(func=cmd_check)

    info = sub.add_parser("info", help="show build platform information")
    info.set_defaults(func=cmd_info)

    build = sub.add_parser("build", help="build an executable from a python project")
    build.add_argument("project", help="path to the python project directory")
    build.add_argument("-e", "--entry", default="main.py", help="entry script")
    build.add_argument("-n", "--name", help="executable name")
    build.add_argument("-o", "--output", help="output directory for dist")
    build.add_argument("-w", "--work-dir", help="temporary build directory")
    build.add_argument("--onefile", action="store_true", help="single file output")
    build.add_argument(
        "--hidden-import",
        action="append",
        dest="hidden_import",
        metavar="MODULE",
        help="pyinstaller hidden import",
    )
    build.add_argument(
        "--data",
        action="append",
        metavar="PATH",
        help="add data file or folder",
    )
    build.add_argument(
        "--extra",
        action="append",
        metavar="ARG",
        help="extra pyinstaller argument",
    )
    build.add_argument(
        "--collect-all",
        action="append",
        dest="collect_all",
        metavar="PACKAGE",
        help="pyinstaller --collect-all for a package",
    )
    build.add_argument(
        "--no-venv",
        action="store_true",
        help="skip isolated venv (not recommended)",
    )
    build.set_defaults(func=cmd_build)

    serve = sub.add_parser("serve", help="run flask api server")
    serve.add_argument("--host", default=DEFAULT_HOST)
    serve.add_argument("--port", type=int, default=DEFAULT_PORT)
    serve.add_argument("--debug", action="store_true")
    serve.set_defaults(func=cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _setup_logging(args.verbose)
    return args.func(args)
