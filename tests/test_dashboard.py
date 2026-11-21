"""Regression tests for the GPT Build Lab starter dashboard."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "web" / "index.html"
MATRIX = ROOT / "config" / "build-matrix.json"


class DashboardAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.forms = []
        self.buttons = []
        self.title = False
        self.lang = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "title":
            self.title = True
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "form":
            self.forms.append(attrs)
        if tag == "button":
            self.buttons.append(attrs)


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = DASHBOARD.read_text(encoding="utf-8")
        cls.audit = DashboardAudit()
        cls.audit.feed(cls.html)
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

    def test_html_document_has_metadata(self):
        self.assertIn("<!doctype html>", self.html.lower())
        self.assertTrue(self.audit.title)
        self.assertEqual(self.audit.lang, "en")
        self.assertIn('name="viewport"', self.html)

    def test_dashboard_has_unique_required_ids(self):
        self.assertEqual(len(self.audit.ids), len(set(self.audit.ids)))
        for required in ("jobForm", "jobs", "jobCount", "exportAll", "importDrafts", "importFile"):
            self.assertIn(required, self.audit.ids)

    def test_build_matrix_has_unique_targets(self):
        targets = self.matrix["targets"]
        ids = [target["id"] for target in targets]
        self.assertGreaterEqual(len(ids), 3)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("web", ids)
        self.assertIn("android-apk", ids)
        self.assertIn("windows-exe", ids)

    def test_planned_targets_are_not_misrepresented_as_ready(self):
        targets = {item["id"]: item for item in self.matrix["targets"]}
        self.assertEqual(targets["android-apk"]["status"], "planned")
        self.assertEqual(targets["windows-exe"]["status"], "planned")
        self.assertEqual(targets["web"]["status"], "prototype")

    def test_dashboard_discloses_no_compilation_yet(self):
        self.assertIn("does not claim to compile apps yet", self.html)
        self.assertIn("Cloud compilation:", self.html)
        self.assertIn("Not connected", self.html)

    def test_json_import_is_bounded_and_validated(self):
        self.assertIn("file.size > 1024 * 1024", self.html)
        self.assertIn("incoming.length > 100", self.html)
        self.assertIn('["web", "android-apk", "windows-exe"]', self.html)
        self.assertIn('confirm("Import "', self.html)

    def test_dashboard_warns_against_entering_secrets(self):
        for phrase in ("access tokens", "private keys", "signing keys"):
            self.assertIn(phrase, self.html)


if __name__ == "__main__":
    unittest.main()
