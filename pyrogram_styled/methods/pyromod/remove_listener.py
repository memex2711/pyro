#  pyrogram_styled - Telegram MTProto API Client Library for Python
#  Copyright (C) 2020-present Cezar H. <https://github.com/usernein>
#  Copyright (C) 2023-present pyrogram_styled <https://pyrogram_styled.org>
#
#  This file is part of pyrogram_styled.
#
#  pyrogram_styled is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  pyrogram_styled is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with pyrogram_styled.  If not, see <http://www.gnu.org/licenses/>.

import contextlib
from typing import TYPE_CHECKING

from pyrogram_styled.types import Listener

if TYPE_CHECKING:
    import pyrogram_styled


class RemoveListener:
    def remove_listener(self: "pyrogram_styled.Client", listener: Listener):
        """
        Removes a listener from the :meth:`pyrogram_styled.Client.listeners` dictionary.

        Parameters:
            listener (:obj:`~pyrogram_styled.types.Listener`):
                The listener to remove.
        """
        with contextlib.suppress(ValueError):
            self.listeners[listener.listener_type].remove(listener)
