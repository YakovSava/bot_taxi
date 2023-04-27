import asyncio
import rtoml as tomli

from os.path import exists
from time import time, strftime, gmtime
from typing import Literal
from random import randint, choice
from string import ascii_uppercase, ascii_letters
from vkbottle import API, VKAPIError
from aiofiles import open as aiopen
from plugins.database import Database # For annotation
from plugins.timer import Timer # For annotation
# from plugins.downoloader import DownoloadC # For annotation
from plugins.keyboards import keyboards

class Dispatch:

	class DispatchNotGetOneParameterError(SystemError): pass

	def __init__(self,
		timer:Timer=None,
		database:Database=None,
		api:API=None,
		# CGetter:DownoloadC=None
	):
		if (timer is None) and (database is None) and (api is None) and (CGetter is None):
			raise self.DispatchNotGetOneParameterError(f'The dispatcher did not receive one of the items (something from the following list is "None", however it should not be "None"): \n\
{timer = }\n{database = }\n{api = }')
		self.timer = timer
		self.database = database
		self.api = api
		# self.downoload = CGetter
		self.all_forms = {}
		if not exists('cache/forms.json'):
			with open('cache/forms.json', 'w', encoding='utf-8') as file:
				file.write('{}')
		self.loop = asyncio.new_event_loop()
		self.loop.run_until_complete(self._downoload_forms())
		
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
		if not exists('cache/promo.pylist'):
			with open('cache/promo.pylist', 'w', encoding='utf-8') as newFile:
				newFile.write('[]')
		if not exists('cache/aipu.pylist'):
			with open('cache/aipu.pylist', 'w', encoding='utf-8') as newFile:
				newFile.write('[]')

	def _validate_toml(self, toml_lines:list=['[block]', 'variable = "data"']) -> bool:
		try: tomli.loads("\n".join(toml_lines))
		except: return False
		else: return True

	async def _cutter(self, toml_lines:str='''[block]\nvariable = "data"''') -> str:
		toml_split = toml_lines.split('\n') #; toml_cplit_copy = toml_split.copy()
		toml_result = ''
		for cut_index in range(len(toml_split)):
			if self._validate_toml(toml_split[:cut_index]):
				toml_result += f'{toml_split[cut_index]}\n'
		return toml_result

	async def _toml_protector(self) -> str:
		async with aiopen('cache/time_database.toml', 'r', encoding='utf-8') as file:
			lines = await self._cutter(await file.read())
		async with aiopen('cache/time_database.toml', 'w', encoding='utf-8') as file:
			await file.write(lines)
		return lines

	async def _downoload_forms(self):
		async with aiopen('cache/forms.json', 'r', encoding='utf-8') as form_getter:
			forms = await form_getter.readline()
		self.all_forms = eval(f'{forms}')

	async def _backup(self):
		async with aiopen('cache/forms.json', 'w', encoding='utf-8') as backup_file:
			await backup_file.write(f'{self.all_forms}')

	async def _get_key(self) -> str:
		key = ''
		for _ in range(randint(10, 100)):
			key += choice(ascii_letters)
		return key

	async def _read(self, filename:str) -> str:
		# return self.downoload.read(join(getcwd(), filename))[1:]
		async with aiopen(filename, 'r', encoding='utf-8') as file:
			return await file.read()

	async def _write(self, filename:str, all_lines:str) -> None:
		# return self.downoload.write(join(getcwd(), filename), all_lines)
		async with aiopen(filename, 'w', encoding='utf-8') as file:
			await file.write(all_lines)

	async def new_form(self, from_id:str) -> None:
		key = await self._get_key()
		self.all_forms[key] = {'from_id': from_id, 'driver_id': 0, 'active': True, 'in_drive': False, 'data': 0}
		asyncio.run_coroutine_threadsafe(self._form_timer(key), self.loop)
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

	async def stop_form(self, key:str, cancel:bool=False) -> None:
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

	async def _form_timer(self, key:str) -> None:
		form = self.all_forms[key]; counter = 0
		# print(form['in_drive'], form['active']); print(counter, ((10*60) // 15)); print(counter != ((10*60) // 15))
		while (counter != ((10*60) // 15)) and (not form['in_drive'] and form['active']):
			await asyncio.sleep(15)
			await self.api.messages.send(
				user_id=form['from_id'],
				peer_id=form['from_id'],
				random_id=0,
				message='Идёт поиск водителя'
			)
			counter += 1
			if (form['in_drive']) and (form['active']):
				break
		if (not form['in_drive'] and form['active']):
			await self.stop_form(key)

	async def cache_cleaner(self) -> None:
		while True:
			await asyncio.sleep(24*60*60)
			await self._backup()
			await self._delete_all_form()

	def __del__(self):
		asyncio.run(self._backup())

	async def checker(self) -> None:
		await asyncio.sleep(20)
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
		lines = await self._read('cache/off.pylist')
		return eval(f'{lines}')

	async def off_account(self, new_id:int) -> None:
		old_list = await self.get_service_file()
		if new_id not in old_list:
			old_list.append(new_id)
			await self._write('cache/off.pylist', f'{old_list}')
				
	async def on_account(self, off_id:int) -> None:
		old_list = await self.get_service_file()
		while off_id in old_list:
			old_list.remove(off_id)
		await self._write('cache/off.pylist', f'{old_list}')

	async def get_no_registred_drivers(self) -> list:
		list_lines = await self._read('cache/no_registred.pylist')
		return eval(list_lines)

	async def remove_no_registred_drivers(self, registred_id:int) -> None:
		old_list = await self.get_no_registred_drivers()
		while registred_id in old_list:
			old_list.remove(registred_id)
		await self._write('cache/no_registred.pylist', f'{old_list}')

	async def update_no_registred_driver(self, new_id:int) -> None:
		list_lines = await self.get_no_registred_drivers()
		if new_id not in list_lines:
			list_lines.append(new_id)
			await self._write('cache/no_registred.pylist', f'{list_lines}')

	async def check_registred(self, from_id:int) -> bool:
		list_lines = await self.get_no_registred_drivers()
		return from_id in list_lines
		
	async def add_and_update_drive(self, date:Literal[int, float]=None, from_id:int=None):
		if (await self.database.driver.exists(from_id)):
			await self.database.driver.set_qunatity(from_id)
		else:
			await self.database.passanger.set_qunatity(from_id)
		old_database = await self.get_database_of_times()
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
		await self._write('cache/time_database.toml', f'{tomli.dumps(old_database)}')

	async def date_checker(self):
		while True:
			await asyncio.gather(
				asyncio.create_task(self._check3()),
				asyncio.create_task(self._check5()),
				asyncio.create_task(self._check_week()),
				asyncio.create_task(self._check_month())
			)

	async def get_time_database(self, from_id:int) -> dict:
		db = await self.get_database_of_times()
		if f'{from_id}' not in db:
			db[f'{from_id}'] = {
				'3': [],
				'5': [],
				'week': [],
				'month': []
			}
			await self._write('cache/time_database.toml', f'{tomli.dumps(db)}')
		return db[f'{from_id}']

	async def get_database_of_times(self) -> dict:
		lines = await self._read('cache/time_database.toml')
		try: return tomli.loads(f'{lines}')
		except: return tomli.loads(await self._toml_protector())

	async def _check3(self):
		database = await self.get_database_of_times()
		for id in list(database.items()):
			for date in id[1]['3']:
				if time() - date >= 3*24*60*60:
					database[id[0]]['3'].remove(date)
		await self._write('cache/time_database.toml', f'{tomli.dumps(database)}')
		await asyncio.sleep(24*60*60)

	async def _check5(self):
		database = await self.get_database_of_times()
		for id in list(database.items()):
			for date in id[1]['5']:
				if len(database[id[0]]['5']) > 100 and (await self.database.driver.exists(int(id))):
					await self.api.messages.send(
						user_id=int(id),
						peer_id=int(id),
						random_id=0,
						message='Ты сделал(а) уже более 100 поездок за 5 днейn\n\
Теперь ты учавствуешь в розыгрыше 100 руб. на баланс!'
					)
				if time() - date >= 5*24*60*60:
					database[id[0]]['5'].remove(date)
		await self._write('cache/time_database.toml', f'{tomli.dumps(database)}')
		await asyncio.sleep((24*60*60) + 10)

	async def _check_week(self):
		database = await self.get_database_of_times()
		for id in list(database.items()):
			for date in id[1]['week']:
				if (time() - date >= 7*24*60*60) and (strftime('%A', gmtime()).lower() == 'sunday'):
					database[id[0]]['week'].remove(date)
		await self._write('cache/time_database.toml', f'{tomli.dumps(database)}')
		await asyncio.sleep((24*60*60) + 20)

	async def _check_month(self):
		database = await self.get_database_of_times()
		for id in list(database.items()):
			for date in id[1]['month']:
				if time() - date >= 30*24*60*60:
					database[id[0]]['month'].remove(date)
		await self._write('cache/time_database.toml', f'{tomli.dumps(database)}')
		await asyncio.sleep((24*60*60) + 30)

	async def debug_spec_checker(self):
		database = await self.get_database_of_times()
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
				if (len(database[id]['week']) > 5):
					await self.api.messages.send(
						user_id=int(id),
						peer_id=int(id),
						random_id=0,
						message='Ты сделал(а) уже более 5 поездок за неделю\n\
Теперь ты учавствуешь в розыгрыше 100 руб. на баланс!'
					)
				if (time() - date >= 7*24*60*60):
					database[id[0]]['week'].remove(date)
			for date in id[1]['month']:
				if time() - date >= 30*24*60*60:
					database[id[0]]['month'].remove(date)
		await self._write('cache/time_database.toml', f'{tomli.dumps(database)}')

	async def get_rate(self) -> str:
		return await self._read('cache/rates.txt')

	async def set_rate_file(self, text:str='') -> None:
		await self._write('cache/rates.txt', text)

	def _find(self, promos:list, from_id:int) -> int:
		for promo in promos:
			if from_id in promo:
				i = promos.index(promo)
				break
		else:
			i = -1
		return i

	async def get_from_promo(self, promo:str) -> int:
		db = await self.get_promo_db()
		for rec in db:
			if promo in rec:
				return rec[0]
		return 0

	async def _gen_promo(self) -> str:
		return f'{choice(ascii_uppercase)}{randint(100, 999)}'

	async def get_promo_db(self):
		lines = await self._read('cache/promo.pylist')
		return eval(f'{lines}')

	async def _save_promo(self, new:str, from_id:int) -> None:
		promos = await self.get_promo_db()
		promos.append([from_id, new])
		await self._write('cache/promo.pylist', f'{promos}')

	async def add_new_promo(self, from_id:int) -> int:
		promos = await self.get_promo_db()
		index = self._find(promos, from_id)
		if index != -1:
			return promos[index]
		else:
			new_promo = await self._gen_promo()
			await self._save_promo(new_promo, from_id)
			return [from_id, new_promo]

	async def exists_promo(self, promo:str) -> bool:
		return bool(await self.get_from_promo(promo))

	async def check_aipu(self, from_id:int) -> bool:
		return from_id in (await self.already_insert_promo_users())

	async def already_insert_promo_users(self) -> list:
		lines = await self._read('cache/aipu.pylist')
		return eval(f'{lines}')

	async def add_insert_promo_user(self, new_id:int) -> None:
		aipu = await self.already_insert_promo_users()
		aipu.append(new_id)
		await self._write('cache/aipu.pylist', f'{aipu}')

	async def time(self):
		hours, minutes = list(
			map(
				int,
				strftime(
					'%H:%M',
					gmtime()
				).split(':')
			)
		)
		return f'{hours + 3}:{minutes}'