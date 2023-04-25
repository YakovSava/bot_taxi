import asyncio

from shutil import copy
from aiosqlite import Row, connect

class Manager:

    def __init__(self,
            loop:asyncio.AbstractEventLoop=asyncio.get_event_loop(),

        ):