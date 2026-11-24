"""
Check benchmark workflow setup on detached release tags and ordinary
branch checkouts.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("ref", ["main", "v0.0.1"])
def test_benchmark_setup_resolves_main_without_moving_the_measured_commit(
    tmp_path: Path,
    ref: str,
) -> None:
    """
    Check the real workflow setup in a fresh clone, with a release tag
    behind main, and on a normal main checkout.

    Parameters
    ----------
    tmp_path : Path
        Temporary Git repositories with no network or user
        configuration.
    ref : str
        The branch or release tag checked out as GitHub Actions would.
    """
    yaml = pytest.importorskip("yaml")
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/performance.yml").read_text(),
    )
    steps = workflow["jobs"]["benchmark"]["steps"]
    setup = next(
        step for step in steps if step.get("id") == "benchmark-branch"
    )
    measure = next(
        step for step in steps if step.get("name") == "Measure this version"
    )
    assert steps.index(setup) < steps.index(measure)
    branch = json.loads((ROOT / "asv.conf.json").read_text())["branches"][0]
    environment = dict(os.environ)
    environment.update(
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        GIT_AUTHOR_NAME="Alto tests",
        GIT_AUTHOR_EMAIL="tests@example.invalid",
        GIT_COMMITTER_NAME="Alto tests",
        GIT_COMMITTER_EMAIL="tests@example.invalid",
    )

    def git(
        args: list[str],
        *,
        cwd: Path,
    ) -> str:
        """
        Run a Git command in a temporary repository.

        Parameters
        ----------
        args : list of str
            Git's arguments.
        cwd : pathlib.Path
            The repository or its containing directory. Keyword-only.

        Returns
        -------
        str
            The command's standard output, without surrounding
            whitespace.
        """
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    source = tmp_path / "source"
    checkout = tmp_path / "checkout"
    git(["init", "--initial-branch=main", str(source)], cwd=tmp_path)
    git(
        [
            "commit",
            "--allow-empty",
            "-m",
            "release",
        ],
        cwd=source,
    )
    git(
        [
            "tag",
            "-a",
            "v0.0.1",
            "-m",
            "release",
        ],
        cwd=source,
    )
    git(
        [
            "commit",
            "--allow-empty",
            "-m",
            "later main",
        ],
        cwd=source,
    )
    git(
        [
            "clone",
            "--no-hardlinks",
            "--branch",
            ref,
            str(source),
            str(checkout),
        ],
        cwd=tmp_path,
    )
    measured = git(["rev-parse", "HEAD"], cwd=checkout)
    main = git(["rev-parse", "origin/main"], cwd=checkout)
    if ref != "main":
        assert git(["branch", "--list", branch], cwd=checkout) == ""
        assert measured != main
    for _ in range(
        2,
    ):  # rerunning the setup must be harmless on an existing local main
        subprocess.run(
            [
                "sh",
                "-eu",
                "-c",
                setup["run"],
            ],
            cwd=checkout,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        assert git(["rev-parse", branch], cwd=checkout) == main
        assert git(["rev-parse", "HEAD"], cwd=checkout) == measured
