from datetime import datetime
from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, DateTime, ForeignKey, String

from .session import BaseModel


class UserStatus(Enum):
    ALIVE = "alive"
    DEAD = "dead"
    FINISHED = "finished"


class TgUser(BaseModel):
    __tablename__ = "tg_user"

    tg_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(
        String(10), default=UserStatus.ALIVE.value)
    status_updated_at: Mapped[datetime] = mapped_column(DateTime)
    first_name: Mapped[str] = mapped_column(
        String(64), nullable=True, default=None)
    last_name: Mapped[str] = mapped_column(
        String(64), nullable=True, default=None)
    username: Mapped[str] = mapped_column(
        String(64), nullable=True, default=None, unique=True)
    user_state: Mapped["UserState"] = relationship(
        back_populates="user", lazy="joined")
