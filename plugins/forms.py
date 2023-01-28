import asyncio

from os.path import exists
from orjson import dumps, loads
from threading import Thread
from random import randint, choice
from string import ascii_letters
from aiofiles import open as aiopen
from vkbottle import API

class Forms:

	def __init__(self, api:API=None):
		self.api = api
		self.all_forms = {}
		if not exists('cache/forms.json'):
			with open('cache/forms.json', 'w', encoding='utf-8') as file:
				file.write('{}')
		loop = asyncio.new_event_loop()
		loop.run_until_complete(self._downoload_forms())

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
		self.all_forms[key] = {'from_id': from_id, 'driver_id': 0, 'active': True, 'in_drive': False}
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

	async def stop_form(self, key:str) -> None:
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
			await self.stop_form(key)

	async def cache_cleaner(self) -> None:
		while True:
			await asyncio.sleep(24*60*60)
			await self._backup()
			await self._delete_all_form()

	def __del__(self):
		asyncio.run(self._backup())