import re

from typing import Any, Dict, List, Optional, Tuple, Union
from pyrogram_styled.types import (
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    CopyTextButton,
    ForceReply
)
from pyrogram_styled.enums import ButtonStyle

ButtonTuple = Tuple[str, Any, str, ButtonStyle, str]
ButtonInput = Union[
    str, Dict[str, Any], InlineKeyboardButton, KeyboardButton, ButtonTuple
]


_STYLE_MAP: Dict[str, ButtonStyle] = {
    # Default
    "default": ButtonStyle.DEFAULT,
    "d": ButtonStyle.DEFAULT,
    # Primary / Blue
    "primary": ButtonStyle.PRIMARY,
    "b": ButtonStyle.PRIMARY,
    "blue": ButtonStyle.PRIMARY,
    # Success / Green
    "success": ButtonStyle.SUCCESS,
    "g":  ButtonStyle.SUCCESS,
    "green": ButtonStyle.SUCCESS,
    # Danger / Red
    "danger": ButtonStyle.DANGER,
    "r": ButtonStyle.DANGER,
    "red": ButtonStyle.DANGER,
}


def parse_style(style: Union[str, ButtonStyle, None]) -> Optional[ButtonStyle]:
    """
    Konversi string atau ButtonStyle ke objek ButtonStyle.

    Alias yang didukung:
        "default" / "d"
        "primary" / "blue" / "b"
        "success" / "green" / "g"
        "danger"  / "red"   / "r"

    Contoh:
        parse_style("red")    → ButtonStyle.DANGER
        parse_style("g")      → ButtonStyle.SUCCESS
        parse_style(None)     → None
    """
    if style is None:
        return None
    if isinstance(style, ButtonStyle):
        return style
    key = str(style).lower().strip()
    result = _STYLE_MAP.get(key)
    if result is None:
        valid = ", ".join(sorted(_STYLE_MAP.keys()))
        raise ValueError(f"Style '{style}' tidak dikenal. Pilihan valid: {valid}")
    return result


# ── Helpers ────────────────────────────────────────────────────────────────────

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
            button = ntb(button)
            line.append(button)
        lines.append(line)
    return lines


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


def _normalize_rows(rows: List[Any]) -> List[List[Any]]:
    """
    Internal helper untuk mendeteksi dan mengubah list 1-Dimensi (sejajar)
    menjadi list 2-Dimensi (multi-baris) secara otomatis.
    """
    if not rows:
        return []

    first_item = rows[0]
    is_1d = False

    if isinstance(first_item, (str, dict, InlineKeyboardButton, KeyboardButton)):
        is_1d = True
    elif isinstance(first_item, tuple):
        if len(first_item) > 0 and isinstance(first_item[0], str):
            is_1d = True

    return [rows] if is_1d else rows


def ikb(rows: List[Any] = None) -> InlineKeyboardMarkup:
    """
    Membuat objek InlineKeyboardMarkup secara dinamis.
    Mendukung auto-normalization (list 1D otomatis dikonversi ke list 2D).

    Parameter style kini menerima string selain ButtonStyle:
        "red"/"r", "green"/"g", "blue"/"b", "default"/"d"

    Format Tuple Tombol yang didukung:
    - 2 Elemen: (text, value)
    - 3 Elemen:
      * (text, value, style)   → style bisa str atau ButtonStyle
      * (text, value, type)    → tipe khusus: url, copy_text, web_app, dll
      * (text, value, icon)    → icon emoji ID (string numerik panjang)
    - 4 Elemen:
      * (text, value, style, icon)
      * (text, value, type, style)
      * (text, value, type, icon)
    - 5 Elemen: (text, value, type, style, icon)

    Contoh:
        >>> ikb([
        >>>     [("✅ Konfirmasi", "ok", "green"), ("❌ Batal", "cancel", "red")],
        >>>     [("🔗 Link", "https://t.me/bot", "url", "blue")],
        >>>     [("📋 Copy", "12345", "copy_text", ButtonStyle.SUCCESS, "5249053508")],
        >>> ])
    """
    if rows is None:
        rows = []

    rows = _normalize_rows(rows)

    _KNOWN_TYPES = frozenset({
        "callback_data",
        "url",
        "copy_text",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "web_app",
    })

    def _is_style(val) -> bool:
        """Cek apakah val adalah style (ButtonStyle atau string style yang dikenal)."""
        if isinstance(val, ButtonStyle):
            return True
        if isinstance(val, str) and val.lower().strip() in _STYLE_MAP:
            return True
        return False

    def _is_known_type(val) -> bool:
        return isinstance(val, str) and val in _KNOWN_TYPES

    lines = []
    for row in rows:
        line = []
        for button in row:
            if isinstance(button, InlineKeyboardButton):
                line.append(button)
                continue

            if isinstance(button, str):
                button = btn(button, button)

            elif isinstance(button, (list, tuple)):
                button_len = len(button)

                if button_len == 5:
                    text, value, typ, style, icon = button
                    button = btn(text, value, typ, style, icon)

                elif button_len == 4:
                    text, value, third, fourth = button
                    if _is_known_type(third):
                        # (text, value, type, style) atau (text, value, type, icon)
                        if _is_style(fourth):
                            button = btn(text, value, typ=third, style=fourth)
                        else:
                            button = btn(text, value, typ=third, icon=fourth)
                    elif _is_style(third):
                        # (text, value, style, icon)
                        button = btn(text, value, style=third, icon=fourth)
                    else:
                        # (text, value, type, icon) — fallback
                        button = btn(text, value, typ=third, icon=fourth)

                elif button_len == 3:
                    text, value, third = button
                    if _is_known_type(third):
                        # (text, value, type)
                        button = btn(text, value, typ=third)
                    elif _is_style(third):
                        # (text, value, style)
                        button = btn(text, value, style=third)
                    else:
                        # (text, value, icon)
                        button = btn(text, value, icon=third)

                elif button_len == 2:
                    text, value = button
                    button = btn(text, value)

                else:
                    button = btn(*button)

            else:
                button = btn(str(button), str(button))

            line.append(button)
        lines.append(line)

    return InlineKeyboardMarkup(inline_keyboard=lines)


def kb(rows: List[Any] = None, **kwargs) -> ReplyKeyboardMarkup:
    """
    Membuat objek ReplyKeyboardMarkup secara dinamis.
    Mendukung auto-normalization (list 1D otomatis dikonversi ke list 2D).

    Parameter style kini menerima string selain ButtonStyle.

    Format Input Tombol yang didukung:
    - str: Tombol teks biasa.
    - dict: Unpacked sebagai kwargs KeyboardButton.
    - KeyboardButton: Objek tombol manual.
    - Tuple 2 Elemen:
      * (text, style) → style bisa str atau ButtonStyle
      * (text, icon)  → icon emoji ID
    - Tuple 3 Elemen: (text, style, icon)

    Contoh:
        >>> kb([
        >>>     [("Premium 👑", "primary"), ("Admin 👤", "52490535")],
        >>>     ["Kembali ke Menu"]
        >>> ], resize_keyboard=True)
    """
    if rows is None:
        rows = []

    rows = _normalize_rows(rows)

    lines = []
    for row in rows:
        line = []
        for button in row:
            if isinstance(button, KeyboardButton):
                line.append(button)
                continue

            if isinstance(button, str):
                button = KeyboardButton(button)
            elif isinstance(button, dict):
                button = KeyboardButton(**button)
            elif isinstance(button, tuple):
                button_len = len(button)
                if button_len == 3:
                    text, style, icon = button
                    button = KeyboardButton(
                        text,
                        style=parse_style(style),
                        icon_custom_emoji_id=icon
                    )
                elif button_len == 2:
                    text, second = button
                    if isinstance(second, (ButtonStyle, str)) and second in _STYLE_MAP or isinstance(second, ButtonStyle):
                        button = KeyboardButton(text, style=parse_style(second))
                    else:
                        button = KeyboardButton(text, icon_custom_emoji_id=second)
                else:
                    button = KeyboardButton(str(button[0]))
            else:
                button = KeyboardButton(str(button))

            line.append(button)
        lines.append(line)

    return ReplyKeyboardMarkup(keyboard=lines, **kwargs)


def btn(
    text: str,
    value: Any,
    typ: str = "callback_data",
    style: Union[str, ButtonStyle, None] = None,
    icon: str = None,
) -> InlineKeyboardButton:
    """
    Membuat objek tunggal InlineKeyboardButton.

    Parameters:
        text  (str): Label tombol.
        value (Any): Payload (callback string, url, teks salin, dll).
        typ   (str): Tipe aksi. Default: "callback_data".
                     Mendukung: "url", "copy_text", "web_app", dll.
        style (str | ButtonStyle, opsional): Warna tombol.
              Bisa string: "red"/"r", "green"/"g", "blue"/"b", dll.
        icon  (str, opsional): ID custom emoji ikon tombol.

    Contoh:
        btn("Hapus", "del_123", style="red")
        btn("Link", "https://t.me/bot", typ="url", style="blue")
        btn("Copy", "ABC123", typ="copy_text", style="g", icon="5249053508")
    """
    if not isinstance(typ, str):
        raise TypeError(f"Parameter 'type' harus string, got {type(typ)}")

    # Parse style string → ButtonStyle
    resolved_style = parse_style(style)

    if typ == "callback_data" and not isinstance(value, (bytes, str)):
        value = str(value)

    if typ == "copy_text" and isinstance(value, (str, int)):
        value = CopyTextButton(text=str(value))

    kwargs = {typ: value}
    if resolved_style is not None:
        kwargs["style"] = resolved_style
    if icon is not None:
        kwargs["icon_custom_emoji_id"] = icon

    return InlineKeyboardButton(text, **kwargs)


def clean_emoji(text: str) -> str:
    """
    Menghapus tag XML custom emoji Telegram dari string teks.

    Contoh:
        >>> clean_emoji("<emoji id=5301083932211550593>🔥</emoji> Bot Started")
        "🔥 Bot Started"
    """
    if not text:
        return None
    text = re.sub(r"<emoji id=\d+>(.*?)</emoji>", r"\1", text)
    return text.strip()


kbtn = KeyboardButton
"""Alias untuk KeyboardButton."""


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
