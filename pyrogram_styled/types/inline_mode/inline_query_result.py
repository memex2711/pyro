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

from uuid import uuid4

import pyrogram_styled
from pyrogram_styled import types
from ..object import Object


class InlineQueryResult(Object):
    """One result of an inline query.

    - :obj:`~pyrogram_styled.types.InlineQueryResultCachedAudio`
    - :obj:`~pyrogram_styled.types.InlineQueryResultCachedDocument`
    - :obj:`~pyrogram_styled.types.InlineQueryResultCachedAnimation`
    - :obj:`~pyrogram_styled.types.InlineQueryResultCachedPhoto`
    - :obj:`~pyrogram_styled.types.InlineQueryResultCachedSticker`
    - :obj:`~pyrogram_styled.types.InlineQueryResultCachedVideo`
    - :obj:`~pyrogram_styled.types.InlineQueryResultCachedVoice`
    - :obj:`~pyrogram_styled.types.InlineQueryResultArticle`
    - :obj:`~pyrogram_styled.types.InlineQueryResultAudio`
    - :obj:`~pyrogram_styled.types.InlineQueryResultContact`
    - :obj:`~pyrogram_styled.types.InlineQueryResultDocument`
    - :obj:`~pyrogram_styled.types.InlineQueryResultAnimation`
    - :obj:`~pyrogram_styled.types.InlineQueryResultLocation`
    - :obj:`~pyrogram_styled.types.InlineQueryResultPhoto`
    - :obj:`~pyrogram_styled.types.InlineQueryResultVenue`
    - :obj:`~pyrogram_styled.types.InlineQueryResultVideo`
    - :obj:`~pyrogram_styled.types.InlineQueryResultVoice`
    """

    def __init__(
        self,
        type: str,
        id: str,
        input_message_content: "types.InputMessageContent",
        reply_markup: "types.InlineKeyboardMarkup"
    ):
        super().__init__()

        self.type = type
        self.id = str(uuid4()) if id is None else str(id)
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup

    async def write(self, client: "pyrogram_styled.Client"):
        pass
