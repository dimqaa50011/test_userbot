from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.tools.mixins.db.bot import ClientMixin


from .session import BaseModel


class Bot(ClientMixin, BaseModel):
    __tablename__ = "bot"

    phone: Mapped[str] = mapped_column(String(12))
    session_path: Mapped[str] = mapped_column(String(128))
