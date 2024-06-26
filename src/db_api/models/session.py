from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config.db_config import DbConfig


db_conf = DbConfig()

engine = create_async_engine(db_conf.get_uri(), echo=False)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class PoolDbConnection:
    SESSION = Session()

    @classmethod
    def get_connection(cls):
        return cls.SESSION

    @classmethod
    async def close_all_connection(cls):
        conn = cls.get_connection()
        await cls.SESSION.close_all()


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(DateTime())
    updated_at: Mapped[datetime] = mapped_column(DateTime())
