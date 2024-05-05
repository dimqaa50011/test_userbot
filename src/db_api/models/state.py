from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .session import BaseModel
from .dialog import Message


class UserState(BaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("tg_user.id"))
    next_message_id: Mapped[int] = mapped_column(ForeignKey("message.id"))
    next_message: Mapped[Message] = relationship()
