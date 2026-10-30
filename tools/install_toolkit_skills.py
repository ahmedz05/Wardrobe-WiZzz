"""Install only reviewed, pinned instruction files through Codex's skill installer.

Run with explicit approval for user-directory writes and public GitHub downloads.
No third-party hooks, package installers, credentials or framework agents are used.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", type=Path, required=True)
    parser.add_argument("--installer", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "tools/toolkit_manifest.json").read_text(encoding="utf-8"))
    destination = args.skills_root.resolve()
    if not args.installer.is_file():
        raise SystemExit("Official Codex skill installer not found.")
    for resource in manifest["resources"]:
        for skill in resource["skills"]:
            name = skill["name"]
            if Path(name).name != name or name in (".", ".."):
                raise SystemExit("Unsafe destination skill name.")
            if (destination / name).exists():
                raise SystemExit(f"Refusing to overwrite existing skill: {name}")
    # All sources are public. Do not send ambient GitHub credentials with downloads.
    environment = {key: value for key, value in os.environ.items()
                   if key.upper() not in {"GH_TOKEN", "GITHUB_TOKEN"}}
    for resource in manifest["resources"]:
        command = [sys.executable, "-B", str(args.installer), "--repo", resource["repository"],
                   "--ref", resource["commit"], "--method", "download",
                   "--dest", str(destination), "--path"]
        command.extend(skill["source_path"] for skill in resource["skills"])
        subprocess.run(command, check=True, env=environment)
        label = "ECC" if resource["repository"] == "affaan-m/ECC" else "wshobson-agents"
        license_text = (ROOT / f"tools/toolkit_sources/LICENSE-{label}.txt").read_text(encoding="utf-8")
        for skill in resource["skills"]:
            with (destination / skill["name"] / "LICENSE").open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(license_text)
    print("Installed five reviewed instruction-only skills. Verify before using them.")


if __name__ == "__main__":
    main()
