-- GPT Build Lab cloud data model.
-- Credentials stay in Supabase Auth; this schema never stores passwords.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text not null unique check (char_length(username) between 3 and 24),
  created_at timestamptz not null default now()
);
create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 80),
  source_repository text not null,
  source_ref text not null default 'main',
  project_path text not null default '.',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.builds (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  project_id uuid references public.projects(id) on delete set null,
  target text not null default 'web-zip' check (target in ('web-zip')),
  status text not null default 'queued' check (status in ('queued','preparing','building','completed','failed','cancelled')),
  source_repository text not null,
  source_ref text not null,
  project_path text not null default '.',
  workflow_run_id bigint,
  workflow_url text,
  artifact_name text,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists projects_owner_updated_idx on public.projects(owner_id, updated_at desc);
create index if not exists builds_owner_created_idx on public.builds(owner_id, created_at desc);

alter table public.profiles enable row level security;
alter table public.projects enable row level security;
alter table public.builds enable row level security;
create policy "profiles_read_own" on public.profiles for select to authenticated using (auth.uid() = id);
create policy "profiles_insert_own" on public.profiles for insert to authenticated with check (auth.uid() = id);
create policy "profiles_update_own" on public.profiles for update to authenticated using (auth.uid() = id) with check (auth.uid() = id);
create policy "projects_read_own" on public.projects for select to authenticated using (auth.uid() = owner_id);
create policy "projects_insert_own" on public.projects for insert to authenticated with check (auth.uid() = owner_id);
create policy "projects_update_own" on public.projects for update to authenticated using (auth.uid() = owner_id) with check (auth.uid() = owner_id);
create policy "projects_delete_own" on public.projects for delete to authenticated using (auth.uid() = owner_id);
create policy "builds_read_own" on public.builds for select to authenticated using (auth.uid() = owner_id);
-- Build rows are created/updated only by trusted Edge Functions using the service role.

-- Create a profile after signup. A generated suffix avoids collisions between providers.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  requested_name text;
  safe_name text;
begin
  requested_name := coalesce(
    new.raw_user_meta_data ->> 'username',
    new.raw_user_meta_data ->> 'user_name',
    split_part(coalesce(new.email, 'member'), '@', 1)
  );
  safe_name := regexp_replace(lower(requested_name), '[^a-z0-9_-]', '', 'g');
  safe_name := left(coalesce(nullif(safe_name, ''), 'member'), 15) || '_' || left(replace(new.id::text, '-', ''), 8);
  insert into public.profiles (id, username) values (new.id, safe_name)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
