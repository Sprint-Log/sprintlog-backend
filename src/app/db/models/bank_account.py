from __future__ import annotations
from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from advanced_alchemy.base import UUIDAuditBase
from enum import Enum

if TYPE_CHECKING:
    from .user import User


class PaymentMethod(str, Enum):
    K_PAY = "k-pay"
    AYA_PAY = "aya-pay"
    WAVE_PAY = "wave-pay"


class BankAccount(UUIDAuditBase):
    __tablename__ = "bank_account"

    method: Mapped[PaymentMethod] = mapped_column(String(length=50), nullable=False, index=True)
    account_number: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_account.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="bank_accounts")
