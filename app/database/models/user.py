from __future__ import annotations

import typing as t
from datetime import datetime

from aiogram.enums import ChatMemberStatus
from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    JSON,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from ._base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    state: Mapped[str] = mapped_column(String(64), default=ChatMemberStatus.MEMBER)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    language_code: Mapped[str] = mapped_column(String(8))

    alert_settings: Mapped[UserAlertSettingModel] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined",
    )
    subscriptions: Mapped[list[UserSubscriptionModel]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class UserSubscriptionModel(BaseModel):
    __tablename__ = "users.subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider_pubkey: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("providers.pubkey", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped[UserModel] = relationship(
        back_populates="subscriptions",
    )


class UserAlertSettingModel(BaseModel):
    __tablename__ = "users.alert_settings"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False, index=True)
    types: Mapped[t.List[str]] = mapped_column(JSON, default=list)

    user: Mapped[UserModel] = relationship(back_populates="alert_settings")


class UserTriggeredAlertModel(BaseModel):
    __tablename__ = "users.triggered_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    provider_pubkey: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("providers.pubkey", ondelete="CASCADE"),
        nullable=False,
    )
    alert_type: Mapped[str] = mapped_column(String(32), index=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "provider_pubkey",
            "alert_type",
            name="uq_user_provider_alert",
        ),
    )
