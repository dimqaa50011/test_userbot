
from pyrogram.types import Message

from src.db_api.crud import CrudSet

crud_set = CrudSet()


async def new_message(client, message: Message):
    print()
