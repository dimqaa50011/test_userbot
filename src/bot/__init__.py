from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler


from .handlers import new_message


def register_handlers(client: Client):
    client.add_handler(MessageHandler(
        new_message, filters.private))
