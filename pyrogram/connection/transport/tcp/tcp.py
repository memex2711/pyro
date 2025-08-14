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
"""
import asyncio
import ipaddress
import logging
import socket
from concurrent.futures import ThreadPoolExecutor

import socks

log = logging.getLogger(__name__)


class TCP:
    TIMEOUT = 10

    def __init__(self, ipv6: bool, proxy: dict):
        self.socket = None

        self.reader = None
        self.writer = None

        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()

        self.proxy = proxy

        if proxy:
            hostname = proxy.get("hostname")

            try:
                ip_address = ipaddress.ip_address(hostname)
            except ValueError:
                self.socket = socks.socksocket(socket.AF_INET)
            else:
                if isinstance(ip_address, ipaddress.IPv6Address):
                    self.socket = socks.socksocket(socket.AF_INET6)
                else:
                    self.socket = socks.socksocket(socket.AF_INET)

            self.socket.set_proxy(
                proxy_type=getattr(socks, proxy.get("scheme").upper()),
                addr=hostname,
                port=proxy.get("port", None),
                username=proxy.get("username", None),
                password=proxy.get("password", None)
            )

            self.socket.settimeout(TCP.TIMEOUT)

            log.info("Using proxy %s", hostname)
        else:
            self.socket = socket.socket(
                socket.AF_INET6 if ipv6
                else socket.AF_INET
            )

            self.socket.setblocking(False)

    async def connect(self, address: tuple):
        if self.proxy:
            with ThreadPoolExecutor(1) as executor:
                await self.loop.run_in_executor(executor, self.socket.connect, address)
        else:
            try:
                await asyncio.wait_for(asyncio.get_event_loop().sock_connect(self.socket, address), TCP.TIMEOUT)
            except asyncio.TimeoutError:  # Re-raise as TimeoutError. asyncio.TimeoutError is deprecated in 3.11
                raise TimeoutError("Connection timed out")

        self.reader, self.writer = await asyncio.open_connection(sock=self.socket)

    async def close(self):
        try:
            if self.writer is not None:
                self.writer.close()
                await asyncio.wait_for(self.writer.wait_closed(), TCP.TIMEOUT)
        except Exception as e:
            log.info("Close exception: %s %s", type(e).__name__, e)

    async def send(self, data: bytes):
        async with self.lock:
            try:
                if self.writer is not None:
                    if self.writer.is_closing():
                        raise OSError("Writer already closed")
                    self.writer.write(data)
                    await self.writer.drain()
            except Exception as e:
                log.info("Send exception: %s %s", type(e).__name__, e)
                raise OSError(e)

    async def recv(self, length: int = 0):
        data = b""

        while len(data) < length:
            try:
                chunk = await asyncio.wait_for(
                    self.reader.read(length - len(data)),
                    TCP.TIMEOUT
                )
            except (OSError, asyncio.TimeoutError):
                return None
            else:
                if chunk:
                    data += chunk
                else:
                    return None

        return data
"""

import asyncio
import ipaddress
import logging
import socket
from concurrent.futures import ThreadPoolExecutor
import socks

log = logging.getLogger(__name__)

class TCP:
    TIMEOUT = 10

    def __init__(self, ipv6: bool, proxy: dict):
        self.socket = None
        self.reader = None
        self.writer = None
        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()
        self.proxy = proxy
        self.last_address = None
        self._closed = False
        self._ipv6 = ipv6

        self._init_socket(ipv6)

    def _init_socket(self, family=None):
        if family is None:
            family = socket.AF_INET6 if self._ipv6 else socket.AF_INET
        self.socket = socket.socket(family, socket.SOCK_STREAM)
        self.socket.setblocking(False)

    async def connect(self, address: tuple):
        if not isinstance(address, tuple) or len(address) != 2:
            raise ValueError(f"Invalid address: {address}")

        self.last_address = address
        log.info("Connecting to %s:%s", *address)

        if self.proxy:
            with ThreadPoolExecutor(1) as executor:
                await self.loop.run_in_executor(executor, self.socket.connect, address)
        else:
            try:
                log.debug(f"Resolving hostname {address[0]}...")
                infos = await asyncio.wait_for(
                    self.loop.getaddrinfo(address[0], address[1], type=socket.SOCK_STREAM),
                    TCP.TIMEOUT
                )
                family, socktype, proto, canonname, sockaddr = infos[0]

                self._init_socket(family)

                log.debug(f"Connecting to {sockaddr}...")
                await asyncio.wait_for(
                    self.loop.sock_connect(self.socket, sockaddr),
                    TCP.TIMEOUT
                )

            except asyncio.TimeoutError:
                raise TimeoutError(f"Connection to {address} timed out")
            except socket.gaierror as e:
                raise OSError(f"DNS resolution failed for {address[0]}: {e}")

        self.reader, self.writer = await asyncio.open_connection(sock=self.socket)
        self._closed = False
        log.info("Connected to %s:%s", *address)

    async def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            if self.writer:
                self.writer.close()
                try:
                    await asyncio.wait_for(self.writer.wait_closed(), TCP.TIMEOUT)
                except Exception:
                    pass
            if self.reader:
                try:
                    self.reader.feed_eof()
                except Exception:
                    pass
            if self.socket:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    self.socket.close()
                except Exception:
                    pass
                await asyncio.sleep(0)
        finally:
            self.reader = None
            self.writer = None
            self.socket = None

    async def _ensure_connected(self):
        async with self.lock:
            if not self.writer or self.writer.is_closing() or not self.reader:
                if (
                    not self.last_address
                    or not isinstance(self.last_address, tuple)
                    or len(self.last_address) != 2
                ):
                    raise OSError(f"No valid last_address stored for reconnect: {self.last_address}")

                log.warning("TCP connection lost, reconnecting to %s:%s", *self.last_address)

                await self.close()
                await asyncio.sleep(0.05)

                self._init_socket(self.socket.family)

                try:
                    await self.connect(self.last_address)
                except Exception as e:
                    log.error("Reconnect failed: %s", e)
                    raise

    async def send(self, data: bytes):
        async with self.lock:
            await self._ensure_connected()
            self.writer.write(data)
            await self.writer.drain()

    async def recv(self, length: int = 0):
        await self._ensure_connected()
        data = b""
        while len(data) < length:
            try:
                chunk = await asyncio.wait_for(
                    self.reader.read(length - len(data)),
                    TCP.TIMEOUT
                )
            except (OSError, asyncio.TimeoutError):
                log.warning("Recv timeout/disconnect, reconnecting...")
                await self._ensure_connected()
                return None
            if not chunk:
                log.warning("Recv got empty chunk, reconnecting...")
                await self._ensure_connected()
                return None
            data += chunk
        return data
