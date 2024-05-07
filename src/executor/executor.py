from datetime import datetime, timedelta
from typing import Any, Sequence
import asyncio

from loguru import logger
from pyrogram.errors import BadRequest, FloodWait
from pyrogram import Client

from src.db_api.crud import CrudSet
from src.db_api.models.dialog import Dialog, Message
from src.db_api.models.state import UserState
from src.db_api.models.tg_user import UserStatus
from src.tools.filters.message import message_filter


class Executor:
    def __init__(self, dialog: Dialog, loop: asyncio.AbstractEventLoop, client: Client, delay_start: float = 10) -> None:
        self._dialog = dialog
        self._loop = loop
        self._client = client
        self._crud = CrudSet()
        self._dialog_cancel_triggers = [
            r"прекрасно",
            r"ожидать"
        ]
        self._start_polling_flag = False
        self._cancel_message = {}
        self.__delay_start = delay_start
        self._pending = {}
        self._delay_polling = 1
        self._dispatch_info = {}

    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        self._start_polling_flag = True
        self._loop
        await asyncio.sleep(self.__delay_start)
        await self._start_polling()

    async def _start_polling(self):
        messages: Sequence[Message] = await self._crud.message.get({"dialog_id": self._dialog.id}, many=True)

        while self._start_polling_flag:

            for index, message in enumerate(messages):
                user_states: Sequence[UserState] = await self._crud.user_state.get({"next_message_id": message.id}, many=True)

                await self.__check_message(message)

                for state_ in user_states:
                    key_ = f"{state_.id}_{message.id}"
                    if state_.next_message_id == message.id and state_.user.status == UserStatus.ALIVE.value:
                        try:
                            _ = self._cancel_message[message.id]
                            next_index = index + 2
                        except KeyError:
                            next_index = index + 1

                        try:
                            next_message_id = messages[next_index].id
                        except IndexError:
                            next_message_id = messages[-1].id

                        task_ = self._pending.get(key_)

                        if not task_:
                            self._pending[key_] = True
                            self._loop.create_task(
                                self.__send_message(
                                    state=state_,
                                    current_message_id=message.id,
                                    next_message_id=next_message_id,
                                    key_=key_
                                )
                            )
            await asyncio.sleep(self._delay_polling)

    async def __check_message(self, message: Message, cancel_dialog: bool = False):
        if cancel_dialog:
            if not message_filter(message.text, self._dialog_cancel_triggers):
                self._start_polling_flag = False
        else:
            if message.trigger and not message_filter(message.text, [message.trigger]):
                try:
                    _ = self._cancel_message[message.id]
                except KeyError:
                    self._cancel_message[message.id] = True

    async def __send_message(self, state: UserState, current_message_id: int, next_message_id: int, key_: str):
        logger.info(
            f"Init __send_message! user_id: {state.user.id} message_id {current_message_id}")
        current_message: Message = await self._crud.message.get({"id": current_message_id})
        _start_send_message = False
        _is_last = current_message_id == next_message_id

        if self._cancel_message.get(current_message.id):
            self._dispatch_info[state.user.id] = datetime.now()
            self._pending.pop(key_)
            await self._crud.user_state.update(
                {"next_message_id": next_message_id},
                {"next_message_id": current_message.id}
            )
            return

        while not _start_send_message:
            last_dispath = self._dispatch_info.get(state.user.id, None)
            if last_dispath is None:
                last_dispath = datetime.now()
                self._dispatch_info[state.user.id] = last_dispath

            if last_dispath + timedelta(seconds=current_message.dispatch_time) <= datetime.now():
                _start_send_message = True
            elif await self.__check_message(current_message, True):
                self._start_polling_flag = False

            await asyncio.sleep(1)

        if _start_send_message:

            try:
                await self._client.send_message(
                    chat_id=state.user.tg_id,
                    text=current_message.text
                )
                self._dispatch_info[state.user.id] = datetime.now()
                logger.info(
                    f"Send message: message_id: {current_message.id} text: {current_message.text}")
                self._pending.pop(key_)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except BadRequest as e:
                logger.warning(e)
            finally:
                await self._crud.user_state.update(
                    {"next_message_id": next_message_id},
                    {"next_message_id": current_message.id}
                )

                if _is_last:
                    await self._crud.tg_user.update(
                        {"status": UserStatus.FINISHED.value},
                        {"id": state.user.id}
                    )
