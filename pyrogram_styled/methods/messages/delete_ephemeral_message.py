from typing import Union

import pyrogram_styled
from pyrogram_styled import raw


class DeleteEphemeralMessage:
    async def delete_ephemeral_message(
        self: "pyrogram_styled.Client",
        chat_id: Union[int, str],
        user_id: Union[int, str],
        message_id: int,
    ) -> bool:
        """Delete an ephemeral message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the receiver user.

            message_id (``int``):
                Identifier of the ephemeral message to delete.

        Returns:
            ``bool``: True on success.
        """
        group_peer = await self.resolve_peer(chat_id)
        user_peer = await self.resolve_peer(user_id)

        receiver = raw.types.InputUser(
            user_id=user_peer.user_id,
            access_hash=user_peer.access_hash,
        )

        return await self.invoke(
            raw.functions.ephemeral.DeleteMessage(
                peer=group_peer,
                receiver_id=receiver,
                id=message_id,
            )
        )