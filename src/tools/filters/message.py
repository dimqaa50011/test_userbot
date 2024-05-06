import re


async def message_filter(text: str, patterns: list):
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return False
    return True
