import asyncio

from os.path import exists
from shutil import copy
from aiofiles import open as aiopen
from aiosqlite import Row, connect
from plugins.binder import Binder

class Manager:

    def __init__(self,
            loop:asyncio.AbstractEventLoop=asyncio.get_event_loop(),
            binders:list[Binder]=None
        ):
        if binders is None:
            raise Exception
        self.parameters = binders
        self._loop = loop

    async def _check_table(self) -> None:
        if exists('table.toml'):
            async with aiopen('table.toml', 'w', encoding='utf-8') as file:
                await file.write('')

    async def _backup(self) -> None:
        copy('cache/drivers.db', '.')
        copy('cache/passangers.db', '.')

    async def _get_stat(self) -> list[list[dict]]:
        await self.backup()
        connection = await connect('drivers.db')
        connection.row_factory = Row
        cursor = await connection.cursor()

        await cursor.execute('SELECT * FROM driver')
        drivers = await cursor.fetchall()
        await cursor.execute('SELECT * FROM driver2')
        drivers2 = await cursor.fetchall()

        unifed_driver = [{
            'VK': driver['VK'],
            'status': driver['status'],
            'gender': driver['gender'],
            'city': driver['city'],
            'name': driver['name'],
            'phone': driver['phone'],
            'auto': driver['auto'],
            'color': driver['color'],
            'state_number': driver['state_number'],
            'first_activity': driver['first_activity'],
            'last_activity': driver2['last_activity'],
            'quantity': driver2['quantity'],
            'balance': driver2['balance']
        } for driver, driver2 in zip(drivers, drivers2)]
        await cursor.close()
        await connection.close()

        connection = await connect('drivers.db')
        connection.row_factory = Row
        cursor = await connection.cursor()

        await cursor.execute('SELECT * FROM passanger')
        passangers = await cursor.fetchall()

        unifed_passangers = [{
            'VK': passanger['VK'],
            'gender': passanger['gender'],
            'city': passanger['city'],
            'name': passanger['name'],
            'phone': passanger['phone'],
            'quantity': passanger['quantity'],
            'balance': passanger['balance']
        } for passanger in passangers]

        return [unifed_driver, unifed_passangers]

    async def sync_database(self) -> None:
        pass