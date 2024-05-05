from email import message
from typing import Any, Type

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete

from .models.session import BaseModel
from .models.tg_user import TgUser
from .models.dialog import Dialog, Message, Event
from .models import sqlalchemy_session


class BaseCrud:
    model: Type[BaseModel]

    def __init__(self, session: AsyncSession) -> None:
        self._sesseion = session

    async def create(self, data: dict[str, Any]) -> BaseModel:
        new_item = self.model(**data)
        try:
            self._sesseion.add(new_item)
            await self._sesseion.commit()
        except IntegrityError as ex:
            logger.info(ex)

        return new_item

    async def get(self, filter: dict[str, Any], many: bool = False) -> BaseModel | list[BaseModel]:
        stmt = select(self.model).where(**self._get_params(filter))
        func_name = "scalar"
        if many:
            func_name = "sclars"

        func = getattr(self._sesseion, func_name)
        return await func(stmt)

    async def update(self, update_data: dict[str, Any], filter: dict[str, Any]):
        stmt = update(self.model).where(
            **self._get_params(filter)).values(**update_data)
        await self._sesseion.execute(stmt)
        await self._sesseion.commit()

    async def delete(self, filter: dict[str, Any]):
        stmt = delete(self.model).where(**self._get_params(filter))
        await self._sesseion.execute(stmt)
        await self._sesseion.commit()

    def _get_params(self, filter: dict[str, Any]):
        result = {}
        for k, v in filter.items():
            if hasattr(self.model, k):
                result[getattr(self.model, k)] = v
        return result


class TgUserCrud(BaseCrud):
    model = TgUser


class DialogCrud(BaseCrud):
    model = Dialog


class EventCrud(BaseCrud):
    model = Event


class MessageCrud(BaseCrud):
    model = Message


class CrudSet:
    tg_user = TgUserCrud(sqlalchemy_session)
    event = EventCrud(sqlalchemy_session)
    message = MessageCrud(sqlalchemy_session)
    dialog = DialogCrud(sqlalchemy_session)
