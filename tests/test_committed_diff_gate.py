import os
from pathlib import Path
import subprocess
import sys

SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/check_committed_diff.py"


def test_event_range_detects_committed_errors(tmp_path):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path).decode().strip()

    git("init")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "user.name", "Fixture")
    def commit(text):
        (tmp_path / "fixture.txt").write_text(text, encoding="utf-8")
        git("add", "fixture.txt")
        git("commit", "-m", "fixture")
        return git("rev-parse", "HEAD")

    base = commit("clean\n")
    def gate(base, head, event="push"):
        env = {**os.environ, "BASE_SHA": base, "HEAD_SHA": head, "EVENT_NAME": event}
        return subprocess.run([sys.executable, str(SCRIPT)], cwd=tmp_path,
                              env=env, capture_output=True).returncode

    clean = commit("clean\nnext\n")
    assert gate(base, clean) == 0
    assert gate("", clean, "workflow_dispatch") == 0
    assert gate(base, clean, "pull_request") == 0
    bad = commit("clean\nnext \n")
    assert git("status", "--porcelain") == ""
    assert gate(base, bad) != 0
    assert gate("0" * 40, bad) != 0
    conflict = commit("<<<<<<< branch\nconflict\n=======\nother\n>>>>>>> branch\n")
    assert gate(base, conflict) != 0
    assert gate("invalid", clean) != 0
