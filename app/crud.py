from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, update
from decimal import Decimal
from typing import List, Optional, Dict
from datetime import date

from app import models, schemas

# --- Account CRUD ---
async def create_amazon_account(db: AsyncSession, account: schemas.AmazonAccountCreate):
    db_account = models.AmazonAccount(**account.model_dump())
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    return db_account

async def get_amazon_accounts(db: AsyncSession, skip=0, limit=100):
    res = await db.execute(select(models.AmazonAccount).offset(skip).limit(limit))
    return res.scalars().all()

async def get_amazon_account_by_id(db: AsyncSession, account_id: int):
    res = await db.execute(select(models.AmazonAccount).filter(models.AmazonAccount.id == account_id))
    return res.scalars().first()

# --- Transaction CRUD ---
async def add_transaction(db: AsyncSession, transaction: schemas.TransactionCreate):
    account = await get_amazon_account_by_id(db, transaction.account_id)
    if not account:
        raise ValueError("Account not found.")
    db_tx = models.Transaction(**transaction.model_dump())
    db.add(db_tx)
    await db.commit()
    await db.refresh(db_tx)
    return db_tx

async def get_transactions_for_account(db: AsyncSession, account_id: int, start_date=None, end_date=None, skip=0, limit=20):
    q = select(models.Transaction).filter(models.Transaction.account_id == account_id)
    if start_date:
        q = q.filter(models.Transaction.trans_date >= start_date)
    if end_date:
        q = q.filter(models.Transaction.trans_date <= end_date)
    q = q.order_by(models.Transaction.trans_date.desc()).offset(skip).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()

# --- Summary helpers ---
async def get_account_summary_data_from_mv(db: AsyncSession, start_date: Optional[date] = None, end_date: Optional[date] = None):
    if start_date or end_date:
        sql = text("""
            SELECT
                aa.id as account_id,
                aa.display_name,
                aa.notes,
                aa.updated_at as last_account_update,
                t.country,
                COALESCE(SUM(CASE WHEN t.trans_type = 'gift_card_added' THEN t.value ELSE 0 END),0) as total_gift_cards,
                COALESCE(SUM(CASE WHEN t.trans_type = 'order_placed' THEN t.value ELSE 0 END),0) as total_orders,
                COALESCE(SUM(CASE WHEN t.trans_type = 'gift_card_added' THEN t.value ELSE -t.value END),0) as balance
            FROM amazon_account aa
            LEFT JOIN transaction t ON aa.id = t.account_id
            AND (:start IS NULL OR t.trans_date >= :start)
            AND (:end IS NULL OR t.trans_date <= :end)
            GROUP BY aa.id, aa.display_name, aa.notes, aa.updated_at, t.country
            ORDER BY aa.display_name, t.country;
        """)
        params = {"start": start_date, "end": end_date}
        res = await db.execute(sql, params)
        rows = res.mappings().all()
    else:
        res = await db.execute(text("SELECT * FROM account_balances_by_country ORDER BY display_name, country"))
        rows = res.mappings().all()

    summary_map: Dict[int, schemas.AccountSummaryRow] = {}
    countries = ["IT","DE","FR","ES","JP","US"]

    for r in rows:
        aid = r["account_id"]
        if aid not in summary_map:
            summary_map[aid] = schemas.AccountSummaryRow(
                account_id=aid,
                display_name=r["display_name"],
                notes=r["notes"],
                last_account_update=r["last_account_update"],
                total_gift_cards_all_countries=Decimal("0.00"),
                total_orders_all_countries=Decimal("0.00"),
                total_balance_all_countries=Decimal("0.00"),
            )
        sm = summary_map[aid]
        country = r["country"]
        balance = Decimal(r["balance"] or 0)
        tg = Decimal(r["total_gift_cards"] or 0)
        to = Decimal(r["total_orders"] or 0)

        if country in countries:
            setattr(sm, country, balance)
        sm.total_gift_cards_all_countries += tg
        sm.total_orders_all_countries += to
        sm.total_balance_all_countries += balance

    return list(summary_map.values())

async def get_giftcard_summary(db: AsyncSession, start_date: date, end_date: date, country: Optional[str] = None):
    q = select(
        models.Transaction.country,
        func.count(models.Transaction.id).label("count"),
        func.sum(models.Transaction.value).label("total_value")
    ).filter(
        models.Transaction.trans_type == models.TransactionType.gift_card_added,
        models.Transaction.trans_date >= start_date,
        models.Transaction.trans_date <= end_date
    )
    if country and country.upper() != "ALL":
        q = q.filter(models.Transaction.country == country.upper())
    q = q.group_by(models.Transaction.country).order_by(models.Transaction.country)
    res = await db.execute(q)
    rows = res.mappings().all()
    return [schemas.GiftCardSummaryData(country=r["country"], count=r["count"], total_value=r["total_value"]) for r in rows]

async def regenerate_materialized_view(db: AsyncSession):
    await db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY account_balances_by_country;"))
    await db.commit()
