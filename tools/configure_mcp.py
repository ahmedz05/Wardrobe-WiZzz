"""Prepare/review MCP config, then append only absent servers to an existing config."""
import argparse
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".tools" / "integrations"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    runtime = json.loads((ROOT / ".tools/node/runtime.json").read_text(encoding="utf-8-sig"))
    node = str(Path(runtime["directory"]) / "node.exe")
    cli = str(ROOT / "tools/browser/node_modules/@playwright/mcp/cli.js")
    original = args.config.read_text(encoding="utf-8")
    existing = tomllib.loads(original).get("mcp_servers", {})
    blocks = []
    if "context7" not in existing:
        blocks.append('[mcp_servers.context7]\nurl = "https://mcp.context7.com/mcp"\nstartup_timeout_sec = 30\nenabled_tools = ["resolve-library-id", "query-docs"]\n')
    if "playwright" not in existing:
        command_args = [cli, "--headless", "--isolated", "--browser", "chrome", "--no-webmcp",
                        "--allowed-origins", "http://127.0.0.1:8080;http://127.0.0.1:8000;https://www.gstatic.com;https://fonts.gstatic.com",
                        "--output-dir", str(ROOT / ".tools/artifacts/browser")]
        blocks.append('[mcp_servers.playwright]\ncommand = ' + json.dumps(node) +
                      '\nargs = ' + json.dumps(command_args) + '\nstartup_timeout_sec = 30\n')
    fragment = "\n".join(blocks)
    combined = original.rstrip() + "\n\n" + fragment
    tomllib.loads(combined)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "mcp.fragment.toml").write_text(fragment, encoding="utf-8")
    backup = OUTPUT / "codex-config-before-mcp.toml"
    if not backup.exists():
        backup.write_text(original, encoding="utf-8")
    if args.apply and fragment:
        args.config.write_text(combined, encoding="utf-8")
    print("Applied" if args.apply else "Prepared", "MCP entries:", [name for name in ("context7", "playwright") if name not in existing])
    print("Playwright uses an isolated headless profile; no OAuth flow or API credentials created.")


if __name__ == "__main__":
    main()
