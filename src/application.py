import asyncio
from datetime import datetime, timedelta

from loguru import logger
from pyrogram import Client, compose
from pyrogram.errors import BadRequest, FloodWait

from src.bot import register_handlers
from src.config import app_config, BASE_DIR
from src.db_api.models.dialog import Dialog, Message
from src.db_api.crud import CrudSet
from src.db_api.models.state import UserState
from src.db_api.models.tg_user import TgUser, UserStatus
from src.controllers.user_controller import UserController
from src.db_api.models import sqlalchemy_session
from src.tools.filters.message import message_filter


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
            r"прекрасно",
            r"ожидать"
        ]
        self._polling_is_start = False
        self._canceled_tasks = {}
        self._processes = {}
        self._cancel_messages = {}

    async def start(self):
        self._loop = asyncio.get_event_loop()
        self._polling_is_start = True
        dialogs: list[Dialog] = await self._crud.dialog.get({}, many=True)
        self._delay_start = len(dialogs)
        clients = []
        callbacks = []
        try:
            for dialog in dialogs:
                client: Client = dialog.bot.get_tg_client()
                register_handlers(client)
                clients.append(client)
                callbacks.append(self._db_polling(dialog, client))

            for callback in callbacks:
                self._loop.create_task(callback)

            await compose(clients)
        finally:
            await sqlalchemy_session.close_all()
            for client in clients:
                if client.is_connected:
                    await client.stop()

    async def _db_polling(self, dialog: Dialog, client: Client):
        logger.info(f"Init polling! Dialog: {dialog.id}")
        await asyncio.sleep(self._delay_start)

        while self._polling_is_start:
            logger.info(f"Start polling! dialog: {dialog.id}")
            users: list[TgUser] = await self._crud.tg_user.get({"status": UserStatus.ALIVE.value}, many=True)
            messages = await self._crud.message.get({"dialog_id": dialog.id}, many=True)

            logger.debug(users)
            for index, message in enumerate(messages):
                logger.info(f"CANCEL TASKS {self._canceled_tasks}")

                if message.trigger and not message_filter(message.text, [message.trigger]):
                    self._cancel_messages[message.id] = True
                else:
                    if self._cancel_messages.get(message.id, False):
                        self._cancel_messages.pop(message.id)

                for user in users:
                    logger.debug(
                        f"user: {user.id} {user.user_state.next_message_id}")
                    logger.debug(f"MESS {message.id}")
                    if user.user_state.next_message_id == message.id:
                        logger.debug(
                            f"MATCHES {user.user_state.next_message_id} {message.id}")

                        try:
                            _: bool = self._pending_tasks[user.tg_id]
                            logger.debug(f"Find task {_}")
                        except KeyError:
                            self._pending_tasks[user.tg_id] = True

                            try:
                                next_message_id = messages[index + 1].id
                            except IndexError:
                                next_message_id = message.id

                            self._loop.create_task(self._background_task(
                                user, client, message.id,
                                next_message_id,
                            ))
                            logger.info(
                                f"Create new task! User_id: {user.id}")

            await asyncio.sleep(self._delay_db_polling)

    def _get_pattern(self, text: str):
        return r"(?<=\s)%s(?=\s?)" % (text)

    async def _background_task(self, user: TgUser, client: Client,  current_message_id: int, next_message_id: int):
        logger.info(f"Init BG task; user_id: {user.id}")
        is_last = True if current_message_id == next_message_id else False
        current_message = await self._crud.message.get({"id": current_message_id})
        logger.info(f"Message: {current_message}")
        key_ = f"{user.id}_{current_message.id}"
        dispatch_time = datetime.now() + timedelta(seconds=current_message.dispatch_time)
        start_send_message = False

        if not message_filter(current_message.text, self._dialog_cancel_triggers):
            self._polling_is_start = False
            return

        while not start_send_message:
            if datetime.now() >= dispatch_time:
                start_send_message = True
            elif current_message.id in self._cancel_messages:
                await self._crud.user_state.update(
                    {
                        "next_message_id": next_message_id,
                    },
                    {
                        "user": user
                    }
                )
                self._cancel_messages.pop(current_message.id)
                self._pending_tasks.pop(user.tg_id)
                return

        try:
            await client.send_message(
                chat_id=user.tg_id,
                text=current_message.text
            )
            logger.info(
                f"Send message: message_id: {current_message.id} text: {current_message.text}")
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
        except Exception as ex:
            logger.warning(ex)
        finally:
            await self._set_next_message(user, next_message_id, is_last)
            self._pending_tasks.pop(user.tg_id)

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
