# GPT Build Lab roadmap

## Phase 1 — Dashboard foundation

- [x] Responsive Russian-language dashboard.
- [x] Local project drafts and JSON import/export.
- [x] Account sign-in/sign-up interface and Supabase profile integration.
- [x] Grouped settings and session controls.
- [x] Fix initial auth visibility and subscribe to auth state changes before loading the session.
- [x] Move avatar settings into the Account section.
- [x] Preset avatars, emoji selection, and compressed image upload.
- [x] CI checks and GitHub Pages publishing.

## Phase 2 — Static Web ZIP

- [x] Add a dedicated ZIP Builder section to the website.
- [x] Select multiple files or a project folder.
- [x] Accept an existing ZIP as input.
- [x] Validate root-level index.html, paths, secret-like files, file count, and size.
- [x] Exclude Git metadata, dependencies, and cache folders.
- [x] Generate and download ZIP locally in the browser without uploading source files.
- [ ] Test the builder on Android Chrome and desktop browsers with representative projects.
- [ ] Add optional GitHub repository import without exposing credentials.

## Phase 3 — Account and project sync

- [x] Supabase Auth username/password integration.
- [x] Per-user profile with Row Level Security.
- [x] Expand avatar storage to support compressed images.
- [ ] Apply the avatar-format migration in the live Supabase project.
- [ ] Add cloud project CRUD and build history.
- [ ] Design optional verified email and password recovery (deferred).

## Phase 4 — Android APK pipeline

- [ ] Select supported Android project formats (initially Gradle).
- [ ] Configure Android SDK and Java versions.
- [ ] Build debug APK first; add release signing only through protected secrets.
- [ ] Upload APK and build logs as artifacts.
- [ ] Add clear failure diagnostics.

## Phase 5 — Windows EXE pipeline

- [ ] Select supported source project formats and toolchains.
- [ ] Use a Windows hosted runner.
- [ ] Package output and upload artifacts.
- [ ] Add tests and build logs.

## Phase 6 — Test Center and deployment

- [ ] Define project-specific test commands.
- [ ] Collect test reports.
- [ ] Add opt-in deployment targets and approval gates.
- [ ] Document artifact retention and runner quotas.

## Design and security constraints

- Never accept arbitrary shell commands from the public dashboard.
- Never expose GitHub tokens in client-side JavaScript.
- Do not execute untrusted project scripts in the static packaging feature.
- Keep privileged workflows separate from pull-request validation.
- Require explicit confirmation for release signing and deployment.
