-- ============================================================
-- Market Risk BI Training -- Supabase schema
--
-- Run this once in your Supabase project: SQL Editor -> New query
-- -> paste -> Run.
--
-- Creates the per-user progress table and the row-level security
-- policies that let each signed-in user read and write only their
-- own progress rows.
-- ============================================================

-- 1. Table -----------------------------------------------------------------
create table if not exists public.user_progress (
  user_id      uuid                     not null references auth.users (id) on delete cascade,
  module_id    text                     not null,
  completed_at timestamp with time zone not null default now(),
  primary key (user_id, module_id)
);

-- Fast lookups by user.
create index if not exists user_progress_user_id_idx
  on public.user_progress (user_id);

-- 2. Row-level security ----------------------------------------------------
alter table public.user_progress enable row level security;

-- A user can read their own rows.
drop policy if exists "user_progress_select_own" on public.user_progress;
create policy "user_progress_select_own"
  on public.user_progress
  for select
  using (auth.uid() = user_id);

-- A user can insert rows for themselves.
drop policy if exists "user_progress_insert_own" on public.user_progress;
create policy "user_progress_insert_own"
  on public.user_progress
  for insert
  with check (auth.uid() = user_id);

-- A user can update their own rows.
drop policy if exists "user_progress_update_own" on public.user_progress;
create policy "user_progress_update_own"
  on public.user_progress
  for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- A user can delete their own rows (used for "Mark as incomplete").
drop policy if exists "user_progress_delete_own" on public.user_progress;
create policy "user_progress_delete_own"
  on public.user_progress
  for delete
  using (auth.uid() = user_id);
