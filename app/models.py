from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Numeric,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    DateTime,
    func,
    CheckConstraint,
    Uuid,
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class TransactionType(enum.Enum):
    gift_card_added = "gift_card_added"
    order_placed = "order_placed"

class AmazonAccount(Base):
    __tablename__ = "amazon_account"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    display_name = Column(String, nullable=False, unique=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    account_id = Column(
        Integer, ForeignKey("amazon_account.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Uuid, ForeignKey("auth.users.id"))
    trans_date = Column(Date, nullable=False)
    trans_type = Column(SQLAlchemyEnum(TransactionType), nullable=False)
    code = Column(String)
    country = Column(String(2), nullable=False)
    value = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (CheckConstraint("value >= 0", name="check_value_positive"),)

    account = relationship("AmazonAccount", back_populates="transactions")
