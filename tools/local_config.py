"""Read local configuration without importing database provisioning code."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_environment(path):
    values = {}
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        name, separator, value = line.partition("=")
        name, value = name.strip(), value.strip()
        if not separator or not name or name in values:
            raise ValueError("Invalid or duplicate environment entry.")
        try:
            parsed = json.loads(value) if value.startswith('"') else value
        except ValueError:
            raise ValueError("Invalid quoted environment value.") from None
        if not isinstance(parsed, str):
            raise ValueError("Environment values must be text.")
        values[name] = parsed
    return values
