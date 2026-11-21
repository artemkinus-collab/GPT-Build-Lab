# GPT Build Lab roadmap

This roadmap separates available features from planned integrations.

## Phase 1 — Foundation

- [x] Establish project structure and security rules.
- [x] Build a responsive browser dashboard.
- [x] Save build-job drafts in browser localStorage.
- [x] Export and import JSON backups with validation.
- [x] Add dashboard and packaging regression tests.
- [x] Check inline JavaScript syntax in CI.
- [x] Add GitHub Actions validation on push and pull request.
- [x] Publish the dashboard through GitHub Pages.

## Phase 2 — Static Web packaging

- [x] Define supported input: public GitHub repository, ref, and optional project folder.
- [x] Add a manually-triggered workflow with explicit inputs.
- [x] Require root-level index.html.
- [x] Reject symlinks and secret-like files.
- [x] Apply file-count and uncompressed-size limits.
- [x] Package static assets into a ZIP artifact.
- [x] Upload the artifact with a 7-day retention period.
- [ ] Verify a real test repository end-to-end and record the run result.

## Phase 2.5 — Accounts and dashboard-triggered Web builds

- [x] Design Supabase Auth + Postgres account architecture.
- [x] Add per-user projects/builds schema with Row Level Security.
- [x] Add authenticated Edge Function to dispatch Web ZIP jobs.
- [x] Add workflow callbacks for queued build status updates.
- [ ] Create Supabase project, configure Email + GitHub OAuth, and deploy schema/function.
- [ ] Configure server-side GitHub/Supabase secrets.
- [ ] Add sign-in/sign-up UI and connect dashboard project storage.
- [ ] Show per-user build history and live status refresh.
- [ ] Provide authenticated artifact download from the dashboard.
- [ ] Verify full end-to-end flow with a test repository.

## Phase 3 — Android APK pipeline

- [ ] Select supported Android project formats (initially Gradle).
- [ ] Configure Android SDK and Java versions.
- [ ] Build debug APK first; add release signing only through protected secrets.
- [ ] Upload APK and build logs as workflow artifacts.
- [ ] Add clear failure diagnostics.

## Phase 4 — Windows EXE pipeline

- [ ] Select supported source project formats and toolchains.
- [ ] Use a Windows hosted runner.
- [ ] Package output and upload artifacts.
- [ ] Add tests and build logs.

## Phase 5 — Test Center and deployment

- [ ] Define project-specific test commands.
- [ ] Collect test reports.
- [ ] Add opt-in deployment targets and approval gates.
- [ ] Document artifact retention and runner quotas.

## Design and security constraints

- Never accept arbitrary shell commands from the public dashboard.
- Never expose GitHub tokens in client-side JavaScript.
- Do not execute untrusted project scripts in the static packaging workflow.
- Keep privileged workflows separate from pull-request validation.
- Require explicit confirmation for release signing and deployment.
- Prefer least-privilege workflow permissions.
