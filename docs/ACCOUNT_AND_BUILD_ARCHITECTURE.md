# Accounts and browser ZIP builds

## Current user-facing architecture

- Frontend: GitHub Pages (web/).
- Identity and database: Supabase Auth + Postgres.
- Sign-in: username/password via Supabase Auth. Public signup uses the username-signup Edge Function; the synthetic internal email is not a recovery address.
- User-facing static Web ZIP packaging: JSZip in the browser.
- Public GitHub repository import: GitHub tree API + raw.githubusercontent.com, fetched directly by the browser.
- CI and Pages deployment: GitHub Actions.
- Legacy cloud build path: create-web-build Edge Function + build-web.yml. It is not required for user-facing ZIP packaging.

## Browser ZIP lifecycle

The user can:
1. Select local files, a folder, or an existing ZIP archive; or
2. Enter a public GitHub repository URL, branch/tag, and optional project subfolder.
3. For GitHub imports, the browser reads the repository tree through the public GitHub API and fetches file contents from raw.githubusercontent.com. Private repositories are not supported; no GitHub token is stored in the frontend.
4. The browser validates paths, root index.html, secret-like filenames, file count, and total size.
5. Git metadata, dependency folders, and caches are excluded.
6. JSZip generates the archive locally and the browser downloads it.

Selected local files and imported GitHub source files are not uploaded to Supabase or to a Build Lab server. Project scripts are never executed.

Limits: 10,000 files and 100 MiB of source/unpacked data. GitHub public API rate limits and browser CORS/network availability apply. This is static packaging, not a framework build system.

## Profile avatars

- Preset symbols and selected emoji are stored in profiles.avatar.
- Uploaded images are cropped and compressed in the browser to 128×128 JPEG data URLs.
- Apply supabase/migrations/202611220002_profile_avatar_images.sql once to allow the expanded avatar formats.
- Existing profile RLS continues to restrict updates to the authenticated user's own row.

## Existing Supabase setup

The existing username/password authentication setup remains unchanged. The avatar migration is additive; it does not recreate accounts or alter sign-in. Email recovery is deliberately deferred.

## Security constraints

- Never put service-role keys or GitHub tokens in web/index.html, browser storage, or public configuration.
- The browser ZIP builder does not transmit selected project files.
- Potential secrets are blocked from packaging; users should still inspect projects before sharing.
- Static packaging does not execute scripts, install dependencies, or run build hooks.
- Keep privileged GitHub workflows separate from pull-request validation.
