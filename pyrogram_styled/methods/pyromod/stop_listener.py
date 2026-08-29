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

import inspect
from typing import TYPE_CHECKING

from pyrogram_styled.errors import (
    ListenerStopped,
)
from pyrogram_styled.types import Listener
from pyrogram_styled.utils import PyromodConfig

if TYPE_CHECKING:
    import pyrogram_styled


class StopListener:
    async def stop_listener(self: "pyrogram_styled.Client", listener: Listener):
        """
        Stops a listener, calling stopped_handler if applicable or raising ListenerStopped if throw_exceptions is True.

        Parameters:
            listener (:obj:`~pyrogram_styled.types.Listener`):
                The :class:`pyrogram_styled.types.Listener` to stop.

        Returns:
            None

        Raises:
            ListenerStopped: If throw_exceptions is True.
        """
        self.remove_listener(listener)

        if listener.future.done():
            return

        if callable(PyromodConfig.stopped_handler):
            if inspect.iscoroutinefunction(PyromodConfig.stopped_handler.__call__):
                await PyromodConfig.stopped_handler(None, listener)
            else:
                await self.loop.run_in_executor(
                    None, PyromodConfig.stopped_handler, None, listener
                )
        elif PyromodConfig.throw_exceptions:
            listener.future.set_exception(ListenerStopped())
