import pyrogram_styled
from pyrogram_styled import raw, types, utils
from ..object import Object


class EphemeralMessage(Object):
    """A message visible only to a specific receiver inside a chat (whisper-style)."""

    def __init__(
        self,
        *,
        client: "pyrogram_styled.Client" = None,
        id: int,
        from_user: "types.User" = None,
        chat: "types.Chat" = None,
        receiver_id: int,
        date=None,
        text: str = None,
        outgoing: bool = None,
        top_msg_id: int = None,
        entities: list = None,
        media=None,
        reply_markup=None,
        reply_to=None,
    ):
        super().__init__(client)

        self.id = id
        self.from_user = from_user
        self.chat = chat
        self.receiver_id = receiver_id
        self.date = date
        self.text = text
        self.outgoing = outgoing
        self.top_msg_id = top_msg_id
        self.entities = entities or []
        self.media = media
        self.reply_markup = reply_markup
        self.reply_to = reply_to

    @staticmethod
    async def _parse(
        client: "pyrogram_styled.Client",
        ephemeral: "raw.types.EphemeralMessage",
        users: dict,
        chats: dict,
    ) -> "EphemeralMessage":
        from_user = None
        if isinstance(ephemeral.from_id, raw.types.PeerUser):
            user = users.get(ephemeral.from_id.user_id)
            if user:
                from_user = types.User._parse(client, user)

        chat = None
        if isinstance(ephemeral.peer_id, raw.types.PeerChannel):
            c = chats.get(ephemeral.peer_id.channel_id)
            if c:
                chat = types.Chat._parse_channel_chat(client, c)
        elif isinstance(ephemeral.peer_id, raw.types.PeerChat):
            c = chats.get(ephemeral.peer_id.chat_id)
            if c:
                chat = types.Chat._parse_chat_chat(client, c)
        elif isinstance(ephemeral.peer_id, raw.types.PeerUser):
            u = users.get(ephemeral.peer_id.user_id)
            if u:
                chat = types.Chat._parse_user_chat(client, u)

        return EphemeralMessage(
            client=client,
            id=ephemeral.id,
            from_user=from_user,
            chat=chat,
            receiver_id=ephemeral.receiver_id,
            date=utils.timestamp_to_datetime(ephemeral.date),
            text=ephemeral.message,
            outgoing=ephemeral.out,
            top_msg_id=ephemeral.top_msg_id,
            entities=ephemeral.entities,
            media=ephemeral.media,
            reply_markup=ephemeral.reply_markup,
            reply_to=ephemeral.reply_to,
        )