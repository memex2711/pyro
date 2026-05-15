from pyrogram_styled.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ForceReply,
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


def ikb(rows=None):
    if rows is None:
        rows = []
    lines = []
    for row in rows:
        line = []
        for button in row:
            if isinstance(button, str):
                button = btn(button, button)
            elif len(button) == 4:          
                text, value, typ, style = button
                button = btn(text, value, typ, style)
            elif len(button) == 3:
                text, value, style = button
                button = btn(text, value, "callback_data", style)
            else:                           
                button = btn(*button)
            line.append(button)
        lines.append(line)
    return InlineKeyboardMarkup(inline_keyboard=lines)

def btn(text, value, type="callback_data", style=None):
    if not isinstance(type, str):
        raise TypeError(f"Parameter 'type' harus string, got {type(type)}")    
    if type == "callback_data" and not isinstance(value, bytes):
        value = str(value).encode()
    
    kwargs = {type: value}
    if style is not None:
        kwargs["style"] = style
    return InlineKeyboardButton(text, **kwargs)

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
            elif isinstance(button, tuple) and len(button) == 2:
                text, style = button
                button = KeyboardButton(text, style=style)
            else:
                button = KeyboardButton(str(button))
            line.append(button)
        lines.append(line)
    return ReplyKeyboardMarkup(keyboard=lines, **kwargs)

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