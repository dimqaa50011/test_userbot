from datetime import datetime

from pyrogram import Client
from pyrogram.types import Message

from src.db_api.crud import CrudSet
from src.db_api.models.tg_user import UserStatus
from src.controllers.user_controller import UserController, UserScheme

crud_set = CrudSet()
user_controller = UserController()


async def new_message(client: Client, message: Message, *args, **kwargs):
    # TODO: crate filter
    print()

    new_user = await user_controller.create_user(
        UserScheme(
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            tg_id=message.from_user.id
        ),
        client.phone_number
    )

    await client.send_message(
        message.from_user.id,
        "test message"
    )
