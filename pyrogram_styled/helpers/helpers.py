import re
from pyrogram_styled.enums import ButtonStyle
from pyrogram_styled.types import (
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# The inverse of above
def bki(keyboard):
    """
    Create a list of lists of buttons from an InlineKeyboardMarkup.

    :param keyboard: InlineKeyboardMarkup
    :return: List of lists of buttons
    """
    lines = []
    for row in keyboard.inline_keyboard:
        line = []
        for button in row:
            button = ntb(button)  # btn() format
            line.append(button)
        lines.append(line)
    return lines
    # return ikb() format


def ntb(button):
    """
    Create a button list from an InlineKeyboardButton.

    :param button: InlineKeyboardButton
    :return: Button as a list to be used in btn()
    """
    for btn_type in [
        "callback_data",
        "url",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "callback_game",
    ]:
        value = getattr(button, btn_type)
        if value:
            break
    button = [button.text, value]
    if btn_type != "callback_data":
        button.append(btn_type)
    return button
    # return {'text': text, type: value}

def clean_emoji(text):
    if not text:
        return "Uncategorized"
    text = re.sub(r"<emoji id=\d+>(.*?)</emoji>", r"\1", text)
    return text.strip()


def ikb(rows=None):
    if rows is None:
        rows = []
    lines = []
    for row in rows:
        line = []
        for button in row:
            if isinstance(button, str):
                button = btn(button, button)
            elif len(button) == 5:
                text, value, typ, style, icon = button
                button = btn(text, value, typ, style, icon)
            elif len(button) == 4:
                if isinstance(button[2], ButtonStyle):
                    text, value, style, icon = button
                    button = btn(text, value, style=style, icon=icon)
                else:
                    text, value, typ, icon_or_style = button
                    if isinstance(icon_or_style, ButtonStyle):
                        button = btn(text, value, typ=typ, style=icon_or_style)
                    else:
                        button = btn(text, value, typ=typ, icon=icon_or_style)
            elif len(button) == 3:
                if isinstance(button[2], ButtonStyle):
                    text, value, style = button
                    button = btn(text, value, style=style)
                else:
                    text, value, icon = button
                    button = btn(text, value, icon=icon)
            else:
                button = btn(*button)
            line.append(button)
        lines.append(line)
    return InlineKeyboardMarkup(inline_keyboard=lines)


def kb(rows=None, **kwargs):
    if rows is None:
        rows = []
    lines = []
    for row in rows:
        line = []
        for button in row:
            if isinstance(button, str):
                button = KeyboardButton(button)
            elif isinstance(button, dict):
                button = KeyboardButton(**button)
            elif isinstance(button, tuple):
                if len(button) == 3:
                    text, style, icon = button
                    button = KeyboardButton(text, style=style, icon_custom_emoji_id=icon)
                elif len(button) == 2:
                    text, second = button
                    if isinstance(second, ButtonStyle):
                        button = KeyboardButton(text, style=second)
                    else:
                        button = KeyboardButton(text, icon_custom_emoji_id=second)
                else:
                    button = KeyboardButton(str(button[0]))
            else:
                button = KeyboardButton(str(button))
            line.append(button)
        lines.append(line)
    return ReplyKeyboardMarkup(keyboard=lines, **kwargs)


def btn(text, value, typ="callback_data", style=None, icon=None):
    if not isinstance(typ, str):
        raise TypeError(f"Parameter 'type' harus string, got {type(typ)}")
    if typ == "callback_data" and not isinstance(value, bytes):
        value = str(value).encode()
    if typ == "copy_text" and isinstance(value, (str, int)):
        value = CopyTextButton(text=str(value))
    kwargs = {typ: value}
    if style is not None:
        kwargs["style"] = style
    if icon is not None:
        kwargs["icon_custom_emoji_id"] = icon
    return InlineKeyboardButton(text, **kwargs)


kbtn = KeyboardButton
"""
Create a KeyboardButton.
"""


def force_reply(selective=True):
    """
    Create a ForceReply.

    :param selective: Whether the reply should be selective. Defaults to True.
    :return: ForceReply
    """
    return ForceReply(selective=selective)


def array_chunk(input_array, size):
    """
    Split an array into chunks.

    :param input_array: The array to split.
    :param size: The size of each chunk.
    :return: List of chunks.
    """
    return [input_array[i: i + size] for i in range(0, len(input_array), size)]