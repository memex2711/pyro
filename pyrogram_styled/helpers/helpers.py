import re
from typing import Any, Dict, List, Optional, Tuple, Union

from pyrogram_styled.enums import ButtonStyle
from pyrogram_styled.types import (
    CopyTextButton,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from pyrogram_styled import raw

# ── Type Definitions ──────────────────────────────────────────────────────────

ButtonTuple = Tuple[Any, ...]
ButtonInput = Union[
    str, Dict[str, Any], InlineKeyboardButton, KeyboardButton, ButtonTuple
]

# ── Constants & Mappings ──────────────────────────────────────────────────────

_STYLE_MAP: Dict[str, ButtonStyle] = {
    # Default
    "default": ButtonStyle.DEFAULT,
    "d": ButtonStyle.DEFAULT,
    # Primary / Blue
    "primary": ButtonStyle.PRIMARY,
    "p": ButtonStyle.PRIMARY,
    "blue": ButtonStyle.PRIMARY,
    "b": ButtonStyle.PRIMARY,
    # Success / Green
    "success": ButtonStyle.SUCCESS,
    "s": ButtonStyle.SUCCESS,
    "green": ButtonStyle.SUCCESS,
    "g": ButtonStyle.SUCCESS,
    # Danger / Red
    "danger": ButtonStyle.DANGER,
    "red": ButtonStyle.DANGER,
    "r": ButtonStyle.DANGER,
}

_KNOWN_TYPES: frozenset = frozenset({
    "callback_data",
    "url",
    "copy_text",
    "switch_inline_query",
    "switch_inline_query_current_chat",
    "web_app",
    "callback_game",
})

# ── Helper Parsing Functions ──────────────────────────────────────────────────


def parse_style(style: Union[str, ButtonStyle, None]) -> Optional[ButtonStyle]:
    """
    Converts a string alias or ButtonStyle to a ButtonStyle object.

    :param style: String alias or ButtonStyle instance.
    :return: ButtonStyle or None if input is None.
    """
    if style is None:
        return None
    if isinstance(style, ButtonStyle):
        return style

    key = str(style).lower().strip()
    result = _STYLE_MAP.get(key)
    if result is None:
        valid = ", ".join(sorted(set(_STYLE_MAP.keys())))
        raise ValueError(f"Style '{style}' tidak dikenal. Pilihan valid: {valid}")
    return result


def _is_style_value(val: Any) -> bool:
    """Checks if the value is a valid ButtonStyle or style alias."""
    if isinstance(val, ButtonStyle):
        return True
    if isinstance(val, str):
        return val.lower().strip() in _STYLE_MAP
    return False


def _is_known_type(val: Any) -> bool:
    """Checks whether the value is a recognized button type name."""
    if isinstance(val, str):
        return val.lower().strip() in _KNOWN_TYPES
    return False


def _is_custom_emoji_id(val: Any) -> bool:
    """
    Checks whether the value is a Telegram custom emoji ID.
    Telegram emoji IDs are always numeric integers or long strings of digits.
    """
    if isinstance(val, int) and val > 0:
        return True
    if isinstance(val, str) and val.isdigit() and len(val) >= 5:
        return True
    return False


def _normalize_rows(rows: List[Any]) -> List[List[Any]]:
    """
    Detect and convert a 1-dimensional (flat) list into a 2-dimensional list.
    """
    if not rows:
        return []

    first_item = rows[0]
    is_1d = False

    if isinstance(first_item, (str, dict, InlineKeyboardButton, KeyboardButton)):
        is_1d = True
    elif isinstance(first_item, (tuple, list)):
        if len(first_item) > 0 and isinstance(first_item[0], (str, int)):
            is_1d = True

    return [rows] if is_1d else rows


def _parse_inline_tuple(tpl: Tuple[Any, ...]) -> InlineKeyboardButton:
    """
    Improved flexibility for reading Tuples for InlineKeyboardButton.
    The positions of parameters following index 1 (value)—specifically style, type, and icon—can now be arbitrary.
    """
    if not tpl:
        raise ValueError("Tuple tombol tidak boleh kosong.")

    text = str(tpl[0])
    value = tpl[1] if len(tpl) > 1 else text

    remaining = tpl[2:]

    typ: Optional[str] = None
    style: Optional[Union[str, ButtonStyle]] = None
    icon: Optional[Union[str, int]] = None

    for arg in remaining:
        if arg is None:
            continue

        if style is None and _is_style_value(arg):
            style = arg
            continue

        if typ is None and _is_known_type(arg):
            typ = str(arg).lower().strip()
            continue

        if icon is None and _is_custom_emoji_id(arg):
            icon = arg
            continue

        if style is None and isinstance(arg, str):
            try:
                style = parse_style(arg)
                continue
            except ValueError:
                pass

        if icon is None and isinstance(arg, (str, int)):
            icon = arg

    return btn(text=text, value=value, typ=typ, style=style, icon=icon)


def _parse_reply_tuple(tpl: Tuple[Any, ...]) -> KeyboardButton:
    """
    Improved flexibility in reading Tuples for KeyboardButton (Reply Keyboard).
    Parameters after index 0 (text) can be randomized (style, icon).
    """
    if not tpl:
        raise ValueError("Tuple tombol tidak boleh kosong.")

    text = str(tpl[0])
    remaining = tpl[1:]

    style: Optional[Union[str, ButtonStyle]] = None
    icon: Optional[Union[str, int]] = None

    for arg in remaining:
        if arg is None:
            continue

        if style is None and _is_style_value(arg):
            style = arg
            continue

        if icon is None and _is_custom_emoji_id(arg):
            icon = arg
            continue

        if style is None and isinstance(arg, str):
            try:
                style = parse_style(arg)
                continue
            except ValueError:
                pass

        if icon is None and isinstance(arg, (str, int)):
            icon = arg

    kwargs: Dict[str, Any] = {}
    parsed_style = parse_style(style) if style else None

    if parsed_style is not None:
        kwargs["style"] = parsed_style
    if icon is not None:
        kwargs["icon_custom_emoji_id"] = str(icon)

    return KeyboardButton(text=text, **kwargs)


# ── Public Builders ───────────────────────────────────────────────────────────


def btn(
    text: str,
    value: Any = None,
    typ: Optional[str] = None,
    style: Union[str, ButtonStyle, None] = None,
    icon: Union[str, int, None] = None,
) -> InlineKeyboardButton:
    """
    Creates a single InlineKeyboardButton object with automatic type detection.

    :param text: Button label.
    :param value: Button payload (callback data, URL, copy text, etc.).
    :param typ: Action type ("callback_data", "url", "copy_text", etc.). Automatically detected if None.
    :param style: Button color/style ("red", "green", "blue", "default", or ButtonStyle).
    :param icon: Custom Emoji ID for the button icon.
    """
    if value is None:
        value = text

    resolved_style = parse_style(style) if style else None

    if typ is None:
        if isinstance(value, str) and value.lower().startswith(
            ("http://", "https://", "t.me/", "tg://")
        ):
            typ = "url"
        else:
            typ = "callback_data"

    if typ == "callback_data" and not isinstance(value, (bytes, str)):
        value = str(value)

    if typ == "copy_text" and isinstance(value, (str, int)):
        value = CopyTextButton(text=str(value))

    kwargs: Dict[str, Any] = {typ: value}

    if resolved_style is not None:
        kwargs["style"] = resolved_style
    if icon is not None:
        kwargs["icon_custom_emoji_id"] = str(icon)

    return InlineKeyboardButton(text=str(text), **kwargs)


def ikb(rows: Optional[List[Any]] = None) -> InlineKeyboardMarkup:
    """
    Dynamically create an InlineKeyboardMarkup using tuples with reorderable parameters.

    Supported tuple formats (parameter order after `value` is flexible):
        - (text,)
        - (text, value)
        - (text, value, style)
        - (text, value, type)
        - (text, value, icon)
        - (text, value, style, type, icon) -> POSITIONS CAN BE SHUFFLED!

    Example:
        >>> ikb([
        >>>     [("Google", "https://google.com")], # Auto-detects type="url"
        >>>     [("Delete", "del_1", "red"), ("Copy", "12345", "5249053508", "copy_text", "green")], # Mixed order
        >>> ])
    """
    if rows is None:
        rows = []

    rows = _normalize_rows(rows)
    lines: List[List[InlineKeyboardButton]] = []

    for row in rows:
        line: List[InlineKeyboardButton] = []
        for button in row:
            if isinstance(button, InlineKeyboardButton):
                line.append(button)
            elif isinstance(button, str):
                line.append(btn(button, button))
            elif isinstance(button, dict):
                line.append(btn(**button))
            elif isinstance(button, (tuple, list)):
                line.append(_parse_inline_tuple(tuple(button)))
            else:
                line.append(btn(str(button), str(button)))
        lines.append(line)

    return InlineKeyboardMarkup(inline_keyboard=lines)


def kb(rows: Optional[List[Any]] = None, **kwargs) -> ReplyKeyboardMarkup:
    """
    Dynamically generate ReplyKeyboardMarkup.

    Supported tuple formats:
    - text
    - (text, style)
    - (text, icon)
    - (text, style, icon) -> The order of styles and icons can be randomized.
    """
    if rows is None:
        rows = []

    rows = _normalize_rows(rows)
    lines: List[List[KeyboardButton]] = []

    for row in rows:
        line: List[KeyboardButton] = []
        for button in row:
            if isinstance(button, KeyboardButton):
                line.append(button)
            elif isinstance(button, str):
                line.append(KeyboardButton(button))
            elif isinstance(button, dict):
                line.append(KeyboardButton(**button))
            elif isinstance(button, (tuple, list)):
                line.append(_parse_reply_tuple(tuple(button)))
            else:
                line.append(KeyboardButton(str(button)))
        lines.append(line)

    return ReplyKeyboardMarkup(keyboard=lines, **kwargs)


# ── Utility Helpers ───────────────────────────────────────────────────────────

def richbutton(
    text: str,
    callback_data: str | bytes | None = None,
    url: str | None = None,
    copy_text: str | None = None,
    *,
    bg_primary: bool = False,
    bg_danger: bool = False,
    bg_success: bool = False,
    link: bool = False,
) -> raw.base.PageButton:
    """Create a Telegram Rich Message button for layer 229.

    Exactly one action must be provided: ``callback_data``, ``url``, or
    ``copy_text``. The helper returns a ``PageButton`` ready to be placed in a
    ``PageBlockButtonRow`` inside an ``InputRichMessage``.

    Args:
        text: The text displayed on the button.
        callback_data: Data sent to the bot when the button is pressed. Strings
            are encoded as UTF-8 bytes automatically.
        url: The HTTPS or Telegram URL opened when the button is pressed.
        copy_text: Text copied to the user's clipboard when the button is
            pressed.
        bg_primary: Use the primary background button style.
        bg_danger: Use the danger background button style.
        bg_success: Use the success background button style.
        link: Use the link button style. URL buttons enable this automatically.

    Returns:
        A raw ``PageButton`` object for a rich message button row.

    Raises:
        ValueError: If zero or more than one button action is provided.

    Examples:
        >>> richbutton("Run", callback_data="run")
        >>> richbutton("Open docs", url="https://core.telegram.org")
        >>> richbutton("Copy", copy_text="text to copy")
        >>> richbutton("Delete", callback_data=b"delete", bg_danger=True)
    """
    actions = [callback_data is not None, url is not None, copy_text is not None]
    if sum(actions) != 1:
        raise ValueError("Provide exactly one of callback_data, url, or copy_text")

    style = raw.types.RichButtonStyle(
        bg_primary=bg_primary,
        bg_danger=bg_danger,
        bg_success=bg_success,
        link=link or url is not None,
    )

    if callback_data is not None:
        data = callback_data.encode("utf-8") if isinstance(callback_data, str) else callback_data
        button_type: raw.base.InlineButtonType = raw.types.InlineButtonTypeCallback(data=data)
    elif url is not None:
        button_type = raw.types.InlineButtonTypeUrl(url=url)
    else:
        button_type = raw.types.InlineButtonTypeCopy(copy_text=copy_text)

    return raw.types.PageButton(
        text=raw.types.TextPlain(text=text),
        type=button_type,
        style=style,
    )


def bki(keyboard: InlineKeyboardMarkup) -> List[List[List[Any]]]:
    """Converting an InlineKeyboardMarkup back into a list structure of buttons."""
    lines = []
    for row in keyboard.inline_keyboard:
        line = []
        for button in row:
            line.append(ntb(button))
        lines.append(line)
    return lines


def ntb(button: InlineKeyboardButton) -> List[Any]:
    """Convert an InlineKeyboardButton into a list representation."""
    btn_type = "callback_data"
    for t in [
        "callback_data",
        "url",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "callback_game",
    ]:
        value = getattr(button, t, None)
        if value is not None:
            btn_type = t
            break

    res = [button.text, value]
    if btn_type != "callback_data":
        res.append(btn_type)
    return res


def clean_emoji(text: Optional[str]) -> Optional[str]:
    """Removes Telegram custom emoji XML tags from text strings."""
    if not text:
        return text
    return re.sub(r"<emoji id=\d+>(.*?)</emoji>", r"\1", text).strip()


def force_reply(selective: bool = True) -> ForceReply:
    """Create a ForceReply object."""
    return ForceReply(selective=selective)


def array_chunk(input_array: List[Any], size: int) -> List[List[Any]]:
    """Split a 1D array/list into multiple rows of size `size`."""
    return [input_array[i : i + size] for i in range(0, len(input_array), size)]


kbtn = KeyboardButton
"""Alias ​​for KeyboardButton."""
