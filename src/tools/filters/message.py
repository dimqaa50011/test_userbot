import re


def message_filter(text: str, patterns: list):
    flag = True
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            flag = False
            break
    return flag
