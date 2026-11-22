"""Regression tests for the current GPT Build Lab dashboard."""
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
        self.assertEqual(self.audit.lang, "ru")
        self.assertIn('name="viewport"', self.html)

    def test_dashboard_has_unique_required_ids(self):
        self.assertEqual(len(self.audit.ids), len(set(self.audit.ids)))
        for required in ("projectForm", "draftList", "searchDrafts", "importFile",
                         "projectModal", "authOpen", "accountWrap", "accountOpen", "accountMenu", "statTotal"):
            self.assertIn(required, self.audit.ids)

    def test_account_entry_points_are_visible(self):
        self.assertIn('href="auth.html"', self.html)
        self.assertIn('id="accountOpen"', self.html)
        self.assertIn('id="accountMenu"', self.html)
        self.assertIn('id="accountSignOut"', self.html)
        self.assertNotIn('id="authSignOut"', self.html)
        self.assertNotIn('id="authModal"', self.html)
        self.assertNotIn('id="newProjectTop"', self.html)

    def test_settings_are_grouped_and_avatar_is_customizable(self):
        for section in ("appearance", "account", "data", "advanced"):
            self.assertIn('data-settings-section="' + section + '"', self.html)
            self.assertIn('data-settings-panel="' + section + '"', self.html)
        self.assertIn('data-avatar="✦"', self.html)
        self.assertIn('data-avatar="⚡"', self.html)

    def test_dedicated_auth_page_uses_username_and_password(self):
        auth = (ROOT / "web" / "auth.html").read_text(encoding="utf-8")
        self.assertIn('id="username"', auth)
        self.assertIn('id="password"', auth)
        self.assertIn('id="confirmPassword"', auth)
        self.assertIn("Зарегистрироваться", auth)
        self.assertIn("Сервер аккаунтов не настроен", auth)
        self.assertNotIn('type="email"', auth)
        self.assertNotIn("localStorage.setItem", auth)

    def test_supabase_account_integration_is_wired(self):
        auth = (ROOT / "web" / "auth.html").read_text(encoding="utf-8")
        config = (ROOT / "web" / "supabase-config.js").read_text(encoding="utf-8")
        migration = (ROOT / "supabase" / "migrations" / "202611210002_username_accounts.sql").read_text(encoding="utf-8")
        self.assertIn('functions.invoke("username-signup"', auth)
        self.assertIn("signInWithPassword", auth)
        self.assertIn("@gptbuildlab.example.com", auth)
        self.assertIn("supabase-config.js", auth)
        self.assertIn("GBL_SUPABASE_CONFIG", config)
        edge = (ROOT / "supabase" / "functions" / "username-signup" / "index.ts").read_text(encoding="utf-8")
        self.assertIn("email_confirm: true", edge)
        self.assertIn('Deno.env.get("GBL_SUPABASE_SECRET_KEY")', edge)
        self.assertNotIn("SUPABASE_SERVICE_ROLE_KEY", edge)
        self.assertNotIn("SUPABASE_SERVICE_ROLE_KEY", config)
        self.assertIn("create table if not exists public.profiles", migration)
        self.assertIn("enable row level security", migration.lower())
        self.assertIn("profiles_username_format", migration)
        self.assertNotIn("service_role_key =", config.lower())
        self.assertNotIn("sb_secret_", config.lower())
        self.assertIn("refreshAccount", self.html)
        self.assertIn("auth.onAuthStateChange", self.html)

    def test_navigation_order_and_custom_dropdowns(self):
        order = ['data-page="home"', 'data-page="drafts"', 'data-page="statistics"',
                 'data-page="github"', 'data-page="settings"', 'data-page="about"']
        positions = [self.html.index(item) for item in order]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('data-select="filterTarget"', self.html)
        self.assertNotIn("<select", self.html.lower())

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
        self.assertEqual(targets["web"]["status"], "available")

    def test_dashboard_discloses_real_build_scope(self):
        self.assertIn("Упаковка статических сайтов", self.html)
        self.assertIn("Сборка APK и EXE", self.html)
        self.assertIn("не запускает пользовательские скрипты", self.html)

    def test_json_import_is_bounded_and_validated(self):
        self.assertIn("f.size>1024*1024", self.html)
        self.assertIn("arr.length>100", self.html)
        self.assertIn('["web","android-apk","windows-exe"]', self.html)
        self.assertIn('confirm("Добавить "+incoming.length', self.html)

    def test_dashboard_warns_against_entering_secrets(self):
        for phrase in ("GitHub", "приватные ключи", "keystore"):
            self.assertIn(phrase, self.html)


if __name__ == "__main__":
    unittest.main()
