import logging
from typing import List, Optional, Union

import pyrogram_styled
from pyrogram_styled import raw, types

log = logging.getLogger(__name__)


class SendEphemeralMessage:
    async def send_ephemeral_message(
        self: "pyrogram_styled.Client",
        chat_id: Union[int, str],
        user_id: Union[int, str],
        text: str,
        query_id: Optional[int] = None,
        entities: Optional[List["raw.base.MessageEntity"]] = None,
        media: Optional["raw.base.InputMedia"] = None,
        rich_message: Optional["types.InputRichMessage"] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[
            Union[
                "types.InlineKeyboardMarkup",
                "types.ReplyKeyboardMarkup",
                "types.ReplyKeyboardRemove",
                "types.ForceReply",
            ]
        ] = None,
    ) -> "types.EphemeralMessage":
        """Send a message visible only to a specific user inside a chat.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat
                (the group/channel where the ephemeral message will live).

            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the receiver
                user who is allowed to see this ephemeral message.

            text (``str``):
                Text of the message to be sent.

            query_id (``int`` 64-bit, *optional*):
                Identifier of the inline query this message answers, if any.

            entities (List of :obj:`MessageEntity <pyrogram_styled.raw.base.MessageEntity>`, *optional*):
                List of special entities that appear in the message text.

            media (:obj:`InputMedia <pyrogram_styled.raw.base.InputMedia>`, *optional*):
                Raw media object to attach. Use :meth:`~pyrogram_styled.Client.save_file`
                and wrap the result in ``raw.types.InputMediaUploadedPhoto`` /
                ``InputMediaUploadedDocument`` to attach local files.

            rich_message (:obj:`~pyrogram_styled.types.InputRichMessage`, *optional*):
                Rich (HTML) formatted message content.

            reply_to_message_id (``int``, *optional*):
                If set, replies to an existing ephemeral message with this id.

            reply_markup (:obj:`~pyrogram_styled.types.InlineKeyboardMarkup` | :obj:`~pyrogram_styled.types.ReplyKeyboardMarkup` | :obj:`~pyrogram_styled.types.ReplyKeyboardRemove` | :obj:`~pyrogram_styled.types.ForceReply`, *optional*):
                Additional interface options.

        Returns:
            :obj:`~pyrogram_styled.types.EphemeralMessage`: On success, the sent ephemeral message is returned.

        Example:
            .. code-block:: python

                await app.send_ephemeral_message(
                    chat_id=chat_id,
                    user_id=user_id,
                    text="Ini rahasia cuma lo yang bisa liat",
                )
        """
        group_peer = await self.resolve_peer(chat_id)
        user_peer = await self.resolve_peer(user_id)

        receiver = raw.types.InputUser(
            user_id=user_peer.user_id,
            access_hash=user_peer.access_hash,
        )

        reply_to = None
        if reply_to_message_id:
            reply_to = raw.types.InputReplyToEphemeralMessage(id=reply_to_message_id)

        r = await self.invoke(
            raw.functions.ephemeral.SendMessage(
                peer=group_peer,
                receiver_id=receiver,
                message=text,
                random_id=self.rnd_id(),
                query_id=query_id,
                entities=entities,
                media=media,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                rich_message=rich_message.write() if rich_message else None,
                reply_to=reply_to,
            ),
        )

        for update in r.updates:
            if isinstance(update, raw.types.UpdateNewEphemeralMessage):
                users = {u.id: u for u in r.users}
                chats = {c.id: c for c in r.chats}
                return await types.EphemeralMessage._parse(
                    self, update.message, users, chats
                )

        log.warning("No UpdateNewEphemeralMessage found in response: %s", r)