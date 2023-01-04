import asyncio

from aiofiles import open as aiopen
from time import sleep
from threading import Thread

class Forms:

	def __init__(self):
		self.all_forms = {}
		asyncio.run(self._downoload_forms())
		thread = Thread(target=self._reload_starter())
		thread.start()

	async def _downoload_forms(self):
		async with aiopen('cache/forms.json', 'r', encoding='utf-8') as form_getter:
			forms = await form_getter.read()
		self.all_forms = eval(forms)

	async def _backup(self):
		async with aiopen('cache/forms.json', 'w', encoding='utf-8') as backup_file:
			await backup_file.write(f'{self.all_forms}')

	def _reload_starter(self):
		sleep(60)
		some_loop = asyncio.get_running_loop()
		while True:
			some_loop.run_until_complete(self._reload_timer())

	async def new_form(self, from_id:int) -> None:
		self.all_forms[from_id] = {'from_id': from_id, 'driver_id': 0, 'active': True, 'in_driver': False}
		await self._form_timer(from_id)

	async def stop_form(self, from_id:int) -> None:
		self.all_forms[from_id]['active'] = False

	async def driver_stop(self, from_id:int) -> None:
		del self.all_forms[from_id]

	async def _delete_all_form(self) -> None:
		for from_id in list(self.all_forms.keys()):
			if not self.all_forms[from_id]['active']:
				del self.all_forms[from_id]

	def get(self, from_id:int) -> dict:
		return self.all_forms[from_id]

	async def _form_timer(self, from_id:int) -> None:
		async def wrapper():
			await asyncio.sleep(10*60)
			await self.stop_form(from_id)
		await asyncio.gather(wrapper())

	async def _reload_timer(self) -> None:
		await asyncio.sleep(24*60*60)
		await self._delete_all_form()

	def __del__(self):
		asyncio.run(self._backup())