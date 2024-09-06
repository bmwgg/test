import asyncio
import signal
from time import sleep

READ_TIMEOUT = 60
BUFFER_SIZE = 4096


class BaseHandler:
    def __init__(self, loop, reader, writer):
        self.loop = loop
        self.writer = writer
        self.reader = reader

    async def run(self):
        pass


class BaseServer:
    """Echo server class"""

    _server: asyncio.Server
    _handler_type = BaseHandler
    _handler: BaseHandler

    def __init__(self, host, port, loop=None, limit=256):
        self._loop = loop or asyncio.get_event_loop()
        self._coro = asyncio.start_server(self.handle_connection, host=host, port=port, limit=limit)

    def start(self):
        self._server = self._loop.run_until_complete(self._coro)

    def stop(self):
        self._server.close()

    def wait_closed(self):
        return self._server.wait_closed()

    async def handle_connection(self, reader, writer):
        self._handler = self._handler_type(self._loop, reader, writer)
        await self._handler.run()


class BinaryServerHandler(BaseHandler):
    async def run(self):
        try:
            while True:
                try:
                    data = await asyncio.wait_for(self.reader.read(BUFFER_SIZE), timeout=READ_TIMEOUT)
                except asyncio.TimeoutError as e:
                    break
                else:

                    # ****************************
                    print(data, data.hex())
                    self.writer.write(data)
                    # ****************************

                    await self.writer.drain()
                    continue
        except ConnectionResetError as e:
            pass
        finally:
            self.writer.close()


class BinaryServer(BaseServer):
    _handler_type = BinaryServerHandler
    _handler: BinaryServerHandler


loop = asyncio.get_event_loop()
binary_server = BinaryServer('0.0.0.0', 8888, loop, 256)
binary_server.start()

try:
    loop.run_forever()
except (KeyboardInterrupt, OSError):
    binary_server.stop()
