from datetime import datetime, timedelta, time
from enum import Enum
from tkinter import dialog

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, DateTime, String, Time, Text, Table, Column, ForeignKey

from .bot import Bot
from .tg_user import TgUser
from .session import BaseModel, Base


class EventNames(Enum):
    MESSAGE = "message"
    TRIGGER = "trigger"


event_message_table = Table(
    "envet_messages",
    Base.metadata,
    Column("event_id", ForeignKey("event.id")),
    Column("message_id", ForeignKey("message.id"))
)


user_dialog_table = Table(
    "user_dialogs",
    Base.metadata,
    Column("user_id", ForeignKey("tg_user.id")),
    Column("dialog_id", ForeignKey("dialog.id"))
)


class Event(BaseModel):
    __tablename__ = "event"

    name: Mapped[str] = mapped_column(String(10))


class Message(BaseModel):
    __tablename__ = "message"

    title: Mapped[str] = mapped_column(String(10))
    dispatch_time: Mapped[time] = mapped_column(Time)
    events: Mapped[list[Event]] = relationship(secondary=event_message_table)
    text: Mapped[str] = mapped_column(Text)
    trigger: Mapped[str] = mapped_column(
        String(10), nullable=True, default=None)
    dialog_id: Mapped[int] = mapped_column(ForeignKey("dialog.id"))


class Dialog(BaseModel):
    __tablename__ = "dialog"

    title: Mapped[str] = mapped_column(String(20))
    messages: Mapped[list[Message]] = relationship(lazy="joined")
    users: Mapped[list[TgUser]] = relationship(lazy="joined")
    bot_id: Mapped[int] = mapped_column(ForeignKey("bot.id"))
    bot: Mapped[Bot] = relationship(lazy="joined")
