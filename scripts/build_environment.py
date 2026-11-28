#!/usr/bin/env python3
"""Install locked wheels and record their versions for the build."""

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path


def prepare(source: Path, *, environment: Path, report: Path) -> None:
    """
    Install the package extra and build Alto with its locked backend.

    Parameters
    ----------
    source : Path
        Project directory containing pyproject.toml and uv.lock.
    environment : Path
        New virtual environment used by this platform's build script.
    report : Path
        Destination for the interpreter and distribution versions.
    """
    subprocess.run(
        [
            "uv",
            "sync",
            "--locked",
            "--extra",
            "package",
            "--no-default-groups",
            "--no-install-project",
            "--no-build",
            "--python",
            sys.executable,
        ],
        cwd=source,
        env={**os.environ, "UV_PROJECT_ENVIRONMENT": str(environment)},
        check=True,
    )
    python = environment / (
        "Scripts/python.exe" if os.name == "nt" else "bin/python"
    )
    # With no index or cache, every required tool must already be in
    # the locked environment, including the declared build backend.
    with (source / "pyproject.toml").open("rb") as project:
        requirements = tomllib.load(project)["build-system"]["requires"]
    tools = ["pyinstaller", *requirements]
    if sys.platform in {"darwin", "win32"}:
        tools.append("pillow")
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python),
            "--no-cache",
            "--no-index",
            "--no-deps",
            "--no-build-isolation",
            *tools,
            str(source),
        ],
        check=True,
    )
    packages = subprocess.check_output(
        ["uv", "pip", "list", "--python", str(python), "--format", "json"],
        text=True,
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        json.dumps(
            {"python": sys.version, "packages": json.loads(packages)},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    prepare(
        Path(sys.argv[1]).resolve(),
        environment=Path(sys.argv[2]).resolve(),
        report=Path(sys.argv[3]).resolve(),
    )
