-- Username-based accounts for GPT Build Lab.
-- Passwords remain exclusively in Supabase Auth; never store them in public tables.
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text not null unique,
  avatar text not null default '✦' check (avatar in ('✦','◈','●','⚡','❋')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint profiles_username_format check (username ~ '^[a-z0-9_.-]{3,24}$')
);

create or replace function public.gbl_handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  requested_username text;
begin
  requested_username := lower(coalesce(new.raw_user_meta_data ->> 'username', ''));
  if requested_username !~ '^[a-z0-9_.-]{3,24}$' then
    raise exception 'Username must be 3-24 characters and use lowercase letters, numbers, dot, underscore or hyphen';
  end if;
  insert into public.profiles (id, username)
  values (new.id, requested_username);
  return new;
end;
$$;

drop trigger if exists gbl_on_auth_user_created on auth.users;
create trigger gbl_on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.gbl_handle_new_user();

create or replace function public.gbl_set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists gbl_profiles_updated_at on public.profiles;
create trigger gbl_profiles_updated_at
  before update on public.profiles
  for each row execute procedure public.gbl_set_updated_at();

alter table public.profiles enable row level security;
drop policy if exists "Users can read their own profile" on public.profiles;
create policy "Users can read their own profile"
  on public.profiles for select to authenticated
  using (auth.uid() = id);
drop policy if exists "Users can update their own profile" on public.profiles;
create policy "Users can update their own profile"
  on public.profiles for update to authenticated
  using (auth.uid() = id)
  with check (auth.uid() = id);

grant select, update on public.profiles to authenticated;
