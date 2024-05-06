import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from loguru import logger
from pyrogram import Client, compose
from pyrogram.errors import BadRequest, FloodWait

from src.bot import register_handlers
from src.config import app_config, BASE_DIR
from src.db_api.models.dialog import Dialog
from src.db_api.crud import CrudSet
from src.db_api.models.tg_user import TgUser, UserStatus
from src.controllers.user_controller import UserController
from src.db_api.models import sqlalchemy_session
from src.tools.filters.message import message_filter


@dataclass(init=True)
class PendingTask:
    ...


class Application:
    def __init__(
        self,

    ) -> None:
        self._crud = CrudSet()
        self._workdir = BASE_DIR / "sess"
        self._user_controller = UserController()
        self._pending_tasks = {}
        self._delay_db_polling = 1
        self._dialog_cancel_triggers = [
            r"(?<=\s)[Пп]рекрасно(?=\s)",
            r"(?<=\s)[Оо]жидать(?=\s)"
        ]
        self._polling_is_start = False

    async def start(self):
        self._loop = asyncio.get_event_loop()
        self._polling_is_start = True
        dialogs: list[Dialog] = await self._crud.dialog.get({}, many=True)
        clients = []
        try:
            for dialog in dialogs:
                client = dialog.bot.get_tg_client()
                register_handlers(client)
                clients.append(client)
                self._loop.create_task(self._db_polling(dialog, client))
                # await client.start()
                # asyncio.gather(*[c.start() for c in clients])
            await compose(clients)
        finally:
            await sqlalchemy_session.close_all()

    def _get_pattern(self, text: str):
        return r"(?<=\s)%s(?=\s)" % (text)

    async def _background_task(self, user: TgUser, client: Client, sleep: int, text: str, next_message_id: int, is_last: bool, trigger: Optional[str] = None):
        logger.info(f"Init BG task; user_id: {user.id}")
        logger.info(f"Before exited: {self._pending_tasks}")
        if trigger and message_filter(text, [self._get_pattern(trigger)]):
            await self._set_next_message(user, next_message_id, is_last)
            return

        await asyncio.sleep(float(sleep))
        try:
            # text = user.user_state.next_message.text
            await client.send_message(
                chat_id=user.tg_id,
                text=text
            )
            logger.info(f"Send message: {text}")
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except BadRequest as e:
            logger.warning(e)
            await self._crud.user_state.update(
                {
                    "status": UserStatus.DEAD,
                    "status_updated_at": datetime.now()
                },
                {
                    "user": user
                }
            )
        finally:
            await self._set_next_message(user, next_message_id, is_last)

    async def _set_next_message(self, user: TgUser, next_message_id: int, is_last: bool):
        if is_last:
            await self._crud.tg_user.update(
                {
                    "status": UserStatus.FINISHED.value
                },
                {
                    "id": user.id
                }
            )

            await self._crud.user_state.update(
                {
                    "next_message_id": next_message_id,
                },
                {
                    "user": user
                }
            )
            self._pending_tasks.pop(user.tg_id)

    async def _db_polling(self, dialog: Dialog, client: Client):
        logger.info(f"Init polling! Dialog: {dialog.id}")

        while self._polling_is_start:
            logger.info(f"Start polling! dialog: {dialog.id}")
            users: list[TgUser] = await self._crud.tg_user.get(
                {
                    "status": UserStatus.ALIVE.value
                },
                many=True
            )
            messages = await self._crud.message.get({"dialog_id": dialog.id}, many=True)
            # u.user for _u in message.user_states if _u.user.status == UserStatus.ALIVE.value
            for index, message in enumerate(messages):
                logger.info(f"Message: {message.id}")

                if message_filter(message.text, self._dialog_cancel_triggers):
                    self._polling_is_start = False
                    break

                for user in users:
                    if user.user_state.next_message_id == message.id:
                        logger.info(f"User: {user.id}")
                        logger.info(f"_pending_tasks: {self._pending_tasks}")
                        try:
                            _: bool = self._pending_tasks[user.tg_id]
                        except KeyError:
                            self._pending_tasks[user.tg_id] = True

                            try:
                                next_message_id = messages[index + 1].id
                                is_last = False
                            except IndexError:
                                next_message_id = message.id
                                is_last = True
                            self._loop.create_task(self._background_task(
                                user, client, message.dispatch_time, message.text,
                                next_message_id=next_message_id, is_last=is_last
                            ))
                            logger.info(f"Create new task! User_id: {user.id}")

            await asyncio.sleep(self._delay_db_polling)
