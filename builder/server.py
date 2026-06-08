import logging
from pathlib import Path

from flask import Flask, jsonify, request

from builder import __version__
from builder.dependencies import ensure_builder_ready
from builder.executable import BuildRequest, build_executable

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "version": __version__})

    @app.post("/build")
    def build():
        body = request.get_json(silent=True) or {}

        project = body.get("project_dir")
        if not project:
            return jsonify({"error": "project_dir is required"}), 400

        try:
            ensure_builder_ready()
            result = build_executable(
                BuildRequest(
                    project_dir=Path(project),
                    entry_point=body.get("entry_point", "main.py"),
                    name=body.get("name"),
                    onefile=bool(body.get("onefile", False)),
                    hidden_imports=body.get("hidden_imports", []),
                    data_files=body.get("data_files", []),
                    extra_args=body.get("extra_args", []),
                    use_isolated_venv=bool(body.get("use_isolated_venv", True)),
                )
            )
        except (FileNotFoundError, RuntimeError) as exc:
            return jsonify({"success": False, "message": str(exc)}), 400

        status = 200 if result.success else 500
        return jsonify(
            {
                "success": result.success,
                "platform": result.platform,
                "artifact_dir": str(result.artifact_dir) if result.artifact_dir else None,
                "binary_path": str(result.binary_path) if result.binary_path else None,
                "message": result.message,
            }
        ), status

    return app
