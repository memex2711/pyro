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
    Membuat objek InlineKeyboardMarkup (Keyboard di dalam pesan) secara dinamis.
    Mendukung auto-normalization (list 1D otomatis dikonversi ke list 2D).

    Format Tuple Tombol yang didukung:
    - 2 Elemen: (text, value) -> Default callback data.
      Contoh: ("Beli", "buy_item")
    - 3 Elemen:
      * (text, value, ButtonStyle) -> Callback dengan warna khusus.
        Contoh: ("Hapus", "del", ButtonStyle.DANGER)
      * (text, value, type) -> Tombol dengan tipe khusus (url, copy_text, web_app).
        Contoh: ("Google", "https://google.com", "url")
      * (text, value, icon) -> Callback dengan ikon emoji kustom.
        Contoh: ("Mainkan", "play", "5301083932211550593")
    - 4 Elemen:
      * (text, value, style, icon) -> Callback dengan warna dan ikon.
        Contoh: ("Alert", "alert", ButtonStyle.DANGER, "5249053508")
      * (text, value, type, ButtonStyle) -> Tipe khusus dengan warna khusus.
        Contoh: ("Buka Web", "https://site.com", "web_app", ButtonStyle.PRIMARY)
      * (text, value, type, icon) -> Tipe khusus dengan ikon kustom.
        Contoh: ("Group", "https://t.me/...", "url", "5301083932")
    - 5 Elemen: (text, value, type, style, icon) -> Konfigurasi tombol lengkap.
      Contoh: ("Copy", "12345", "copy_text", ButtonStyle.SUCCESS, "52490535")

    Contoh Penggunaan:
        >>> markup = ikb([
        >>>     [("🌐 Google", "https://google.com", "url"), ("📋 Salin ID", "12345", "copy_text")],
        >>>     [("🗑️ Hapus Data", "confirm_delete", ButtonStyle.DANGER, "5249053508681883137")]
        >>> ])
    """
    if rows is None:
        rows = []

    rows = _normalize_rows(rows)

    _KNOWN_TYPES = frozenset(
        {
            "callback_data",
            "url",
            "copy_text",
            "switch_inline_query",
            "switch_inline_query_current_chat",
            "web_app",
        }
    )

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
                    if isinstance(button[2], ButtonStyle):
                        text, value, style, icon = button
                        button = btn(text, value, style=style, icon=icon)
                    else:
                        text, value, typ, icon_or_style = button
                        if isinstance(icon_or_style, ButtonStyle):
                            button = btn(text, value, typ=typ, style=icon_or_style)
                        else:
                            button = btn(text, value, typ=typ, icon=icon_or_style)
                elif button_len == 3:
                    if isinstance(button[2], ButtonStyle):
                        text, value, style = button
                        button = btn(text, value, style=style)
                    elif isinstance(button[2], str) and button[2] in _KNOWN_TYPES:
                        text, value, typ = button
                        button = btn(text, value, typ=typ)
                    else:
                        text, value, icon = button
                        button = btn(text, value, icon=icon)
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
    Membuat objek ReplyKeyboardMarkup (Tombol menu di bawah kolom input chat) secara dinamis.
    Mendukung auto-normalization (list 1D otomatis dikonversi ke list 2D).

    Format Input Tombol yang didukung:
    - str: Tombol teks biasa. Contoh: "Kirim Lokasi"
    - dict: Dikirim sebagai unpacked kwargs. Contoh: {"text": "Kontak", "request_contact": True}
    - KeyboardButton: Objek tombol manual.
    - Tuple 2 Elemen:
      * (text, ButtonStyle) -> Tombol menu dengan warna/gaya khusus.
        Contoh: ("Utama 🏠", ButtonStyle.PRIMARY)
      * (text, icon) -> Tombol menu dengan custom emoji ID khusus.
        Contoh: ("Bantuan ❓", "5301083932211550593")
    - Tuple 3 Elemen: (text, style, icon) -> Tombol lengkap dengan warna dan emoji.
      Contoh: ("Setting ⚙️", ButtonStyle.SECONDARY, "5249053508681883137")

    Contoh Penggunaan:
        >>> reply_markup = kb([
        >>>     [("Layanan Premium 👑", ButtonStyle.PRIMARY), ("Hubungi Admin 👤", "52490535")],
        >>>     ["Kembali ke Menu Utama"]
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
                        text, style=style, icon_custom_emoji_id=icon
                    )
                elif button_len == 2:
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


def btn(
    text: str,
    value: Any,
    typ: str = "callback_data",
    style: ButtonStyle = None,
    icon: str = None,
) -> InlineKeyboardButton:
    """
    Membuat objek tunggal InlineKeyboardButton secara manual.

    Parameters:
        text (str): Teks label yang akan ditampilkan di tombol.
        value (Any): Payload tombol (bisa string callback, url, atau teks salin).
        typ (str): Tipe aksi tombol. Default: "callback_data". 
                   Mendukung: "url", "copy_text", "web_app", dll.
        style (ButtonStyle, opsional): Warna/gaya khusus untuk tombol.
        icon (str, opsional): ID custom emoji yang akan ditaruh sebagai ikon tombol.

    Returns:
        InlineKeyboardButton: Objek tombol yang telah terkonfigurasi.
    """
    if not isinstance(typ, str):
        raise TypeError(f"Parameter 'type' harus string, got {type(typ)}")

    if typ == "callback_data" and not isinstance(value, (bytes, str)):
        value = str(value)

    if typ == "copy_text" and isinstance(value, (str, int)):
        value = CopyTextButton(text=str(value))

    kwargs = {typ: value}
    if style is not None:
        kwargs["style"] = style
    if icon is not None:
        kwargs["icon_custom_emoji_id"] = icon

    return InlineKeyboardButton(text, **kwargs)


def clean_emoji(text: str) -> str:
    """
    Menghapus tag XML custom emoji Telegram secara bersih dari string teks yang diberikan.

    Contoh:
        >>> clean_emoji("<emoji id=5301083932211550593>🔥</emoji> Bot Started")
        "🔥 Bot Started"
    """
    if not text:
        return None
    text = re.sub(r"<emoji id=\d+>(.*?)</emoji>", r"\1", text)
    return text.strip()

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