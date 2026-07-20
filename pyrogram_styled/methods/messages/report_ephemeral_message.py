from typing import Union

import pyrogram_styled
from pyrogram_styled import raw


class ReportEphemeralMessage:
    async def report_ephemeral_message(
        self: "pyrogram_styled.Client",
        chat_id: Union[int, str],
        message_id: int,
        option: bytes,
        message: str = "",
    ) -> "raw.base.ReportResult":
        """Report an ephemeral message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the ephemeral message to report.

            option (``bytes``):
                Report option chosen, as returned by Telegram's report flow.

            message (``str``, *optional*):
                Additional comment for the report.

        Returns:
            :obj:`ReportResult <pyrogram_styled.raw.base.ReportResult>`
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.ephemeral.ReportMessage(
                peer=peer,
                id=message_id,
                option=option,
                message=message,
            )
        )