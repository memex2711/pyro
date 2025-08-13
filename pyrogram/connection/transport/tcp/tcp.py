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
        self.use_ipv6 = ipv6           
        self.last_address = None       
        self.reconnect_delay = 2       
        self.max_retries = 8           

        self._init_socket(self.use_ipv6)

    def _init_socket(self, ipv6: bool):
        """Inisialisasi socket baru sesuai setting/proxy."""
        if self.proxy:
            hostname = self.proxy.get("hostname")
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
                proxy_type=getattr(socks, self.proxy.get("scheme").upper()),
                addr=hostname,
                port=self.proxy.get("port", None),
                username=self.proxy.get("username", None),
                password=self.proxy.get("password", None)
            )
            self.socket.settimeout(TCP.TIMEOUT)
            log.info("Using proxy %s", hostname)
        else:
            self.socket = socket.socket(socket.AF_INET6 if ipv6 else socket.AF_INET)
            self.socket.setblocking(False)

    async def _reconnect(self):
        """Tutup koneksi & coba connect ulang dengan retry + backoff."""
        if not self.last_address:
            raise OSError("No previous connection address stored, cannot reconnect")

        async with self.lock:
            if self.writer and not self.writer.is_closing():
                return

            try:
                await self.close()
            except Exception as e:
                log.warning("Exception while closing before reconnect: %s", e)

            for attempt in range(1, self.max_retries + 1):
                try:
                    self._init_socket(self.use_ipv6)
                    await self._connect_low(self.last_address)
                    log.info("Reconnected on attempt %d to %s:%s",
                             attempt, self.last_address[0], self.last_address[1])
                    return
                except Exception as e:
                    wait_time = self.reconnect_delay * attempt
                    log.warning("Reconnect attempt %d failed: %s (retry in %ss)",
                                attempt, e, wait_time)
                    await asyncio.sleep(wait_time)

            raise ConnectionError("Max reconnect attempts reached")

    async def _connect_low(self, address: tuple):
        if self.proxy:
            with ThreadPoolExecutor(1) as executor:
                await self.loop.run_in_executor(executor, self.socket.connect, address)
        else:
            try:
                await asyncio.wait_for(
                    asyncio.get_event_loop().sock_connect(self.socket, address),
                    TCP.TIMEOUT
                )
            except asyncio.TimeoutError:
                raise TimeoutError("Connection timed out")

        self.reader, self.writer = await asyncio.open_connection(sock=self.socket)

    async def connect(self, address: tuple):
        self.last_address = address
        log.info("Connecting to %s:%s", address[0], address[1])

        self._init_socket(self.use_ipv6)
        await self._connect_low(address)

        log.info("Connected to %s:%s", address[0], address[1])

    async def close(self):
        """Tutup koneksi TCP."""
        try:
            if self.writer is not None:
                self.writer.close()
                await asyncio.wait_for(self.writer.wait_closed(), TCP.TIMEOUT)
                log.info("TCP connection closed")
        except Exception as e:
            log.warning("Close exception: %s %s", type(e).__name__, e)
        finally:
            self.writer = None
            self.reader = None

    async def send(self, data: bytes):
        """Kirim data ke server, auto-reconnect kalau writer mati."""
        async with self.lock:
            try:
                if self.writer is None or self.writer.is_closing():
                    log.warning("Writer closed/None before send, reconnecting...")
                    await self._reconnect()

                self.writer.write(data)
                await self.writer.drain()
            except Exception as e:
                log.error("Send exception: %s %s", type(e).__name__, e)
                await self._reconnect()
                self.writer.write(data)
                await self.writer.drain()

    async def recv(self, length: int = 0):
        if length <= 0:
            length = 1

        data = b""
        while len(data) < length:
            try:
                chunk = await asyncio.wait_for(
                    self.reader.read(length - len(data)),
                    TCP.TIMEOUT
                )
                if not chunk:
                    log.warning("Recv got empty chunk (EOF). Reconnecting...")
                    await self._reconnect()
                    continue
                data += chunk
            except (OSError, asyncio.TimeoutError, asyncio.IncompleteReadError) as e:
                log.warning("Recv exception: %s. Reconnecting...", e)
                await self._reconnect()

        return data
