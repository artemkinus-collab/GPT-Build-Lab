# GPT Build Lab — Cloud architecture

## Selected stack
- Frontend: existing static site on GitHub Pages.
- Authentication and database: Supabase Auth + PostgreSQL.
- Providers: email/password and GitHub OAuth. Each user has a unique username in the profiles table; credentials remain inside Supabase Auth.
- Build execution: GitHub Actions, initially static Web ZIP packaging only.
- Private orchestration: Supabase Edge Functions. GitHub tokens and callback secrets are server-side secrets, never browser code.
- Build output: GitHub Actions artifact.

## Data ownership
profiles.id, projects.owner_id, and builds.owner_id refer to auth.users.id. Row Level Security restricts users to their own profile, projects, and build history. Build creation and status updates are performed by trusted Edge Functions.

## Build lifecycle
1. An authenticated user calls start-build.
2. The function validates repository, ref, and relative project path.
3. It creates a per-user build row with status queued.
4. It dispatches Build Web Artifact using a server-side GitHub token.
5. The workflow packages public static project files without executing project scripts.
6. A final workflow step calls build-callback with the build ID and a server-side callback secret.
7. The dashboard reads only the authenticated user's build rows.

## Required one-time setup
1. Create a Supabase project.
2. Run supabase/schema.sql in the Supabase SQL editor.
3. Enable Email provider and GitHub provider in Supabase Auth. Configure the GitHub OAuth callback URL shown by Supabase.
4. Deploy the two Edge Functions.
5. Configure Edge Function secrets: GITHUB_TOKEN (fine-grained token limited to this repository; Actions read/write and Contents read), GITHUB_OWNER=artemkinus-collab, GITHUB_REPO=GPT-Build-Lab, BUILD_CALLBACK_SECRET (long random secret), APP_ORIGIN=https://artemkinus-collab.github.io.
6. Configure GitHub Actions repository secret BUILD_CALLBACK_SECRET with the same value, and repository variable SUPABASE_FUNCTIONS_URL with the project's functions base URL.
7. Configure frontend with Supabase project URL and public anon key. The anon key is public; service-role keys and GitHub tokens are not.
8. Add the Supabase redirect URLs for the GitHub Pages domain.

## Important limitations
- This is an integration foundation, not a deployed service. No Supabase project, OAuth app, token, or secrets have been configured by this repository change.
- Email/password authentication uses email as the authentication identifier. Username is the unique public profile handle. Username-only sign-in needs a separate carefully designed server-side lookup.
- First target is Web ZIP. No framework build commands, APKs, or EXEs are supported yet.
- Private source repositories are not supported by the current packager.
- Never put credentials in GitHub Pages, source files, browser storage, or public repository JSON files.
