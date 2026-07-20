#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional

import pyrogram_styled
from pyrogram_styled import raw, enums
from pyrogram_styled import types
from pyrogram_styled import utils
from .inline_session import get_session


class EditInlineText:
    async def edit_inline_text(
        self: "pyrogram_styled.Client",
        inline_message_id: str,
        text: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[list["types.MessageEntity"]] = None,
        rich_message: Optional["types.InputRichMessage"] = None,
        disable_web_page_preview: bool = None,
        reply_markup: "types.InlineKeyboardMarkup" = None
    ) -> bool:
        """Edit the text of inline messages.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            inline_message_id (``str``):
                Identifier of the inline message.

            text (``str``):
                New text of the message.

            parse_mode (:obj:`~pyrogram_styled.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`~pyrogram_styled.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            rich_message (:obj:`~pyrogram_styled.types.InputRichMessage`, *optional*):
                New rich content of the message.
                Required if ``text`` isn't specified.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Bots only

                # Simple edit text
                await app.edit_inline_text(inline_message_id, "new text")

                # Edit rich text
                await app.edit_inline_text(
                    inline_message_id,
                    rich_message=types.InputRichMessage(
                        html="new <b>text</b>"
                    )
                )

                # Take the same text message, remove the web page preview only
                await app.edit_inline_text(
                    inline_message_id, message.text,
                    disable_web_page_preview=True)
        """

        unpacked = utils.unpack_inline_message_id(inline_message_id)
        dc_id = unpacked.dc_id

        session = await get_session(self, dc_id)

        message = ""
        _entities = None
        input_rich_message = None

        if text is not None:
            message, _entities = (
                await utils.parse_text_entities(self, text, parse_mode, entities)
            ).values()
        elif rich_message is not None:
            input_rich_message = rich_message.write()
        else:
            raise ValueError("Either text or rich_message must be specified")

        return await session.invoke(
            raw.functions.messages.EditInlineBotMessage(
                id=unpacked,
                no_webpage=disable_web_page_preview or None,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                message=message,
                entities=_entities,
                rich_message=input_rich_message,
            ),
            sleep_threshold=self.sleep_threshold
        )
