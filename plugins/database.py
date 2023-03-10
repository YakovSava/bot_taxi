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
				VK TEXT,
				gender TEXT,
				city TEXT,
				name TEXT,
				phone TEXT,
				quantity INTEGER,
				balance INTEGER
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
			await self.cursor.execute('INSERT INTO passanger VALUES (?, ?, ?, ?, ?, ?, ?)', (
				json['vk'], json['gender'],
				json['city'], json['name'],
				json['phone'], 0, 0
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

		async def set_balance(self, vk:str, set:int) -> None:
			await self.cursor.execute(f'SELECT * FROM passanger WHERE VK = "{vk}"')
			rec = await self.cursor.fetchone()
			if rec is not None:
				last = int(rec['balance'])
			else:
				last = 0
			await self.cursor.execute(f'UPDATE passanger SET balance = "{last + set}" WHERE VK = "{vk}"')
			await self.db.commit()


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
				VK TEXT,
				status INTEGER,
				gender TEXT,
				city TEXT,
				name TEXT,
				phone TEXT,
				auto TEXT,
				color TEXT,
				state_number TEXT,
				first_activity TEXT
	)''')
			await self.cursor.execute('''CREATE TABLE if not exists driver2 (
				VK TEXT,
				last_activity TEXT,
				quantity INTEGER,
				balance BIGINT
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
			await self.cursor.execute(f'SELECT * FROM driver2 WHERE VK = "{vk}"')
			rec = await self.cursor.fetchone()
			if rec is not None:
				last = int(rec['balance'])
			else:
				last = 0
			await self.cursor.execute(f'UPDATE driver2 SET balance = "{last + set}" WHERE VK = "{vk}"')
			await self.db.commit()

		async def set_qunatity(self, vk:str):
			await self.cursor.execute(f"SELECT quantity FROM driver2 WHERE VK = '{vk}'")
			last = int((await self.cursor.fetchone())['quantity'])
			await self.cursor.execute(f"UPDATE driver2 SET quantity = {last + 1} WHERE VK = '{vk}'")
			await self.db.commit()

		async def get_all(self) -> aiosqlite.Row:
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
			all_data1 = [
				{
					'VK': record['VK'],
					'status': record['status'],
					'gender': record['gender'],
					'city': record['city'],
					'name': record['name'],
					'phone': record['phone'],
					'auto': record['auto'],
					'color': record['color'],
					'state_number': record['state_number'],
					'first_activity': record['first_activity']
				}
				for record in (await self.cursor.fetchall())
			]
			await self.cursor.execute('SELECT * FROM driver2')
			all_data2 = [
				{
					'last_activity': record['last_activity'],
					'quantity': record['quantity'],
					'balance': record['balance']
				}
				for record in (await self.cursor.fetchall())
			]
			return list(
				map(
					lambda x: dict(list(x[0].items()) + list(x[1].items())),
					zip(all_data1, all_data2)
				)
			)

		async def get_all_inform(self):
			await self.cursor.execute('SELECT * FROM driver')
			one = await self.cursor.fetchall()
			await self.cursor.execute('SELECT * FROM driver2')
			one.extend(await self.cursor.fetchall())
			for info in one:
				if info is not None:
					yield info