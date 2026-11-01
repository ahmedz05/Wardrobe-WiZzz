"""Hash application files before/after tooling work without importing the app."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / ".tools" / "toolkit" / "application-before.json"


def application_hashes():
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--",
         "backend", "frontend", "ai", "database", "requirements.txt"],
        cwd=ROOT, capture_output=True, check=True,
    )
    paths = sorted(set(name.decode("utf-8") for name in result.stdout.split(b"\0") if name))
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in paths if (ROOT / name).is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()
    current = application_hashes()
    if args.snapshot:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        if BASELINE.exists():
            raise SystemExit("Baseline already exists; refusing to overwrite it.")
        BASELINE.write_text(json.dumps(current, indent=2), encoding="utf-8")
        print(f"Recorded {len(current)} application/source files; no app imports or database access.")
    else:
        previous = json.loads(BASELINE.read_text(encoding="utf-8"))
        changed = sorted(name for name in set(previous) | set(current) if previous.get(name) != current.get(name))
        if changed:
            raise SystemExit("Application files changed: " + ", ".join(changed))
        print(f"PASS: all {len(current)} application/source files match the pre-tooling baseline.")


if __name__ == "__main__":
    main()
