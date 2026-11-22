# Accounts and browser ZIP builds

## Selected architecture
- Frontend: GitHub Pages (web/).
- Identity and database: Supabase Auth + Postgres.
- Sign-in: username/password via Supabase Auth (username is mapped to an internal synthetic email address); public signup is handled by the `username-signup` Edge Function with Admin API and does not send confirmation email; GitHub OAuth is deferred.
- Build runner: GitHub Actions in this repository.
- Artifact: GitHub Actions artifact (initially 7-day retention).
- Trusted bridge: Supabase Edge Function create-web-build. No GitHub credential is sent to the browser.

## Request lifecycle
1. A signed-in user submits a public source repository, ref, and safe relative project folder.
2. The Edge Function validates the Supabase access token and request fields.
3. It creates a builds row owned by auth.uid().
4. It calls GitHub workflow_dispatch using a server-side secret.
5. The workflow updates the build row to running, succeeded, or failed.
6. The browser reads only rows permitted by Postgres Row Level Security (RLS).

## Required setup (not committed)
Create a Supabase project and:
- The existing username/password authentication setup remains unchanged. Apply supabase/migrations/202611220002_profile_avatar_images.sql once to allow custom compressed avatar images.
- Configure web/supabase-config.js with the public Project URL and anon/publishable key.
- Deploy `supabase/functions/username-signup` with JWT verification disabled for the public signup endpoint. Keep the service-role key in Edge Function secrets only.\n- Apply `supabase/migrations/202611220001_signup_rate_limit.sql` to enable a five-attempts-per-hour-per-IP registration limit.\n- Email confirmation can remain enabled: the signup function creates users as confirmed and does not send confirmation email.
- Follow docs/ACCOUNT_SETUP.md for the complete setup and verification checklist.
- Enable the Email provider in Supabase Auth. GitHub OAuth is not part of the current username/password release.
- Deploy supabase/functions/create-web-build.
- Set Edge Function secrets: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, GPT_BUILD_LAB_GITHUB_TOKEN, GPT_BUILD_LAB_REPOSITORY=artemkinus-collab/GPT-Build-Lab, ALLOWED_ORIGIN=https://artemkinus-collab.github.io.
- Add GitHub Actions repository secrets SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY for workflow status callbacks.
- The GitHub token must be fine-grained, restricted to this repository, with Actions: write and Contents: read.

Never put service-role keys or GitHub tokens in web/index.html, committed config, browser storage, or client-side environment variables.

## Current scope and limitations
- The first pipeline packages static websites only; it does not execute submitted scripts or install dependencies.
- Only public GitHub source repositories are supported initially.
- Browser ZIP packaging is limited to static sites with root-level index.html; framework build commands and dependency installation are not supported.
- Add CAPTCHA/bot protection before opening registration widely. The username signup endpoint currently applies a basic IP rate limit; monitor it and adjust carefully.
- GitHub OAuth is deferred; no OAuth callback is needed for this release.

## Next steps
1. Deploy schema and Edge Function; configure server-side secrets for ZIP build dispatch separately from the public account client.
2. Configure Supabase and complete the account smoke test described in docs/ACCOUNT_SETUP.md.
3. Add per-user project CRUD and build history.
4. Add authenticated build creation and status refresh.
5. Add secure artifact download.
6. Run an end-to-end test with a harmless public static-site repository.
7. Then start Windows EXE support.
