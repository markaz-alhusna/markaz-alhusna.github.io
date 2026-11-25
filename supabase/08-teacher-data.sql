-- AL-HUSNA: личные данные учителя (учебные материалы, «О себе», настройки).
-- Вставить целиком в Supabase → SQL Editor → New query → Run.
-- Можно запускать повторно: ничего не сломается и не удалится.

create table if not exists public.teacher_data (
  id         text primary key references public.members(id) on delete cascade,
  data       jsonb not null default '{}'::jsonb check (octet_length(data::text) < 300000),
  updated_at timestamptz not null default now()
);

drop trigger if exists touch on public.teacher_data;
create trigger touch before update on public.teacher_data for each row execute function public.touch_updated_at();

alter table public.teacher_data enable row level security;
revoke all on public.teacher_data from anon;

drop policy if exists teacher_data_read   on public.teacher_data;
drop policy if exists teacher_data_insert on public.teacher_data;
drop policy if exists teacher_data_update on public.teacher_data;
drop policy if exists teacher_data_delete on public.teacher_data;
-- Учитель видит и меняет только свою строку; админы видят все.
create policy teacher_data_read on public.teacher_data for select to authenticated
  using (id = public.my_id() or public.is_admin());
create policy teacher_data_insert on public.teacher_data for insert to authenticated
  with check (id = public.my_id() and public.is_staff());
create policy teacher_data_update on public.teacher_data for update to authenticated
  using (id = public.my_id()) with check (id = public.my_id());
create policy teacher_data_delete on public.teacher_data for delete to authenticated
  using (id = public.my_id() or public.is_admin());

grant select, insert, update, delete on public.teacher_data to authenticated;
