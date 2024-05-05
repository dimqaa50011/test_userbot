from pyrogram import Client

from src.config import app_config, BASE_DIR
from src.db_api.models.dialog import Dialog
from src.db_api.crud import CrudSet
from src.db_api.models.tg_user import TgUser, UserStatus


class Application:
    def __init__(
        self,

    ) -> None:
        self._crud = CrudSet()
        self._workdir = BASE_DIR / "sessions"

    async def start(self):
        dialogs: list[Dialog] = await self._crud.dialog.get({}, many=True)
        dialog_tasks = []

        for dialog in dialogs:

            bot = Client(
                name=dialog.bot.phone,
                api_id=app_config.bot.API_ID,
                api_hash=app_config.bot.API_HASH,
                workdir=str(self._workdir),
                phone_number=dialog.bot.phone
            )

            _users: list[TgUser] = await self._crud.tg_user.get(
                {
                    "status": UserStatus.ALIVE.value
                }
            )

            for message in dialog.messages:

                for _user in _users:
                    if _user.user_state.next_message == message:
                        dialog_tasks.append(_user)

    async def _db_polling(self, dialog: Dialog):
        while True:
            ...
