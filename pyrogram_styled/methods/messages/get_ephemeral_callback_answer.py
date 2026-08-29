from typing import Optional, Union

import pyrogram_styled
from pyrogram_styled import raw


class GetEphemeralCallbackAnswer:
    async def get_ephemeral_callback_answer(
        self: "pyrogram_styled.Client",
        chat_id: Union[int, str],
        message_id: int,
        data: Optional[bytes] = None,
    ) -> "raw.base.messages.BotCallbackAnswer":
        """Request a callback answer for an inline button on an ephemeral message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the ephemeral message containing the button.

            data (``bytes``, *optional*):
                Callback data of the pressed button.

        Returns:
            :obj:`messages.BotCallbackAnswer <pyrogram_styled.raw.base.messages.BotCallbackAnswer>`
        """
        peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.ephemeral.GetCallbackAnswer(
                peer=peer,
                id=message_id,
                data=data,
            )
        )