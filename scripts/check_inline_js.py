#!/usr/bin/env python3
"""Check inline JavaScript syntax in the standalone dashboard using Node.js."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "web" / "index.html"


class InlineScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_inline_script = False
        self.parts = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            attributes = dict(attrs)
            self.in_inline_script = "src" not in attributes

    def handle_data(self, data):
        if self.in_inline_script:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self.in_inline_script:
            self.scripts.append("".join(self.parts))
            self.parts = []
            self.in_inline_script = False


def main():
    if not DASHBOARD.is_file():
        print("Missing web/index.html", file=sys.stderr)
        return 1

    parser = InlineScriptParser()
    parser.feed(DASHBOARD.read_text(encoding="utf-8"))
    if not parser.scripts:
        print("No inline JavaScript block found.", file=sys.stderr)
        return 1

    try:
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as handle:
            handle.write("\n".join(parser.scripts))
            handle.flush()
            result = subprocess.run(
                ["node", "--check", handle.name],
                text=True,
                capture_output=True,
                check=False,
            )
    except FileNotFoundError:
        print("Node.js is required for the inline JavaScript syntax check.", file=sys.stderr)
        return 2

    if result.returncode:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        return result.returncode

    print("Inline JavaScript syntax check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
