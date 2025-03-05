from sqlalchemy import Column, String, ForeignKey, Boolean, DECIMAL, DateTime, Integer
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime, timezone
import uuid


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")


class Account(Base):
    __tablename__ = "accounts"

    account_number = Column(String(20), primary_key=True)
    type = Column(String(20), nullable=False)
    current_balance = Column(DECIMAL(20, 2), default=0)
    net_deposits = Column(DECIMAL(20, 2), default=0)
    currency = Column(String(10), nullable=False)
    status = Column(String(10), nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    last_synced = Column(DateTime(timezone=True), default=utc_now)

    linked_account_id = Column(
        String(20), ForeignKey("accounts.account_number"), nullable=True
    )
    account_broker_id = Column(String(20), ForeignKey("brokers.name"), nullable=True)

    linked_account = relationship("Account", remote_side=[account_number])
    account_broker = relationship("Broker")
    activities = relationship("Activity", backref="Account")


class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(String(255), primary_key=True)
    bank_account_id = Column(String(255))
    status = Column(String(255))
    currency = Column(String(30))
    amount = Column(DECIMAL(10, 2), default=0)

    cancelled_at = Column(DateTime(timezone=True))
    rejected_at = Column(DateTime(timezone=True))
    accepted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utc_now)
    last_synced = Column(DateTime(timezone=True))

    account_id = Column(String, ForeignKey("accounts.account_number"))


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String(255), primary_key=True, nullable=False)
    currency = Column(String(30), nullable=True)
    type = Column(String(30), nullable=False)
    sub_type = Column(String(30), nullable=True)
    action = Column(String(30), nullable=True)

    stop_price = Column(DECIMAL(10, 2), nullable=True, default=0)
    price = Column(DECIMAL(10, 2), nullable=False, default=0)
    quantity = Column(DECIMAL(10, 2), nullable=False, default=0)
    amount = Column(DECIMAL(10, 2), nullable=True, default=0)
    commission = Column(DECIMAL(10, 2), nullable=False, default=0)
    option_multiplier = Column(String(255), nullable=True)

    symbol = Column(String(255), nullable=True)
    market_currency = Column(String(20), nullable=True)
    status = Column(String(20), nullable=True)

    cancelled_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    filled_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    last_updated = Column(DateTime, default=utc_now, onupdate=utc_now)
    last_synced = Column(DateTime, default=utc_now)

    security_id = Column(String(255), ForeignKey("securities.id"), nullable=True)
    security = relationship("Security", back_populates="securities")

    account_id = Column(
        String(255), ForeignKey("accounts.account_number"), nullable=False
    )


class Position(Base):
    __tablename__ = "account_positions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quantity = Column(DECIMAL(20, 2), default=0)
    amount = Column(DECIMAL(20, 2), default=0)
    is_active = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    security_id = Column(String, ForeignKey("securities.id"))
    account_id = Column(String, ForeignKey("accounts.account_number"))

    security = relationship("Security")
    account = relationship("Account")


class Broker(Base):
    __tablename__ = "brokers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class Security(Base):
    __tablename__ = "securities"

    id = Column(String(255), primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False)
    name = Column(String(255))
    description = Column(String(255))
    type = Column(String(50))
    currency = Column(String(50))
    status = Column(String(50))
    exchange = Column(String(50))
    option_details = Column(String(255))
    order_subtypes = Column(String(255))

    trade_eligible = Column(Boolean, default=False)
    options_eligible = Column(Boolean, default=False)
    buyable = Column(Boolean, default=False)
    sellable = Column(Boolean, default=False)

    active_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utc_now)
    last_synced = Column(DateTime(timezone=True), default=utc_now)
    activities = relationship("Activity", backref="activities")
