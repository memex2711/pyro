from typing import List, Dict, Optional
import pyrogram
from pyrogram import raw, utils

class GetDialogs:
    async def get_dialogs(
        self: "pyrogram.Client",
        limit: int = 100
    ) -> List[Dict]:
        """Get a user's dialogs as a list of dictionaries.
        
        This method is patched to return a simplified list of dictionaries 
        instead of Pyrogram Dialog objects.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            limit (``int``, *optional*):
                The chunk size limit for the request.
                Defaults to 100.

        Returns:
            ``List[Dict]``: A list of dictionaries representing dialogs.
            Each dictionary contains:
            - ``id`` (int): The chat/user ID.
            - ``name`` (str): The title or full name.
            - ``type`` (str): "private", "group", "supergroup", or "channel".
            - ``username`` (str, optional): Username if available.
            - ``is_bot`` (bool, optional): True if the user is a bot.
            - ``is_deleted`` (bool, optional): True if the account is deleted.

        Example:
            .. code-block:: python

                # Get all dialogs
                dialogs = await app.get_dialogs()
                
                for dialog in dialogs:
                    print(f"Name: {dialog['name']} | ID: {dialog['id']}")
        """
        dialogs_data = []

        offset_date = 0
        offset_id = 0
        offset_peer = raw.types.InputPeerEmpty()
        chunk_limit = limit if limit <= 100 else 100

        while True:
            try:
                r = await self.invoke(
                    raw.functions.messages.GetDialogs(
                        offset_date=offset_date,
                        offset_id=offset_id,
                        offset_peer=offset_peer,
                        limit=chunk_limit,
                        hash=0
                    )
                )

                if not r.dialogs:
                    break

                chat_map = {c.id: c for c in r.chats}
                user_map = {u.id: u for u in r.users}
                message_map = {m.id: m for m in r.messages}

                for dialog in r.dialogs:
                    peer = dialog.peer
                    entry = None

                    if isinstance(peer, raw.types.PeerUser):
                        user = user_map.get(peer.user_id)
                        if user:
                            first_name = user.first_name or ""
                            last_name = user.last_name or ""
                            full_name = f"{first_name} {last_name}".strip() or "Unknown"

                            entry = {
                                "id": user.id,
                                "name": full_name,
                                "type": "private",
                                "username": user.username,
                                "is_bot": user.bot,
                                "is_deleted": getattr(user, "deleted", False),
                            }

                    elif isinstance(peer, raw.types.PeerChat):
                        chat = chat_map.get(peer.chat_id)
                        if chat and not getattr(chat, "deactivated", False):
                            entry = {
                                "id": -chat.id,
                                "name": chat.title,
                                "type": "group"
                            }

                    elif isinstance(peer, raw.types.PeerChannel):
                        channel = chat_map.get(peer.channel_id)
                        if channel:
                            is_supergroup = getattr(channel, "megagroup", False)
                            chat_type = "supergroup" if is_supergroup else "channel"
                            final_id = utils.get_channel_id(channel.id)

                            entry = {
                                "id": final_id,
                                "name": channel.title,
                                "type": chat_type
                            }

                    if entry:
                        dialogs_data.append(entry)

                last_dialog = r.dialogs[-1]
                offset_peer = self._resolve_input_peer(last_dialog.peer, chat_map, user_map)
                offset_id = last_dialog.top_message

                if offset_id in message_map:
                    offset_date = message_map[offset_id].date
                else:
                    offset_date = 0

                if len(r.dialogs) < chunk_limit:
                    break

            except Exception:
                break

        return dialogs_data

    def _resolve_input_peer(self, peer, chat_map, user_map):
        try:
            if isinstance(peer, raw.types.PeerUser):
                user = user_map.get(peer.user_id)
                if user:
                    return raw.types.InputPeerUser(user_id=user.id, access_hash=user.access_hash)

            elif isinstance(peer, raw.types.PeerChat):
                return raw.types.InputPeerChat(chat_id=peer.chat_id)

            elif isinstance(peer, raw.types.PeerChannel):
                channel = chat_map.get(peer.channel_id)
                if channel:
                    return raw.types.InputPeerChannel(channel_id=channel.id, access_hash=channel.access_hash)
        except Exception:
            pass

        return raw.types.InputPeerEmpty()

    async def get_groups(self: "pyrogram.Client") -> List[Dict]:
        """Get all groups and supergroups from dialogs.

        Returns:
            ``List[Dict]``: A list of dictionaries representing group chats.
        """
        all_chats = await self.get_dialogs()
        return [c for c in all_chats if c["type"] in ["group", "supergroup"]]

    async def get_private_chats(self: "pyrogram.Client") -> List[Dict]:
        """Get all private chats (excluding bots and deleted accounts).

        Returns:
            ``List[Dict]``: A list of dictionaries representing private chats.
        """
        all_chats = await self.get_dialogs()
        return [
            c for c in all_chats 
            if c["type"] == "private" 
            and not c.get("is_bot") 
            and not c.get("is_deleted")
        ]

    async def get_channels(self: "pyrogram.Client") -> List[Dict]:
        """Get all channels from dialogs.

        Returns:
            ``List[Dict]``: A list of dictionaries representing channels.
        """
        all_chats = await self.get_dialogs()
        return [c for c in all_chats if c["type"] == "channel"]

    async def get_bots(self: "pyrogram.Client") -> List[Dict]:
        """Get all bots from dialogs.

        Returns:
            ``List[Dict]``: A list of dictionaries representing bots.
        """
        all_chats = await self.get_dialogs()
        return [c for c in all_chats if c["type"] == "private" and c.get("is_bot")]

    async def get_deleted_users(self: "pyrogram.Client") -> List[Dict]:
        """Get all deleted user accounts from dialogs.

        Returns:
            ``List[Dict]``: A list of dictionaries representing deleted accounts.
        """
        all_chats = await self.get_dialogs()
        return [c for c in all_chats if c["type"] == "private" and c.get("is_deleted")]