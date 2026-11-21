-- GPT Build Lab: account-scoped data model.
create extension if not exists pgcrypto;
create table if not exists public.projects (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 name text not null check (char_length(name) between 1 and 80),
 target text not null default 'web' check (target in ('web')),
 source_repository text not null check (source_repository ~ '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$'),
 source_ref text not null default 'main' check (char_length(source_ref) between 1 and 200),
 project_path text not null default '.' check (char_length(project_path) between 1 and 240),
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
create table if not exists public.builds (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 project_id uuid references public.projects(id) on delete set null,
 target text not null default 'web' check (target = 'web'),
 status text not null default 'queued' check (status in ('queued','running','succeeded','failed')),
 github_run_id bigint,
 artifact_name text,
 artifact_expires_at timestamptz,
 error_message text check (error_message is null or char_length(error_message) <= 2000),
 created_at timestamptz not null default now(),
 started_at timestamptz,
 completed_at timestamptz
);
create index if not exists projects_user_updated_idx on public.projects(user_id, updated_at desc);
create index if not exists builds_user_created_idx on public.builds(user_id, created_at desc);
create index if not exists builds_project_created_idx on public.builds(project_id, created_at desc);
alter table public.projects enable row level security;
alter table public.builds enable row level security;
create policy "Users can read their projects" on public.projects for select to authenticated using (auth.uid() = user_id);
create policy "Users can create their projects" on public.projects for insert to authenticated with check (auth.uid() = user_id);
create policy "Users can update their projects" on public.projects for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Users can delete their projects" on public.projects for delete to authenticated using (auth.uid() = user_id);
create policy "Users can read their builds" on public.builds for select to authenticated using (auth.uid() = user_id);
-- Build rows are created/updated only by trusted server-side code using the service-role key.
