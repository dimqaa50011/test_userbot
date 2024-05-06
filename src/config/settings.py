from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv

from .db_config import DbConfig
from .bot_config import BotConfig


BASE_DIR = Path(__file__).resolve().parent.parent.parent
BOT_SESSION_DIR = BASE_DIR / "sess"

env_path = BASE_DIR / ".env"

load_dotenv(env_path)


class AppConfig(NamedTuple):
    db: DbConfig
    bot: BotConfig
