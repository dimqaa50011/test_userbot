from email import message
from typing import Any, Optional, Sequence, Type

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from src.db_api.models.bot import Bot
from src.db_api.models.state import UserState

from .models.session import BaseModel
from .models.tg_user import TgUser
from .models.dialog import Dialog, Message, Event
from .models import sqlalchemy_session


class BaseCrud:
    model: Type[BaseModel]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: dict[str, Any]) -> BaseModel:
        new_item = self.model(**data)
        try:
            self._session.add(new_item)
            await self._session.commit()
        except IntegrityError as ex:
            logger.info(ex)
            await self._session.rollback()

        return new_item

    async def get(self, filter: Optional[dict[str, Any]] = None, many: bool = False) -> BaseModel | None | Sequence[BaseModel]:
        stmt = select(self.model)
        if filter:
            stmt = stmt.where(and_(*self._get_params(filter)))

        stmt = stmt.order_by("created")
        result = await self._session.scalars(stmt)
        if many:
            return result.unique().all()
        return result.first()

    async def update(self, update_data: dict[str, Any], filter: dict[str, Any]):
        stmt = update(self.model).where(
            *self._get_params(filter)).values(update_data)
        try:
            await self._session.execute(stmt)
            await self._session.commit()
        except Exception as ex:
            logger.warning(ex)
            await self._session.rollback()

    async def delete(self, filter: dict[str, Any]):
        stmt = delete(self.model).where(and_(*self._get_params(filter)))
        await self._session.execute(stmt)
        await self._session.commit()

    def _get_params(self, filter: dict[str, Any]):
        params = []
        for k, v in filter.items():
            params.append(
                (getattr(self.model, k) == v)
            )
        return params


class TgUserCrud(BaseCrud):
    model = TgUser


class DialogCrud(BaseCrud):
    model = Dialog


class EventCrud(BaseCrud):
    model = Event


class MessageCrud(BaseCrud):
    model = Message


class BotCrud(BaseCrud):
    model = Bot


class UserStateCrud(BaseCrud):
    model = UserState


class CrudSet:
    tg_user = TgUserCrud(sqlalchemy_session)
    event = EventCrud(sqlalchemy_session)
    message = MessageCrud(sqlalchemy_session)
    dialog = DialogCrud(sqlalchemy_session)
    bot = BotCrud(sqlalchemy_session)
    user_state = UserStateCrud(sqlalchemy_session)
