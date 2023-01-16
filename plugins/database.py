import asyncio
import aiosqlite

from os.path import join
from time import time

class Database:

	def __init__(self):
		self.passanger = self._passanger()
		asyncio.run(self.passanger._create_table())
		self.driver = self._driver()
		asyncio.run(self.driver._create_table())

	class _passanger:

		def __init__(self):
			asyncio.run(self._initialize())

		async def _initialize(self):
			self.db = await aiosqlite.connect(join('cache', 'passangers.db'), check_same_thread=False)
			self.db.row_factory = aiosqlite.Row
			self.cursor = await self.db.cursor()

		async def _create_table(self):
			await self.cursor.execute('''CREATE TABLE if not exists passanger (
				VK text,
				gender text,
				city text,
				name text,
				phone text,
				quantity integer
		)''')
			await self.db.commit()

		async def exists(self, vk:int) -> bool:
			return (await self.get(vk)) is not None

		async def get(self, vk:str) -> dict:
			await self.cursor.execute(f"SELECT * FROM passanger WHERE VK = '{vk}'")
			return await self.cursor.fetchone()

		async def delete_before_phone(self, phone:str) -> None:
			await self.cursor.execute(f'DELETE FROM passanger WHERE phone = "{phone}"')
			await self.db.commit()

		# def get_before_phone(self, phone:str) -> bool:
		# 	await self.cursor.execute(f'SELECT VK FROM passanger WHERE phone = "{phone}"')
		# 	if (await self.cursor.fetchone()) is not None:
		# 		return True
		# 	else:
		# 		return False

		async def reg(self, json:dict) -> None:
			await self.cursor.execute('INSERT INTO passanger VALUES (?, ?, ?, ?, ?, ?)', (
				json['vk'], json['gender'],
				json['city'], json['name'],
				json['phone'], 0
			))
			await self.db.commit()

		async def delete(self, vk:int) -> None:
			await self.cursor.execute(f"DELETE FROM passanger WHERE VK = '{vk}'")
			await self.db.commit()

		async def set_qunatity(self, vk:str):
			await self.cursor.execute(f'SELECT quantity FROM passanger WHERE VK = "{vk}"')
			last = int((await self.cursor.fetchone())['quantity'])
			await self.cursor.execute(f'UPDATE passanger SET quantity = {last + 1} WHERE VK = "{vk}"')
			await self.db.commit()

		async def admin_get_all(self):
			await self.cursor.execute('SELECT * FROM passanger')
			for info in (await self.cursor.fetchall()):
				if info is not None: 
					yield info


	class _driver:

		def __init__(self):
			asyncio.run(self._initialize())

		async def _initialize(self):
			self.db = await aiosqlite.connect(join('cache', 'drivers.db'), check_same_thread=False)
			self.db.row_factory = aiosqlite.Row
			self.cursor = await self.db.cursor()

		async def exists(self, vk:int) -> bool:
			return (await self.get(vk)) != [None, None]

		async def _create_table(self):
			await self.cursor.execute('''CREATE TABLE if not exists driver (
				VK text,
				status integer,
				gender text,
				city text,
				name text,
				phone text,
				auto text,
				color text,
				state_number text,
				first_activity text
	)''')
			await self.cursor.execute('''CREATE TABLE if not exists driver2 (
				VK text,
				last_activity text,
				quantity integer,
				balance bigint
	)''')
			await self.db.commit()

		async def get(self, VK:str) -> dict:
			await self.cursor.execute(f'SELECT * FROM driver WHERE VK = "{VK}"')
			first_table = await self.cursor.fetchone()
			await self.cursor.execute(f'SELECT * FROM driver2 WHERE VK = "{VK}"')
			second_table = await self.cursor.fetchone()
			return [first_table, second_table]

		async def reg(self, json:dict) -> None:
			await self.cursor.execute('INSERT INTO driver VALUES (?,?,?,?,?,?,?,?,?,?)', (
				json['vk'], 1, json['gender'],
				json['city'], json['name'], json['phone'],
				json['auto'], json['color'], json['state_number'],
				time()
			))
			await self.db.commit()
			await self.cursor.execute('INSERT INTO driver2 VALUES (?,?,?,?)', (
				json['vk'], time(), 0, json['balance']
			))
			await self.db.commit()

		async def set_activity(self, vk:str) -> None:
			await self.cursor.execute(f'UPDATE driver2 SET last_activity = "{time()}" WHERE VK = "{vk}"')
			await self.db.commit()

		async def set_balance(self, vk:str, set:int) -> None:
			await self.cursor.execute(f'SELECT balance FROM driver2 WHERE VK = "{vk}"')
			last = int((await self.cursor.fetchone())['balance'])
			await self.cursor.execute(f'UPDATE driver2 SET balance = {last + set} WHERE VK = "{vk}"')
			await self.db.commit()

		async def set_qunatity(self, vk:str):
			await self.cursor.execute(f"SELECT quantity FROM driver2 WHERE VK = '{vk}'")
			last = int((await self.cursor.fetchone())['quantity'])
			await self.cursor.execute(f"UPDATE driver2 SET quantity = {last + 1} WHERE VK = '{vk}'")
			await self.db.commit()

		async def get_all(self) -> tuple:
			await self.cursor.execute('SELECT * FROM driver')
			for info in (await self.cursor.fetchall()):
				if info is not None:
					yield info['VK'], info['city']

		async def delete(self, vk:int) -> None:
			await self.cursor.execute(f'DELETE FROM driver WHERE VK = "{vk}"')
			await self.cursor.execute(f'DELETE FROM driver2 WHERE VK = "{vk}"')
			await self.db.commit()

		async def admin_get_all(self):
			await self.cursor.execute('SELECT * FROM driver')
			all1 = await self.cursor.fetchall()
			await self.cursor.execute('SELECT * FROM driver2')
			return list(zip(all1, await self.cursor.fetchall()))

		async def get_all_inform(self):
			await self.cursor.execute('SELECT * FROM driver2')
			for info in (await self.cursor.fetchall()):
				if info is not None:
					yield info