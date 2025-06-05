from pydantic import BaseModel, constr, condecimal
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
import uuid
from app.models import TransactionType

class AmazonAccountBase(BaseModel):
    display_name: str
    notes: Optional[str] = None

class AmazonAccountCreate(AmazonAccountBase):
    pass

class AmazonAccountSchema(AmazonAccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    trans_date: date
    trans_type: TransactionType
    code: Optional[str] = None
    country: constr(min_length=2, max_length=2)
    value: condecimal(max_digits=10, decimal_places=2)

class TransactionCreate(TransactionBase):
    account_id: int
    user_id: Optional[uuid.UUID] = None

class TransactionSchema(TransactionBase):
    id: int
    account_id: int
    user_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AccountBalanceByCountry(BaseModel):
    account_id: int
    display_name: str
    notes: Optional[str] = None
    last_account_update: Optional[datetime] = None
    country: Optional[str] = None
    total_gift_cards: condecimal(max_digits=10, decimal_places=2)
    total_orders: condecimal(max_digits=10, decimal_places=2)
    balance: condecimal(max_digits=10, decimal_places=2)

    class Config:
        from_attributes = True

class AccountSummaryRow(BaseModel):
    account_id: int
    display_name: str
    notes: Optional[str] = None
    last_account_update: Optional[datetime] = None
    IT: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    DE: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    FR: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    ES: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    JP: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    US: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    total_gift_cards_all_countries: condecimal(max_digits=10, decimal_places=2)
    total_orders_all_countries: condecimal(max_digits=10, decimal_places=2)
    total_balance_all_countries: condecimal(max_digits=10, decimal_places=2)

class GiftCardSummaryData(BaseModel):
    country: str
    count: int
    total_value: condecimal(max_digits=10, decimal_places=2)
    pending_value: condecimal(max_digits=10, decimal_places=2) = Decimal("0.00")
