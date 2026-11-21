# GPT Build Lab roadmap

This roadmap distinguishes shipped foundation from future work. A planned item is not available until its workflow has been implemented and tested.

## Phase 1 — Foundation (this commit series)

- [x] Establish project structure and security rules.
- [x] Add a dependency-free browser dashboard.
- [x] Save build-job drafts in browser localStorage.
- [x] Export one draft or all drafts as JSON.
- [x] Add a lightweight validation script.
- [x] Add GitHub Actions validation on push and pull request.

## Phase 2 — Web build pipeline

- [ ] Define a supported web-project input contract.
- [ ] Add a manually-triggered workflow with explicit inputs.
- [ ] Build and upload a web artifact.
- [ ] Show a link to the workflow run and artifact.

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

## Design constraints

- Never accept arbitrary shell commands from an unauthenticated web page.
- Do not expose GitHub tokens in client-side JavaScript.
- Keep privileged workflows separate from pull-request validation.
- Require explicit confirmation for release signing and deployment.
- Prefer least-privilege workflow permissions.
