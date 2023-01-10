import asyncio

from aiofiles import open as aiopen
from threading import Thread

class Forms:

	def __init__(self):
		self.all_forms = {}
		loop = asyncio.new_event_loop()
		loop.run_until_complete(self._downoload_forms())

	async def _downoload_forms(self):
		async with aiopen('cache/forms.json', 'r', encoding='utf-8') as form_getter:
			forms = await form_getter.read()
		self.all_forms = eval(f'{forms}')

	async def _backup(self):
		async with aiopen('cache/forms.json', 'w', encoding='utf-8') as backup_file:
			await backup_file.write(f'{self.all_forms}')

	async def new_form(self, from_id:int) -> None:
		self.all_forms[from_id] = {'from_id': from_id, 'driver_id': 0, 'active': True, 'in_drive': False}
		thread = Thread(target=self._form_timer_starter, args=(from_id,))
		thread.start()

	async def start_drive(self, from_id:int, driver_id:int) -> None:
		try:
			self.all_forms[from_id]['active'] = False
			self.all_forms[from_id]['in_drive'] = True
			self.all_forms[from_id]['driver_id'] = driver_id
		except:
			pass

	async def stop_drive(self, from_id:int):
		try:
			self.all_forms[from_id]['active'] = False
			self.all_forms[from_id]['in_drive'] = False
		except:
			pass

	async def stop_form(self, from_id:int) -> None:
		try:
			self.all_forms[from_id]['active'] = False
		except:
			pass

	async def delete_all_form(self) -> None:
		for from_id in list(self.all_forms.keys()):
			if not self.all_forms[from_id]['active'] and not self.all_forms[from_id]['in_drive']:
				del self.all_forms[from_id]

	def get(self, from_id:int) -> dict:
		return self.all_forms[from_id]

	def _form_timer_starter(self, *args) -> None:
		loop = asyncio.new_event_loop()
		loop.run_until_complete(self._form_timer(*args))

	async def _form_timer(self, from_id:int) -> None:
		async def wrapper():
			await asyncio.sleep(10*60)
			await self.stop_form(from_id)
		await asyncio.gather(wrapper())

	async def cache_cleaner(self) -> None:
		await asyncio.sleep(24*60*60)
		await self._delete_all_form()

	def __del__(self):
		asyncio.run(self._backup())