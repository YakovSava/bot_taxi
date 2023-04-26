import asyncio

from rtoml import loads
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

    async def _form_csv(self, data:list[list[dict]]) -> str:
        global_parameters = await self._get_global_parameters()
        text = 'город;количество водителей;количество пассажиров;кнопки;общий баланс водителей;общий баланс пассажиров;стоимость поездки;ссылка на расценку\n'
        lambda_filter = lambda u: len(filter(lambda x: x.lower() == city.lower(), u))
        lambda_balance = lambda u: sum(map(lambda x: x['balance'], u))
        for city, button, amount, link, token in global_parameters['citys']:
            text += f'{city};{lambda_filter(data[0])};{lambda_filter(data[1])};{button};{lambda_balance(data[0])};{lambda_balance(data[1])};{amount};{link}\n'
        return text

    async def _get_global_parameters(self) -> dict:
        async with aiopen('global_parameters.toml', 'r', encoding='utf-8') as file:
            return loads(await file.read())

    async def _check_once(self) -> None:
        async with aiopen('table.csv', 'w', encoding='utf-8') as csv:
            await csv.write(
                await self._form_csv(
                    await self._get_stat()
                )
            )
        await self._backup()

    async def sync_database(self) -> None:
        while True:
            await self._check_once()
            await asyncio.sleep(24*60*60)