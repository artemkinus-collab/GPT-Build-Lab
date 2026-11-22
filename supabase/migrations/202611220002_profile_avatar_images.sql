-- Allow profile avatars to be preset symbols, selected emoji, or compressed image data URLs.
-- Image payloads are resized/compressed by the browser before being stored.
alter table public.profiles
  drop constraint if exists profiles_avatar_check;

alter table public.profiles
  add constraint profiles_avatar_check
  check (
    char_length(avatar) <= 160000
    and (
      avatar in (
        '✦','◈','●','⚡','❋','☾','狐',
        '🐱','🐼','🐸','🚀','🎮','🌙','🦊','💎'
      )
      or avatar ~ '^data:image/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$'
    )
  );
