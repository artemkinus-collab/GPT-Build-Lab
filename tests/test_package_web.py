"""Security and behavior tests for the static web packager."""
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_web import collect_files, package_project


class PackageWebTests(unittest.TestCase):
    def make_project(self, base: Path) -> Path:
        project = base / "project"
        project.mkdir()
        (project / "index.html").write_text("<h1>Hello</h1>", encoding="utf-8")
        (project / "assets").mkdir()
        (project / "assets" / "site.css").write_text("body{}", encoding="utf-8")
        return project

    def test_creates_zip_with_root_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = self.make_project(base)
            output = base / "out" / "site.zip"
            count, size = package_project(project, output)
            self.assertEqual(count, 2)
            self.assertGreater(size, 0)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(set(archive.namelist()), {"index.html", "assets/site.css"})

    def test_requires_root_index_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            (project / "about.html").write_text("hello", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "root-level index.html"):
                collect_files(project)

    def test_rejects_secret_like_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.make_project(Path(tmp))
            (project / ".env").write_text("TOKEN=not-a-real-secret", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Potential secret file"):
                collect_files(project)

    def test_excludes_dependency_and_git_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.make_project(Path(tmp))
            (project / "node_modules").mkdir()
            (project / "node_modules" / "ignored.js").write_text("ignored", encoding="utf-8")
            (project / ".git").mkdir()
            (project / ".git" / "config").write_text("ignored", encoding="utf-8")
            paths = [p.relative_to(project).as_posix() for p in collect_files(project)]
            self.assertNotIn("node_modules/ignored.js", paths)
            self.assertNotIn(".git/config", paths)

    def test_rejects_symlink_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = self.make_project(base)
            outside = base / "outside.txt"
            outside.write_text("outside", encoding="utf-8")
            link = project / "linked.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks are not supported on this platform")
            with self.assertRaisesRegex(ValueError, "Symlinks are not allowed"):
                collect_files(project)


if __name__ == "__main__":
    unittest.main()
