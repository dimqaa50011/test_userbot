from functools import wraps
import re

from pyrogram import Client, types


class CustomMessageFilter:
    def __init__(self) -> None:
        self._default_patterns = [
            r""
        ]

    def _get_pattern():
        ...

    async def message_filter(self, text: str, patterns: list, user_id: int):
        print()
        for pattern in filter.patterns:
            match = re.search(pattern, message.text)
            if match:
                ret
        return True
    # for pattern in patterns:
    #     result = re.search(pattern, message.text)
