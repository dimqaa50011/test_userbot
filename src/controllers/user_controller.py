from dataclasses import dataclass
from datetime import datetime

from src.db_api.crud import CrudSet
from src.db_api.models.dialog import Dialog
from src.db_api.models.tg_user import UserStatus


@dataclass(init=True, frozen=True)
class UserScheme:
    first_name: str | None
    last_name: str | None
    username: str | None
    tg_id: int

    status: str = UserStatus.ALIVE.value
    created: datetime = datetime.now()
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    status_updated_at: datetime = datetime.now()

    def to_dict(self):
        data = {}
        for k in self.__annotations__.keys():
            data[k] = getattr(self, k)
        return data


class UserController:
    def __init__(self) -> None:
        self.crud = CrudSet()

    async def create_user(self, user_item: UserScheme, phone: str):
        dialog: Dialog = await self.crud.dialog.get(
            {
                "bot": await self.crud.bot.get(
                    {
                        "phone": phone
                    }
                )
            }
        )
        _user = await self.crud.tg_user.get({"tg_id": user_item.tg_id})
        if not _user:
            first_message = await self.crud.message.get({"dialog_id": dialog.id})
            new_user = await self.crud.tg_user.create(
                user_item.to_dict()
            )
            user_state = await self.crud.user_state.create(
                {
                    "user_id": new_user.id,
                    "user": new_user,
                    "next_message_id": first_message.id,
                    "next_message": first_message,
                    "created": datetime.now(),
                    "updated_at": datetime.now()
                }
            )
        print()
