-- Enum per i tipi di transazione
create type transaction_type as enum ('gift_card_added', 'order_placed');

-- Tabella account Amazon
create table amazon_account (
  id serial primary key,
  display_name text not null unique,
  notes text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Tabella transazioni
create table transaction (
  id serial primary key,
  account_id int references amazon_account(id) on delete cascade not null,
  user_id uuid references auth.users(id),
  trans_date date not null,
  trans_type transaction_type not null,
  code text,
  country varchar(2) not null,
  value numeric(10,2) not null check (value >= 0),
  created_at timestamptz default now()
);

create index idx_transaction_account_id on transaction(account_id);
create index idx_transaction_trans_date on transaction(trans_date);
create index idx_transaction_country on transaction(country);
create index idx_transaction_user_id on transaction(user_id);

-- Materialized view
create materialized view account_balances_by_country as
select
    aa.id as account_id,
    aa.display_name,
    aa.notes,
    aa.updated_at as last_account_update,
    t.country,
    coalesce(sum(case when t.trans_type = 'gift_card_added' then t.value else 0 end), 0) as total_gift_cards,
    coalesce(sum(case when t.trans_type = 'order_placed' then t.value else 0 end), 0) as total_orders,
    coalesce(sum(case when t.trans_type = 'gift_card_added' then t.value else -t.value end), 0) as balance
from
    amazon_account aa
left join
    transaction t on aa.id = t.account_id
group by
    aa.id, aa.display_name, aa.notes, aa.updated_at, t.country;

create unique index uidx_account_balances_country on account_balances_by_country(account_id, country);

-- Function & trigger per refresh vista
create or replace function refresh_account_balances_view()
returns trigger language plpgsql as $$
begin
    refresh materialized view concurrently account_balances_by_country;
    return null;
end $$;

create trigger refresh_account_balances_after_transaction
after insert or update or delete on transaction
for each statement execute function refresh_account_balances_view();

create or replace function refresh_account_balances_view_after_account_update()
returns trigger language plpgsql as $$
begin
    refresh materialized view concurrently account_balances_by_country;
    return null;
end $$;

create trigger refresh_account_balances_after_account_update
after update on amazon_account
for each row
when (old.display_name is distinct from new.display_name or old.notes is distinct from new.notes)
execute function refresh_account_balances_view_after_account_update();

-- Timestamp trigger
create or replace function trigger_set_timestamp()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger set_amazon_account_updated_at
before update on amazon_account
for each row
execute function trigger_set_timestamp();
