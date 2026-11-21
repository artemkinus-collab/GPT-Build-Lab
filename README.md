# GPT Build Lab

A small, transparent starting point for a cloud build workspace.

> **Current stage:** foundation / prototype. This repository does not yet build APK or EXE files. The dashboard currently manages local draft build jobs in the browser; actual cloud runners will be added in later phases.

## What is included

- **Web dashboard** in `web/index.html` — responsive, dependency-free interface.
- **Draft job manager** — create build-job drafts, persist them in the current browser using localStorage, and export a JSON job description.
- **Regression tests** in `tests/test_dashboard.py` — checks dashboard metadata, required controls, target configuration, honest capability labels, and security warnings.
- **Validation workflow** — GitHub Actions runs the regression tests and project validator on pushes and pull requests.
- **GitHub Pages workflow** — deploys the contents of `web/` when Pages is configured to use GitHub Actions.
- **Roadmap and build matrix** — clearly separates implemented features from planned integrations.

## Open the dashboard

The published site is intended to be available at [GPT Build Lab on GitHub Pages](https://artemkinus-collab.github.io/GPT-Build-Lab/) after Pages deployment succeeds. The source is in [web/index.html](web/index.html).

## Run checks locally

The checks use only Python's standard library:

```bash
python -m unittest discover -s tests -v
python scripts/validate.py
```

## Current limitations

- No APK/EXE compilation is performed yet.
- No cloud runner is provisioned or triggered by the dashboard.
- Draft jobs are stored only in the browser profile where they were created.
- Exported job JSON is a specification, not a runnable build artifact.
- A successful GitHub Pages deployment must be verified separately; having a workflow file alone does not publish the site.
- Do not put secrets in this public repository or in exported job files.

## Planned phases

1. Foundation, regression tests, and validation (current).
2. Connect a controlled GitHub Actions workflow to build a static web artifact.
3. Add Android SDK build runner for APK projects.
4. Add Windows runner for EXE projects.
5. Add test reports, artifact links, and deployment targets.

See [docs/ROADMAP.md](docs/ROADMAP.md) and [config/build-matrix.json](config/build-matrix.json).

## Security principles

- Use GitHub Actions secrets or environment-scoped secrets for credentials when integrations are introduced.
- Grant workflows the minimum permissions they need.
- Never commit private keys, access tokens, passwords, signing keys, or keystores.
- Review workflow changes before enabling privileged deployment or release actions.
