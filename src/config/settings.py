from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv

from src.config.db_config import DbConfig
from src.db_api.models import Base


BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_path = BASE_DIR / ".env"

load_dotenv(env_path)


class AppConfig(NamedTuple):
    db: DbConfig
    base = Base
