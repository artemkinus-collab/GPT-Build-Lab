# Accounts and cloud ZIP builds

## Selected architecture
- Frontend: GitHub Pages (web/).
- Identity and database: Supabase Auth + Postgres.
- Sign-in: email/password and GitHub OAuth.
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
- Apply supabase/migrations/202611210001_initial_schema.sql.
- Enable Email and GitHub OAuth providers in Supabase Auth.
- Deploy supabase/functions/create-web-build.
- Set Edge Function secrets: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, GPT_BUILD_LAB_GITHUB_TOKEN, GPT_BUILD_LAB_REPOSITORY=artemkinus-collab/GPT-Build-Lab, ALLOWED_ORIGIN=https://artemkinus-collab.github.io.
- Add GitHub Actions repository secrets SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY for workflow status callbacks.
- The GitHub token must be fine-grained, restricted to this repository, with Actions: write and Contents: read.

Never put service-role keys or GitHub tokens in web/index.html, committed config, browser storage, or client-side environment variables.

## Current scope and limitations
- The first pipeline packages static websites only; it does not execute submitted scripts or install dependencies.
- Only public GitHub source repositories are supported initially.
- Successful ZIPs are Actions artifacts; direct authenticated download from the dashboard is a follow-up.
- Register the Supabase OAuth callback URL in the GitHub OAuth App and configure Supabase allowed redirect URLs.
- Configure rate limits and email confirmation before public registration.

## Next steps
1. Deploy schema and Edge Function; configure secrets and OAuth.
2. Add Supabase client configuration and account UI to the dashboard.
3. Add per-user project CRUD and build history.
4. Add authenticated build creation and status refresh.
5. Add secure artifact download.
6. Run an end-to-end test with a harmless public static-site repository.
7. Then start Windows EXE support.
