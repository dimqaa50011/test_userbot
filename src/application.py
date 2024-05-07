import asyncio

from loguru import logger
from pyrogram import Client, compose

from src.executor.executor import Executor
from src.bot import register_handlers
from src.db_api.models.dialog import Dialog
from src.db_api.crud import CrudSet

from src.db_api.models import PoolDbConnection


class Application:
    def __init__(
        self,
    ) -> None:
        self._crud = CrudSet()

    async def start(self):
        self._loop = asyncio.get_event_loop()
        self._polling_is_start = True
        dialogs: list[Dialog] = await self._crud.dialog.get({}, many=True)
        clients = []
        callbacks = []
        try:
            for dialog in dialogs:
                client: Client = dialog.bot.get_tg_client()
                register_handlers(client)
                exec_item = Executor(
                    dialog, self._loop, client
                )
                clients.append(client)
                callbacks.append(exec_item())
            logger.info("Init clients and tasks")

            for callback in callbacks:
                self._loop.create_task(callback)

            await compose(clients)
        finally:
            await PoolDbConnection.close_all_connection()
            for client in clients:
                if client.is_connected:
                    await client.stop()
