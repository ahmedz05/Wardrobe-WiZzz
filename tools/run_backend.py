"""Run the real API without creating schemas; secrets come from a local env file."""
import argparse
import os
import sys
from pathlib import Path

from local_config import read_environment

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / "backend" / ".env.local")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    values = read_environment(args.env_file)
    if not {"DATABASE_URL", "JWT_SECRET_KEY"}.issubset(values):
        parser.error("The env file must define DATABASE_URL and JWT_SECRET_KEY.")
    os.environ.update(values)
    sys.path.insert(0, str(ROOT / "backend"))
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=args.port, access_log=False)


if __name__ == "__main__":
    main()
