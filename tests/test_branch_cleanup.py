"""Exercise Alto's post-merge hook during a fast-forward pull in an isolated clone."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_pull_prunes_only_merged_local_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check the hook, manual preview, and keep list with a real origin and two checkouts.

    Parameters
    ----------
    tmp_path : Path
        Parent directory for disposable repositories and the hook cache.
    monkeypatch : pytest.MonkeyPatch
        Isolate Git and pre-commit configuration.
    """
    yaml = pytest.importorskip("yaml")
    for name in list(os.environ):
        if name.startswith("GIT_"):
            monkeypatch.delenv(name)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("LC_ALL", "C")
    monkeypatch.setenv("PRE_COMMIT_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Test")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Test")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "test@example.org")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "test@example.org")
    clone = tmp_path / "clone"
    clone.mkdir()

    def git(*args: str, cwd: Path = clone) -> str:
        """
        Run Git in the test clone or the specified repository.

        Parameters
        ----------
        *args : str
            Arguments for Git.
        cwd : Path
            Working directory.

        Returns
        -------
        str
            Standard output with surrounding whitespace removed.
        """
        return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()

    origin = tmp_path / "origin.git"
    git("init", "--bare", "--initial-branch=main", str(origin))
    git("init", "--initial-branch=main")
    git("remote", "add", "origin", str(origin))

    # Exercise the real configured hook without downloading unrelated linters.
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    assert "post-merge" in config["default_install_hook_types"]
    hooks = [
        hook for repo in config["repos"] if repo["repo"] == "local" for hook in repo["hooks"] if "post-merge" in hook["stages"]
    ]
    assert [hook["id"] for hook in hooks] == ["prune-merged-branches"]
    config["repos"] = [{"repo": "local", "hooks": hooks}]
    (clone / ".pre-commit-config.yaml").write_text(yaml.safe_dump(config))
    (clone / "scripts").mkdir()
    script = Path("scripts/prune-branches.sh")
    shutil.copyfile(ROOT / script, clone / script)
    git("add", ".")
    git("commit", "-qm", "initial")
    git("push", "-u", "origin", "main")

    # A branch with a live upstream is still eligible once both mains contain it.
    git("switch", "-c", "feature/merged")
    git("commit", "--allow-empty", "-qm", "feature")
    tip = git("rev-parse", "--short", "HEAD")
    git("push", "-u", "origin", "feature/merged")
    git("push", "origin", "HEAD:main")
    for branch in ("release/next", "personal", "gh-pages", "asv-results", "in-use", "feature/another"):
        git("branch", branch)
    git("config", "--add", "alto.keepBranch", "release/next")
    git("config", "--add", "alto.keepBranch", "personal")
    git("worktree", "add", str(tmp_path / "other"), "in-use")
    git("switch", "-c", "feature/continued")
    git("commit", "--allow-empty", "-qm", "unmerged work")

    subprocess.run([sys.executable, "-m", "pre_commit", "install"], cwd=clone, check=True)
    git("switch", "-c", "side", "main")
    git("merge", "--ff-only", "origin/main")
    assert git("branch", "--list", "feature/merged")
    git("switch", "main")
    preview = subprocess.check_output(["sh", str(script), "--dry-run"], cwd=clone, text=True)
    assert "feature/merged" not in preview  # origin/main has it, local main still does not
    report = subprocess.check_output(["git", "pull", "--ff-only"], cwd=clone, text=True, stderr=subprocess.STDOUT)
    assert f"feature/merged (was {tip})" in report
    remaining = set(git("for-each-ref", "--format=%(refname:lstrip=2)", "refs/heads").splitlines())
    assert remaining == {"main", "release/next", "personal", "gh-pages", "asv-results", "in-use", "feature/continued"}
    assert git("rev-parse", "--short", "refs/heads/feature/merged", cwd=origin) == tip

    git("branch", "preview-me")
    preview = subprocess.check_output(["sh", str(script), "--dry-run"], cwd=clone, text=True)
    assert f"preview-me ({tip})" in preview
    assert git("branch", "--list", "preview-me")
    # A local merge can advance main beyond origin/main.
    git("merge", "--ff-only", "feature/continued")
    assert git("branch", "--list", "feature/continued")
