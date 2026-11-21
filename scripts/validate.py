#!/usr/bin/env python3
"""Dependency-free sanity checks for the GPT Build Lab starter project."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

class DashboardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_seen = False
        self.ids = set()
        self.duplicate_ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.title_seen = True
        element_id = attrs.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.append(element_id)
            self.ids.add(element_id)

def check(condition, message):
    if not condition:
        errors.append(message)

def main():
    dashboard = ROOT / "web" / "index.html"
    matrix = ROOT / "config" / "build-matrix.json"
    check(dashboard.is_file(), "Missing web/index.html")
    check(matrix.is_file(), "Missing config/build-matrix.json")

    if dashboard.is_file():
        source = dashboard.read_text(encoding="utf-8")
        parser = DashboardParser()
        parser.feed(source)
        check("<!doctype html>" in source.lower(), "Dashboard should declare HTML5 doctype")
        check(parser.title_seen, "Dashboard is missing a title element")
        check("projectForm" in parser.ids, "Dashboard is missing the project creation form")
        check("draftList" in parser.ids, "Dashboard is missing the projects list")
        check(not parser.duplicate_ids, "Duplicate HTML ids: " + ", ".join(parser.duplicate_ids))

    if matrix.is_file():
        try:
            data = json.loads(matrix.read_text(encoding="utf-8"))
            check(data.get("project") == "GPT Build Lab", "Build matrix project name mismatch")
            targets = data.get("targets", [])
            check(isinstance(targets, list) and len(targets) >= 3, "Build matrix should list at least three targets")
        except (json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"Invalid build matrix JSON: {exc}")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1
    print("GPT Build Lab validation passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
