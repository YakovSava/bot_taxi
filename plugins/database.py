import sqlite3

from os.path import join
from time import time

class Database:

	def __init__(self):
		self.passanger = self._passanger()
		self.passanger._create_table()
		self.driver = self._driver()
		self.driver._create_table()

	class _passanger:

		def __init__(self): 
			self.db = sqlite3.connect(join('cache', 'passangers.db'), check_same_thread=False)
			self.db.row_factory = sqlite3.Row
			self.cursor = self.db.cursor()

		def _create_table(self):
			self.cursor.execute('''CREATE TABLE if not exists passanger (
				VK text,
				gender text,
				city text,
				name text,
				phone text,
				quantity integer
		)''')
			self.db.commit()

		async def exists(self, vk:int) -> bool:
			what = await self.get(vk)
			if what is not None:
				return True
			else:
				return False

		async def get(self, vk:str) -> dict:
			self.cursor.execute(f"SELECT * FROM passanger WHERE VK = '{vk}'")
			return self.cursor.fetchone()

		async def delete_before_phone(self, phone:str) -> None:
			self.cursor.execute(f'DELETE FROM passanger WHERE phone = "{phone}"')
			self.db.commit()

		def get_before_phone(self, phone:str) -> bool:
			self.cursor.execute(f'SELECT VK FROM passanger WHERE phone = "{phone}"')
			if self.cursor.fetchone() is not None:
				return True
			else:
				return False

		async def reg(self, json:dict) -> None:
			self.cursor.execute('INSERT INTO passanger VALUES (?, ?, ?, ?, ?, ?)', (
				json['vk'], json['gender'],
				json['city'], json['name'],
				json['phone'], 0
			))
			self.db.commit()

		async def delete(self, vk:int) -> None:
			self.cursor.execute(f"DELETE FROM passanger WHERE VK = '{vk}'")
			self.db.commit()

		async def set_qunatity(self, vk:str):
			self.cursor.execute(f'SELECT quantity FROM passanger WHERE VK = "{vk}"')
			last = int(self.cursor.fetchone()['quantity'])
			self.cursor.execute(f'UPDATE passanger SET quantity = {last + 1} WHERE VK = "{vk}"')
			self.db.commit()

		async def admin_get_all(self):
			self.cursor.execute('SELECT * FROM passanger')
			for info in (self.cursor.fetchall()):
				if info is not None: 
					yield info


	class _driver:

		def __init__(self):
			self.db = sqlite3.connect(join('cache', 'drivers.db'), check_same_thread=False)
			self.db.row_factory = sqlite3.Row
			self.cursor = self.db.cursor()

		async def exists(self, vk:int) -> bool:
			what = await self.get(vk)
			if what != [None, None]:
				return True
			else:
				return False

		def _create_table(self):
			self.cursor.execute('''CREATE TABLE if not exists driver (
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
			self.cursor.execute('''CREATE TABLE if not exists driver2 (
				VK text,
				last_activity text,
				quantity integer,
				balance bigint
	)''')
			self.db.commit()

		async def get(self, VK:str) -> dict:
			self.cursor.execute(f'SELECT * FROM driver WHERE VK = "{VK}"')
			first_table = self.cursor.fetchone()
			self.cursor.execute(f'SELECT * FROM driver2 WHERE VK = "{VK}"')
			second_table = self.cursor.fetchone()
			return [first_table, second_table]

		async def reg(self, json:dict) -> None:
			self.cursor.execute('INSERT INTO driver VALUES (?,?,?,?,?,?,?,?,?,?)', (
				json['vk'], 1, json['gender'],
				json['city'], json['name'], json['phone'],
				json['auto'], json['color'], json['state_number'],
				time()
			))
			self.db.commit()
			self.cursor.execute('INSERT INTO driver2 VALUES (?,?,?,?)', (
				json['vk'], time(), 0, json['balance']
			))
			self.db.commit()

		async def set_activity(self, vk:str) -> None:
			self.cursor.execute(f'UPDATE driver2 SET last_activity = "{time()}" WHERE VK = "{vk}"')
			self.db.commit()

		async def set_balance(self, vk:str, set:int) -> None:
			self.cursor.execute(f'SELECT balance FROM driver2 WHERE VK = "{vk}"')
			last = int(self.cursor.fetchone()['balance'])
			self.cursor.execute(f'UPDATE driver2 SET balance = {last + set} WHERE VK = "{vk}"')
			self.db.commit()

		async def set_qunatity(self, vk:str):
			self.cursor.execute(f"SELECT quantity FROM driver2 WHERE VK = '{vk}'")
			last = int(self.cursor.fetchone()['quantity'])
			self.cursor.execute(f"UPDATE driver2 SET quantity = {last + 1} WHERE VK = '{vk}'")
			self.db.commit()

		async def get_all(self) -> tuple:
			self.cursor.execute('SELECT * FROM driver')
			for info in (self.cursor.fetchall()):
				if info is not None:
					yield info['VK'], info['city']

		async def delete(self, vk:int) -> None:
			self.cursor.execute(f'DELETE FROM driver WHERE VK = "{vk}"')
			self.cursor.execute(f'DELETE FROM driver2 WHERE VK = "{vk}"')
			self.db.commit()

		async def admin_get_all(self):
			self.cursor.execute('SELECT * FROM driver')
			all1 = self.cursor.fetchall()
			self.cursor.execute('SELECT * FROM driver2')
			return [all1, self.cursor.fetchall()]

		async def get_all_inform(self):
			self.cursor.execute('SELECT * FROM driver2')
			for info in (self.cursor.fetchall()):
				if info is not None:
					yield info