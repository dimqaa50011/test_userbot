from .db_config import DbConfig
from .bot_config import BotConfig
from .settings import AppConfig, BASE_DIR, BOT_SESSION_DIR

app_config = AppConfig(
    db=DbConfig(),
    bot=BotConfig()
)

__all__ = (
    "AppConfig",
    "DbConfig",
    "app_config",
    "BotConfig",
    "BASE_DIR",
    "BOT_SESSION_DIR",
)
