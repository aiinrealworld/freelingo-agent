-- =========================
-- 📘 FreeLingo Database Schema
-- Database: freelingo
-- =========================

-- =========================
-- 📘 Table: words (Updated for React UI + Firebase)
-- =========================
create table public.words (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,  -- Firebase UID (not UUID)
  word text not null,
  translation text not null,
  example text,
  created_at timestamp with time zone default now()
);

-- No Row Level Security - backend handles user isolation
create index on public.words(user_id);

-- =========================
-- 📘 Table: dialogue_sessions
-- =========================
create table public.dialogue_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  messages jsonb not null,
  started_at timestamp with time zone,
  ended_at timestamp with time zone,
  created_at timestamp with time zone default now()
);

create index on public.dialogue_sessions(user_id);