from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .session import BaseModel
from .dialog import Message
from .tg_user import TgUser


class UserState(BaseModel):
    __tablename__ = "user_state"

    user_id: Mapped[int] = mapped_column(ForeignKey("tg_user.id"))
    user: Mapped[TgUser] = relationship(
        lazy="joined", back_populates="user_state")
    next_message_id: Mapped[int] = mapped_column(ForeignKey("message.id"))
    next_message: Mapped[Message] = relationship(
        lazy="joined", back_populates="user_states")
