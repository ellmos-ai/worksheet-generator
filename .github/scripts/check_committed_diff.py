"""Check the complete event commit range, including clean checked-out changes."""
import os
import re
import subprocess


def main():
    base, head = os.environ.get("BASE_SHA", ""), os.environ.get("HEAD_SHA", "")
    event = os.environ.get("EVENT_NAME", "")
    if event == "workflow_dispatch" and not base and re.fullmatch(r"[0-9a-f]{40}", head):
        parents = subprocess.check_output(["git", "rev-list", "--parents", "-n", "1", head]).decode().split()
        base = parents[1] if len(parents) > 1 else "0" * 40
    if not all(re.fullmatch(r"[0-9a-f]{40}", value) for value in (base, head)):
        raise SystemExit("Missing or invalid event commit identity")
    if base == "0" * 40:
        base = subprocess.check_output(
            ["git", "hash-object", "-t", "tree", "--stdin"], input=b""
        ).decode().strip()
    elif event == "pull_request":
        base = subprocess.check_output(["git", "merge-base", base, head]).decode().strip()
    return subprocess.run(
        ["git", "--no-pager", "diff", "--no-ext-diff", "--no-textconv",
         "--check", base, head, "--"], check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
