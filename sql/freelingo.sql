-- =========================
-- 📘 FreeLingo Database Schema
-- Database: freelingo
-- =========================

-- =========================
-- 📘 Table: known_words (Updated for React UI + Firebase)
-- =========================
create table public.known_words (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,  -- Firebase UID (not UUID)
  word text not null,
  translation text not null,
  example text,
  learned boolean default false,
  created_at timestamp with time zone default now()
);

-- No Row Level Security - backend handles user isolation
create index on public.known_words(user_id);
create index on public.known_words(user_id, learned);

-- =========================
-- 📊 Table: user_progress
-- =========================
create table public.user_progress (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,  -- Firebase UID (not UUID)
  dialogue_sessions integer default 0,
  streak_days integer default 0,
  last_activity timestamp with time zone default now(),
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- No Row Level Security - backend handles user isolation
create index on public.user_progress(user_id);

-- =========================
-- 🔄 Function: update_updated_at
-- =========================
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger update_user_progress_updated_at
  before update on public.user_progress
  for each row
  execute function update_updated_at_column();