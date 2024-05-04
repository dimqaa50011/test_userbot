from .db_config import DbConfig
from .settings import AppConfig

app_config = AppConfig(
    db=DbConfig()
)

__all__ = (
    "AppConfig",
    "DbConfig",
    "app_config"
)
