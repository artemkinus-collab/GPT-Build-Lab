# GPT Build Lab

GPT Build Lab is a browser-based project workspace published with GitHub Pages. Static Web ZIP archives are created directly in the website, in the user's browser.

> **Current stage:** Static Web ZIP packaging is available directly on the website. Users can select files, a folder, or an existing ZIP and download the resulting archive without opening GitHub Actions. APK and Windows EXE compilation are not implemented yet.

## Open the dashboard

[GPT Build Lab](https://artemkinus-collab.github.io/GPT-Build-Lab/)

## Available: browser-based static Web ZIP packaging

The website's **ZIP-сборка** section accepts multiple files, a folder (where supported by the browser), or an existing ZIP archive.
- A public GitHub repository in `owner/repository` form.
- A branch, tag, or commit reference.
- An optional project subfolder containing a root-level `index.html`.

Open the site, go to **ZIP-сборка**, choose files/folder/ZIP, and press **Собрать ZIP**. The archive is downloaded directly to the device. Selected project files are not uploaded to a server.\n\nThe browser builder requires a root-level index.html, enforces file-count/size limits, excludes Git/dependency/cache folders, and blocks secret-like files. It does not run npm, shell scripts, build hooks, or project code.
1. Open [Build Web Artifact](https://github.com/artemkinus-collab/GPT-Build-Lab/actions/workflows/build-web.yml).
2. Select **Run workflow**.
3. Enter the public repository, ref, and project folder.
4. Wait for the workflow to finish successfully.
5. Download the ZIP from the run's **Artifacts** section.

The artifact is retained for 7 days. This workflow packages static files only: it does not run npm, shell scripts, build hooks, or other code from the submitted project.

### Packaging safeguards

- Requires a root-level `index.html` in the selected project folder.
- Rejects symbolic links and secret-like files such as `.env`, private key files, and keystores.
- Excludes dependency and Git metadata folders.
- Limits input to 10,000 files and 100 MiB uncompressed.
- Uses read-only repository permissions and does not persist checkout credentials.

Private source repositories are not supported by this first version. Use only source projects you are authorized to package.

## Account and profile foundation

The repository includes Supabase Auth integration for username/password accounts and private user profiles with RLS. Custom avatar images require applying migration 202611220002_profile_avatar_images.sql. Email recovery is deferred. To activate accounts, follow [Account Setup](docs/ACCOUNT_SETUP.md). Build automation still needs its separate server-side secrets; never put service-role keys or GitHub tokens in the public page.

## Dashboard features

- Responsive Russian-language interface.
- Local draft management using browser `localStorage`.
- JSON import/export with validation.
- Browser-based ZIP packaging without GitHub credentials or server uploads.

Drafts remain in the browser where they were created; they are not uploaded to GitHub.

## Run validation

Requires Python 3.12+; the JavaScript syntax check additionally requires Node.js.

```bash
python -m unittest discover -s tests -v
python scripts/check_inline_js.py
python scripts/validate.py
```

## Current limitations

- The Web pipeline packages static files; it does not compile JavaScript frameworks or run custom build commands.
- APK and EXE pipelines are planned, not available.
- The dashboard cannot trigger Actions directly because no GitHub token is embedded in the public page. Start the workflow in GitHub Actions.
- Build artifacts expire after 7 days.
- GitHub Pages and this repository are public. Never commit secrets, tokens, signing keys, passwords, or private data.

## Project structure

- `web/index.html` — public dashboard and browser ZIP builder.
- `web/auth.html` — username/password sign-in and registration.
- `web/supabase-config.js` — public Supabase URL and anon/publishable key placeholders.
- `scripts/package_web.py` — safe static ZIP packager for CI/internal workflows.
- `scripts/validate.py` — project sanity checks.
- `scripts/check_inline_js.py` — inline JavaScript syntax check.
- `tests/` — regression and packaging safety tests.
- `.github/workflows/` — validation, Pages deployment, and Web packaging workflows.

See [the roadmap](docs/ROADMAP.md) and [build matrix](config/build-matrix.json).

## Security principles

- Keep workflow permissions minimal.
- Never run untrusted source scripts in packaging jobs.
- Do not expose GitHub tokens in client-side JavaScript.
- Review workflow changes before adding privileged release or deployment steps.
