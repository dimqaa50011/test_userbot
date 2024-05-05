import asyncio
from datetime import datetime

from pyrogram import Client

from src.config import app_config, BASE_DIR
from src.db_api.crud import BotCrud
from src.db_api.models.session import Session


def add_bot():

    async def _save(phone: str, session_path: str, client: Client):
        await client.start()
        sqlalchemy_session = Session()
        _crud = BotCrud(sqlalchemy_session)
        await client.get_me()
        res = await _crud.create(
            {
                "phone": phone,
                "session_path": session_path,
                "created": datetime.now(),
                "updated_at": datetime.now()
            }
        )

        await sqlalchemy_session.close()
        # await client.stop()
        return res

    workdir = BASE_DIR / "sessions"
    phone = input("Enter phone: ").strip()
    new_client = Client(
        name=phone,
        phone_number=phone,
        api_id=app_config.bot.API_ID,
        api_hash=app_config.bot.API_HASH,
        workdir=str(str(workdir))
    )

    asyncio.run(_save(phone, str(workdir / f"{phone}.session"), new_client))


if __name__ == "__main__":
    add_bot()
