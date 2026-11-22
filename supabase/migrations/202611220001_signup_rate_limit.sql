-- Rate-limit public username registrations by source IP.
-- Only the server-side Edge Function (service_role) may call the RPC.
create table if not exists public.gbl_signup_rate_limits (
  ip_hash text primary key,
  attempts integer not null default 0 check (attempts >= 0),
  window_started_at timestamptz not null default now()
);

alter table public.gbl_signup_rate_limits enable row level security;
revoke all on public.gbl_signup_rate_limits from public, anon, authenticated;
grant all on public.gbl_signup_rate_limits to service_role;

create or replace function public.gbl_consume_signup_attempt(p_ip_hash text)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  current_attempts integer;
begin
  if p_ip_hash is null or length(p_ip_hash) <> 64 then
    return false;
  end if;

  insert into public.gbl_signup_rate_limits (ip_hash, attempts, window_started_at)
  values (p_ip_hash, 1, now())
  on conflict (ip_hash) do update
    set attempts = case
      when public.gbl_signup_rate_limits.window_started_at < now() - interval '1 hour' then 1
      else public.gbl_signup_rate_limits.attempts + 1
    end,
    window_started_at = case
      when public.gbl_signup_rate_limits.window_started_at < now() - interval '1 hour' then now()
      else public.gbl_signup_rate_limits.window_started_at
    end
  returning attempts into current_attempts;

  return current_attempts <= 5;
end;
$$;

revoke all on function public.gbl_consume_signup_attempt(text) from public, anon, authenticated;
grant execute on function public.gbl_consume_signup_attempt(text) to service_role;
