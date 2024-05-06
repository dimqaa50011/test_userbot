import asyncio
from pyrogram import Client

from src.config import app_config, BASE_DIR
from src.db_api.crud import CrudSet
from src.bot import register_handlers
from src.application import Application


class Starter:
    def __init__(self) -> None:
        self.crud = CrudSet()

    async def _init_client(self):
        bot_model = await self.crud.bot.get({}, many=False)

        self.client = Client(
            name=bot_model.phone,
            api_id=app_config.bot.API_ID,
            api_hash=app_config.bot.API_HASH,
            workdir=str(BASE_DIR / "sessions"),
            phone_number=bot_model.phone
        )

    def start(self):
        loop = asyncio.get_event_loop()
        wait_tasks = asyncio.wait(
            [loop.create_task(self._init_client())]
        )
        loop.run_until_complete(wait_tasks)
        register_handlers(self.client)
        self.client.run()

    async def tester(self):
        user = await self.crud.tg_user.get(
            {
                "id": 2
            }
        )
        print()


if __name__ == "__main__":
    app = Application()
    # starter = Starter()
    # starter.start()
    asyncio.run(app.start())
