# GPT Build Lab

A public cloud build workspace. The dashboard is published with GitHub Pages; controlled build jobs run separately in GitHub Actions.

> **Current stage:** Static Web ZIP packaging is available through GitHub Actions. Account/database integration scaffolding has been added, but it is not live until a Supabase project and secrets are configured. Android APK and Windows EXE compilation are not implemented yet.

## Open the dashboard

[GPT Build Lab](https://artemkinus-collab.github.io/GPT-Build-Lab/)

## Available: static Web ZIP packaging

The **Build Web Artifact** workflow accepts:
- A public GitHub repository in `owner/repository` form.
- A branch, tag, or commit reference.
- An optional project subfolder containing a root-level `index.html`.

To run it:
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

## Account and cloud build foundation

The repository now includes a Supabase schema for user-owned projects/build history and an authenticated Edge Function that queues the Web ZIP workflow. The workflow can report queued build status to Supabase when the required secrets are configured. Setup instructions and security boundaries are documented in [Account and Build Architecture](docs/ACCOUNT_AND_BUILD_ARCHITECTURE.md).

This integration is **not active on the public dashboard yet**: Supabase credentials, OAuth provider setup, and server-side GitHub secrets must be configured first. No credentials belong in the public page.

## Dashboard features

- Responsive Russian-language interface.
- Local draft management using browser `localStorage`.
- JSON import/export with validation.
- Direct links to the Web Build workflow and Actions history.

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

- `web/index.html` — public dashboard.
- `scripts/package_web.py` — safe static ZIP packager.
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
