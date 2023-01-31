import asyncio
import toml

from os.path import exists
from threading import Thread
from time import time, strftime, gmtime
from typing import Literal
from random import randint, choice
from string import ascii_letters
from orjson import dumps, loads
from vkbottle import API, VKAPIError
from aiofiles import open as aiopen
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
		self.all_forms = {}
		if not exists('cache/forms.json'):
			with open('cache/forms.json', 'w', encoding='utf-8') as file:
				file.write('{}')
		loop = asyncio.new_event_loop()
		loop.run_until_complete(self._downoload_forms())
		
		if not exists('cache/orders.pyint'):
			with open('cache/orders.pyint', 'w', encoding='utf-8') as newFile:
				newFile.write('100')
		if not exists('cache/off.pylist'):
			with open('cache/off.pylist', 'w', encoding='utf-8') as newFile:
				newFile.write('[]')
		if not exists('cache/no_registred.pylist'):
			with open('cache/no_registred.pylist', 'w', encoding='utf-8') as newFile:
				newFile.write('[]')
		if not exists('cache/time_database.toml'):
			with open('cache/time_database.toml', 'w', encoding='utf-8') as newFile:
				newFile.write('[test]\n3=[]\n5=[]\nweek=[]\nmonth=[]\n')
		if not exists('cache/rates.txt'):
			with open('cache/rates.txt', 'w', encoding='utf-8') as newFile:
				newFile.write('') 

	async def _downoload_forms(self):
		async with aiopen('cache/forms.json', 'r', encoding='utf-8') as form_getter:
			forms = await form_getter.read()
		self.all_forms = loads(f'{forms}')

	async def _backup(self):
		async with aiopen('cache/forms.json', 'w', encoding='utf-8') as backup_file:
			await backup_file.write(f'{dumps(self.all_forms).decode()}')

	async def _get_key(self) -> str:
		key = ''
		for _ in range(randint(10, 100)):
			key += choice(ascii_letters)
		return key

	async def new_form(self, from_id:str) -> None:
		key = await self._get_key()
		self.all_forms[key] = {'from_id': from_id, 'driver_id': 0, 'active': True, 'in_drive': False, 'data': 0}
		thread = Thread(target=self._form_timer_starter, args=(key,))
		thread.start()
		return key

	async def start_drive(self, key:str, driver_id:int) -> None:
		try:
			self.all_forms[key]['active'] = False
			self.all_forms[key]['in_drive'] = True
			self.all_forms[key]['driver_id'] = driver_id
		except:
			pass
		await self._backup()

	async def stop_drive(self, key:str):
		try:
			self.all_forms[key]['active'] = False
			self.all_forms[key]['in_drive'] = False
		except:
			pass
		await self._backup()

	async def stop_form(self, key:str, data:dict, cancel:bool=False) -> None:
		if not cancel:
			await self.api.messages.send(
				user_id=self.all_forms[key]['from_id'],
				peer_id=self.all_forms[key]['from_id'],
				random_id=0,
				message='Не один водитель не принял твою заявку\nТы можешь повторить заказ снова!',
				keyboard=keyboards.repeat_order(self.all_forms[key]['data'])
			)
		try:
			self.all_forms[key]['active'] = False
		except:
			pass
		await self._backup()

	async def delete_all_form(self) -> None:
		for key in list(self.all_forms.keys()):
			if not self.all_forms[key]['active'] and not self.all_forms[key]['in_drive']:
				self.all_forms.remove(key)
		await self._backup()

	async def get(self, key:str) -> dict:
		await self._backup()
		return self.all_forms[key]

	def _form_timer_starter(self, *args) -> None:
		asyncio.run(self._form_timer(*args))

	async def _form_timer(self, key:str) -> None:
		form = self.all_forms[key]; counter = 0
		while (counter != ((10*60) // 15)) and (form['in_drive'] and not form['active']):
			await asyncio.sleep(15)
			await self.api.messages.send(
				user_id=form['from_id'],
				peer_id=form['from_id'],
				random_id=0,
				message='Идёт поиск водителя'
			)
			counter += 1
			if (form['in_drive'] and not form['active']):
				break
		if (form['in_drive'] and not form['active']):
			await self.stop_form(key)

	async def cache_cleaner(self) -> None:
		while True:
			await asyncio.sleep(24*60*60)
			await self._backup()
			await self._delete_all_form()

	def __del__(self):
		asyncio.run(self._backup())

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
							message='Привет!\n\
Ты давно не пользовался ботом,\n\
поэтому напоминаю, через нашего бота ты можешь вызвать такси, если ты пассажир. Или принять заявку, если ты водитель.\n\
Нажми на кнопку, чтобы начать.',
							keyboard=keyboards.month_no_activity
						)
				except VKAPIError:
					continue
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
		if f'{from_id}' not in old_database:
			old_database[f'{from_id}'] = {
				'3': [],
				'5': [],
				'week': [],
				'month': []
			}
		old_database[f'{from_id}']['3'].append(date)
		old_database[f'{from_id}']['5'].append(date)
		old_database[f'{from_id}']['week'].append(date)
		old_database[f'{from_id}']['month'].append(date)
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
		async with aiopen('cache/time_database.toml', 'w', encoding='utf-8') as file:
			await file.write(f'{toml.dumps(old_database)}')

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
		if f'{from_id}' not in db:
			db[f'{from_id}'] = {
				'3': [],
				'5': [],
				'week': [],
				'month': []
			}
			async with aiopen('cache/time_database.toml', 'w', encoding='utf-8') as file:
				await file.write(f'{toml.dumps(db)}')
		return db[f'{from_id}']

	async def _get_database(self) -> dict:
		async with aiopen('cache/time_database.toml', 'r', encoding='utf-8') as file:
			lines = await file.read()
		return toml.loads(f'{lines}')

	async def _check3(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1]['3']:
				if time() - date >= 3*24*60*60:
					database[id[0]]['3'].remove(date)
		async with aiopen('cache/time_database.toml', 'w', encoding='utf-8') as file:
			await file.write(f'{toml.dumps(database)}')
		await asyncio.sleep(24*60*60)

	async def _check5(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1]['5']:
				if len(database[id]['5']) > 100 and (await self.database.driver.exists(int(id))):
					await self.api.messages.send(
						user_id=int(id),
						peer_id=int(id),
						random_id=0,
						message='Ты сделал(а) уже более 100 поездок за 5 днейn\n\
Теперь ты учавствуешь в розыгрыше 100 руб. на баланс!'
					)
				if time() - date >= 5*24*60*60:
					database[id[0]]['5'].remove(date)
		async with aiopen('cache/time_database.toml', 'w', encoding='utf-8') as file:
			await file.write(f'{toml.dumps(database)}')
		await asyncio.sleep((24*60*60) + 10)

	async def _check_week(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1]['week']:
				if (time() - date >= 7*24*60*60) and (strftime('%A', gmtime()).lower() == 'sunday'):
					database[id[0]]['week'].remove(date)
		async with aiopen('cache/time_database.toml', 'w', encoding='utf-8') as file:
			await file.write(f'{toml.dumps(database)}')
		await asyncio.sleep((24*60*60) + 20)

	async def _check_month(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1]['month']:
				if time() - date >= 30*24*60*60:
					database[id[0]]['month'].remove(date)
		async with aiopen('cache/time_database.toml', 'w', encoding='utf-8') as file:
			await file.write(f'{toml.dumps(database)}')
		await asyncio.sleep((24*60*60) + 30)

	async def debug_spec_checker(self):
		database = await self._get_database()
		for id in list(database.items()):
			for date in id[1]['3']:
				if time() - date >= 3*24*60*60:
					database[id[0]]['3'].remove(date)
			for date in id[1][5]:
				if len(database[id]['5']) > 100 and (await self.database.driver.exists(int(id))):
					await self.api.messages.send(
						user_id=int(id),
						peer_id=int(id),
						random_id=0,
						message='Ты сделал(а) уже более 100 поездок за 5 днейn\n\
Теперь ты учавствуешь в розыгрыше 100 руб. на баланс!'
					)
				if time() - date >= 5*24*60*60:
					database[id[0]]['5'].remove(date)
			for date in id[1]['week']:
				if (len(database[id]['week']) > 5)
				if (time() - date >= 7*24*60*60):
					database[id[0]]['week'].remove(date)
			for date in id[1]['month']:
				if time() - date >= 30*24*60*60:
					database[id[0]]['month'].remove(date)
		async with aiopen('cache/time_database.toml', 'w', encoding='utf-8') as file:
			await file.write(f'{toml.dumps(database)}')

	async def get_rate(self) -> str:
		async with aiopen('cache/rates.txt', 'r', encoding='utf-8') as rate:
			return await rate.read()

	async def set_rate_file(self, text:str='') -> None:
		async with aiopen('cache/rates.txt', 'w', encoding='utf-8') as rate:
			await rate.write(f'{text}')