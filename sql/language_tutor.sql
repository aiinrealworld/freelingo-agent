-- =========================
-- 📘 Table: known_words
-- =========================
create table public.known_words (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  word text not null,
  added_on timestamp with time zone default now()
);

alter table public.known_words enable row level security;

create policy "Users can access their own known words"
  on public.known_words
  for all
  using (auth.uid() = user_id);

create index on public.known_words(user_id);