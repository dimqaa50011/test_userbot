from pyrogram import Client

from src.config import app_config, BOT_SESSION_DIR


class ClientMixin:
    def get_tg_client(self) -> Client:
        return Client(
            name=f"bot_{self.phone}",
            phone_number=self.phone,
            api_id=app_config.bot.API_ID,
            api_hash=app_config.bot.API_HASH,
            workdir=str(BOT_SESSION_DIR)
        )
