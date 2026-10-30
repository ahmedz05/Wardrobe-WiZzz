"""Verify installed skill bytes against the reviewed upstream Git tree; no imports/runs."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "tools/toolkit_manifest.json").read_text(encoding="utf-8"))
    verified = []
    for resource in manifest["resources"]:
        label = "ECC" if resource["repository"] == "affaan-m/ECC" else "wshobson-agents"
        license_text = (ROOT / f"tools/toolkit_sources/LICENSE-{label}.txt").read_text(encoding="utf-8")
        for skill in resource["skills"]:
            directory = args.skills_root / skill["name"]
            expected = {item["path"] for item in skill["files"]} | {"LICENSE"}
            actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
            if actual != expected:
                raise SystemExit(f"Unexpected/missing files in {skill['name']}: {actual ^ expected}")
            hashes = {}
            for item in skill["files"]:
                path = directory / item["path"]
                if path.is_symlink() or path.resolve().is_relative_to(directory.resolve()) is False:
                    raise SystemExit(f"Unsafe skill path: {path}")
                data = path.read_bytes()
                blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
                if hashlib.sha1(blob).hexdigest() != item["git_blob_sha1"]:
                    raise SystemExit(f"Upstream byte mismatch: {skill['name']}/{item['path']}")
                hashes[item["path"]] = hashlib.sha256(data).hexdigest()
            text = (directory / "SKILL.md").read_text(encoding="utf-8")
            if not text.startswith("---\n") or f"name: {skill['name']}\n" not in text:
                raise SystemExit(f"Invalid skill metadata: {skill['name']}")
            if not re.search(r"^description: .+", text, re.MULTILINE):
                raise SystemExit(f"Missing skill description: {skill['name']}")
            if (directory / "LICENSE").read_text(encoding="utf-8") != license_text:
                raise SystemExit(f"License notice mismatch: {skill['name']}")
            verified.append({"name": skill["name"], "commit": resource["commit"], "sha256": hashes})
    report = ROOT / ".tools/artifacts/toolkit-skills-verification.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({"verified": verified}, indent=2), encoding="utf-8")
    print(f"PASS: {len(verified)} skills, pinned upstream bytes, metadata, file inventory and licenses.")


if __name__ == "__main__":
    main()
