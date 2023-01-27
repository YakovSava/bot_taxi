import asyncio
import orjson

from time import time, strftime, gmtime
from os.path import exists
from typing import Literal
from aiofiles import open as aiopen
from vkbottle import API
from plugins.database import Database # For annotation
from plugins.timer import Timer # For annotation
from plugins.keyboards import keyboards

class Dispatch:

	class DispatchNotGetOneParameterError(SystemError): pass

	def __init__(self,
		timer:Timer=None,
		database:Database=None,
		api:API=None
	):
		if (timer is None) or (database is None) and (api is None):
			raise self.DispatchNotGetOneParameterError(f'The dispatcher did not receive one of the items (something from the following list is "None", however it should not be "None"): \n\
{timer = }\n{database = }\n{api = }')
		self.timer = timer
		self.database = database
		self.api = api
		
		if not exists('cache/orders.pyint'):
			with open('cache/orders.pyint', 'w', encoding='utf-8') as newFile:
				newFile.write('100')
		if not exists('cache/off.pylist'):
			with open('cache/off.pylist', 'w', encoding='utf-8') as newFile:
				newFile.write('[]')
		if not exists('cache/no_registred.pylist'):
			with open('cache/no_registred.pylist', 'w', encoding='utf-8') as newFile:
				newFile.write('[]')
		if not exists('cache/time_database.json'):
			with open('cache/time_database.json', 'w', encoding='utf-8') as newFile:
				newFile.write('{}')

	async def checker(self) -> None:
		# await asyncio.sleep(20) # Debug mode
		while True:
			service_file = await self.get_service_file()
			all_chats = await self.api.messages.get_conversations(
				offset=0,
				count=200
			)
			for chat in all_chats.items:
				try:
					if (chat.last_message.peer_id not in service_file) and ((time() - chat.last_message.date) >= 30*24*60*60):
						await self.api.messages.send(
							user_id=chat.last_message.peer_id,
							peer_id=chat.last_message.peer_id,
							random_id=0,
							message='Привет!\nТы целый месяц не пользовался нашим ботом &#128532;\nНажми на кнопку что бы снова начать',
							keyboard=keyboards.month_no_activity
						)
				except Exception as err:
					print(err)
					continue
			await asyncio.sleep(24*60*60)

	async def get_order_names(self) -> int:
		async with aiopen('cache/orders.pyint', 'r', encoding='utf-8') as file:
			line = await file.readline()
		return int(line)

	async def set_order_names(self) -> None:
		so = await self.get_order_names()
		async with aiopen('cache/orders.pyint', 'r', encoding='utf-8') as file:
			await file.write(f'{so + 1}')

	async def run_order_setter(self):
		while True:
			async with aiopen('cache/orders.pyint', 'r', encoding='utf-8') as file:
				await file.write('100')
			await asyncio.sleep(24*60*60)

	async def get_service_file(self) -> list:
		async with aiopen('cache/off.pylist', 'r', encoding='utf-8') as list_file:
			lines = await list_file.read()
		return eval(f'{lines}')

	async def off_account(self, new_id:int) -> None:
		old_list = await self.get_service_file()
		if new_id not in old_list:
			async with aiopen('cache/off.pylist', 'w', encoding='utf-8') as list_file:
				old_list.append(new_id)
				await list_file.write(f'{old_list}')

	async def on_account(self, off_id:int) -> None:
		old_list = await self.get_service_file()
		while off_id in old_list:
			old_list.remove(off_id)
		async with aiopen('cache/off.pylist', 'w', encoding='utf-8') as list_file:
			await list_file.write(f'{old_list}')

	async def get_no_registred_drivers(self) -> list:
		async with aiopen('cache/no_registred.pylist', 'r', encoding='utf-8') as file:
			list_lines = await file.read()
		return eval(list_lines)

	async def remove_no_registred_drivers(self, registred_id:int) -> None:
		old_list = await self.get_no_registred_drivers()
		while registred_id in old_list:
			old_list.remove(registred_id)
		async with aiopen('cache/no_registred.pylist', 'w', encoding='utf-8') as file:
			await file.write(f'{old_list}')

	async def update_no_registred_driver(self, new_id:int) -> None:
		list_lines = await self.get_no_registred_drivers()
		if new_id not in list_lines:
			async with aiopen('cache/no_registred.pylist', 'w', encoding='utf-8') as file:
				list_lines.append(new_id)
				await file.write(f'{list_lines}')

	async def check_registred(self, from_id:int) -> bool:
		list_lines = await self.get_no_registred_drivers()
		return from_id in list_lines
		
	async def add_and_update_drive(self, date:Literal[int, float]=None, from_id:int=None):
		if (await self.database.driver.exists(from_id)):
			await self.database.driver.set_qunatity(from_id)
		else:
			await self.database.passanger.set_qunatity(from_id)
		old_database = await self._get_database()
		if int(from_id) not in old_database:
			old_database[int(from_id)] = {
				3: [],
				5: [],
				'week': [],
				'month': []
			}
		old_database[int(from_id)][3].append(date)
		old_database[int(from_id)][5].append(date)
		old_database[int(from_id)]['week'].append(date)
		old_database[int(from_id)]['month'].append(date)
		'''
	Structure of database
{
	id: {
		3: [],
		5: [],
		'week': [],
		'month': []
	}
}
	Trips for all time are stored in the main database
		'''
		async with aiopen('cache/time_database.json', 'w', encoding='utf-8') as file:
			await file.write(f'{orjson.dumps(old_database).decode()}')

	async def date_checker(self):
		while True:
			await asyncio.gather(
				asyncio.create_task(self._check3()),
				asyncio.create_task(self._check5()),
				asyncio.create_task(self._check_week()),
				asyncio.create_task(self._check_monnth())
			)

	async def get_time_database(self, from_id:int) -> dict:
		db = await self._get_database()
		if from_id not in db:
			db[from_id] = {
				3: [],
				5: [],
				'week': [],
				'month': []
			}
			async with aiopen('cache/time_database.json', 'w', encoding='utf-8') as file:
				await file.write(f'{db}')
		return db[from_id]

	async def _get_database(self) -> dict:
		async with aiopen('cache/time_database.json', 'r', encoding='utf-8') as file:
			lines = await file.read()
		return orjson.loads(f'{lines}')

	async def _check3(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1][3]:
				if time() - date >= 3*24*60*60:
					database[id[0]][3].remove(date)
		async with aiopen('cache/time_database.json', 'w', encoding='utf-8') as file:
			await file.write(f'{orjson.dumps(database).decode()}')
		await asyncio.sleep(24*60*60)

	async def _check5(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1][5]:
				if time() - date >= 5*24*60*60:
					database[id[0]][5].remove(date)
		async with aiopen('cache/time_database.json', 'w', encoding='utf-8') as file:
			await file.write(f'{orjson.dumps(database).decode()}')
		await asyncio.sleep((24*60*60) + 10)

	async def _check_week(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1]['week']:
				if (time() - date >= 7*24*60*60) and (strftime('%A', gmtime()).lower() == 'sunday'):
					database[id[0]]['week'].remove(date)
		async with aiopen('cache/time_database.json', 'w', encoding='utf-8') as file:
			await file.write(f'{orjson.dumps(database).decode()}')
		await asyncio.sleep((24*60*60) + 20)

	async def _check_month(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1]['month']:
				if time() - date >= 30*24*60*60:
					database[id[0]]['month'].remove(date)
		async with aiopen('cache/time_database.json', 'w', encoding='utf-8') as file:
			await file.write(f'{orjson.dumps(database).decode()}')
		await asyncio.sleep((24*60*60) + 30)

	async def debug_spec_checker(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1][3]:
				if time() - date >= 3*24*60*60:
					database[id[0]][3].remove(date)
			for date in id[1][5]:
				if time() - date >= 5*24*60*60:
					database[id[0]][5].remove(date)
			for date in id[1]['week']:
				if (time() - date >= 7*24*60*60):
					database[id[0]]['week'].remove(date)
			for date in id[1]['month']:
				if time() - date >= 30*24*60*60:
					database[id[0]]['month'].remove(date)
		async with aiopen('cache/time_database.json', 'w', encoding='utf-8') as file:
			await file.write(f'{orjson.dumps(database).decode()}')