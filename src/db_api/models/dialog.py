from datetime import datetime, timedelta, time
from enum import Enum
from optparse import Option
from tkinter import dialog
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, String, Time, Text, Table, Column, ForeignKey

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
    message_trigger_id: Mapped[Optional[int]
                               ] = mapped_column(ForeignKey("message.id"))
    message_trigger: Mapped[Optional["Message"]] = relationship(lazy="joined")


class Message(BaseModel):
    __tablename__ = "message"

    title: Mapped[str] = mapped_column(String(10))
    dispatch_time: Mapped[int] = mapped_column(Integer)
    events: Mapped[Optional[list[Event]]] = relationship(lazy="joined")
    text: Mapped[str] = mapped_column(Text)
    trigger: Mapped[str] = mapped_column(
        String(10), nullable=True, default=None)
    dialog_id: Mapped[int] = mapped_column(ForeignKey("dialog.id"))


class Dialog(BaseModel):
    __tablename__ = "dialog"

    title: Mapped[str] = mapped_column(String(20))
    messages: Mapped[Optional[list[Message]]] = relationship(lazy="joined")
    users: Mapped[Optional[list[TgUser]]] = relationship(
        lazy="joined", secondary=user_dialog_table, backref="dialogs")
    bot_id: Mapped[int] = mapped_column(ForeignKey("bot.id"))
    bot: Mapped[Bot] = relationship(lazy="joined")
