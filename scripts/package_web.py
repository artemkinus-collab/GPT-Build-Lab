#!/usr/bin/env python3
"""Safely package a static web project into a ZIP artifact.

This tool never executes project scripts. It rejects symlinks, secret-like files,
oversized projects, and archives without a root-level index.html.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path, PurePosixPath
import sys
import zipfile

MAX_FILES = 10_000
MAX_TOTAL_BYTES = 100 * 1024 * 1024
EXCLUDED_DIRS = {".git", ".github", ".ssh", ".aws", ".azure", ".terraform", "node_modules", ".venv", "venv", "__pycache__", ".next", ".cache"}
SECRET_NAMES = {".env", ".env.local", ".env.production", ".npmrc", ".pypirc", ".netrc", "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa", "credentials.json", "secrets.json", "service-account.json", "terraform.tfstate"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".keystore", ".jks"}


def is_secret(path: Path) -> bool:
    name = path.name.lower()
    return name in SECRET_NAMES or name.startswith(".env.") or path.suffix.lower() in SECRET_SUFFIXES


def collect_files(root: Path) -> list[Path]:
    if not root.is_dir():
        raise ValueError(f"Project directory does not exist: {root}")
    files: list[Path] = []
    total = 0
    for current, dirs, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept_dirs = []
        for directory in dirs:
            candidate = current_path / directory
            if directory in EXCLUDED_DIRS:
                continue
            if candidate.is_symlink():
                raise ValueError(f"Symlink directories are not allowed: {candidate.relative_to(root)}")
            kept_dirs.append(directory)
        dirs[:] = kept_dirs
        for name in names:
            path = current_path / name
            if path.is_symlink():
                raise ValueError(f"Symlinks are not allowed: {path.relative_to(root)}")
            if not path.is_file():
                continue
            if is_secret(path):
                raise ValueError(f"Potential secret file found; remove it before packaging: {path.relative_to(root)}")
            size = path.stat().st_size
            total += size
            if total > MAX_TOTAL_BYTES:
                raise ValueError("Project exceeds the 100 MiB uncompressed size limit.")
            files.append(path)
            if len(files) > MAX_FILES:
                raise ValueError("Project exceeds the 10,000-file limit.")
    if not any(path.name.lower() == "index.html" and path.parent == root for path in files):
        raise ValueError("A root-level index.html is required for a static web project.")
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def package_project(root: Path, output: Path) -> tuple[int, int]:
    root = root.resolve(strict=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    files = collect_files(root)
    output_resolved = output.resolve()
    if output_resolved == root or root in output_resolved.parents:
        raise ValueError("Output archive must be outside the project directory.")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
        for path in files:
            relative = PurePosixPath(path.relative_to(root).as_posix())
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Unsafe archive path detected.")
            archive.write(path, relative.as_posix())
    return len(files), sum(path.stat().st_size for path in files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Checked-out repository directory")
    parser.add_argument("--project-path", default=".", help="Project subdirectory containing index.html")
    parser.add_argument("--output", required=True, type=Path, help="Output ZIP path outside the project")
    args = parser.parse_args()
    try:
        source = args.source.resolve(strict=True)
        project = (source / args.project_path).resolve(strict=True)
        if project != source and source not in project.parents:
            raise ValueError("Project path must stay inside the checked-out repository.")
        count, size = package_project(project, args.output)
        print(f"Packaged {count} files ({size} bytes) into {args.output}")
        return 0
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"Packaging failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
