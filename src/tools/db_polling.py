from typing import Optional
from src.db_api.models.dialog import Dialog
from src.db_api.crud import CrudSet


class DialogNode:
    def __init__(
        self,
        next_node: Optional["DialogNode"] = None,
        previous_node: Optional["DialogNode"] = None,
    ) -> None:
        self.next_node = next_node
        self.previous_node = previous_node
        self.state = {
            "users": []
        }


class PollingWorker:
    crud_set = CrudSet()

    async def start_polling(self, dialog: Dialog):
        while True:
            messages = dialog.messages

            for message in messages:
                ...
