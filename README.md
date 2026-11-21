# GPT Build Lab

A small, transparent starting point for a cloud build workspace.

> **Current stage:** foundation / prototype. This repository does not yet build APK or EXE files. The dashboard currently manages local draft build jobs in the browser; actual cloud runners will be added in later phases.

## What is included

- **Web dashboard** in `web/index.html` — responsive, dependency-free interface.
- **Draft job manager** — create build-job drafts, persist them in the current browser using localStorage, and export a JSON job description.
- **Validation workflow** — GitHub Actions checks the dashboard and project configuration on pushes and pull requests.
- **Roadmap and build matrix** — clearly separates implemented features from planned integrations.

## Open the dashboard

Open [web/index.html](web/index.html) in a modern browser. No server, package installation, or API key is required for this prototype.

## Current limitations

- No APK/EXE compilation is performed yet.
- No cloud runner is provisioned or triggered by the dashboard.
- Draft jobs are stored only in the browser profile where they were created.
- Exported job JSON is a specification, not a runnable build artifact.
- Do not put secrets in this public repository or in exported job files.

## Planned phases

1. Foundation and validation (current).
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
