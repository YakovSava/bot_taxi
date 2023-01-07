import asyncio

from time import time
from aiofiles import open as aiopen
from vkbottle import API, AiohttpClient
from aiohttp import ClientSession
from plugins.database import Database # For annotation
from plugins.timer import Timer # For annotation
from plugins.keyboards import keyboards
from config import vk_token

class Dispatch:

	class DispatchNotGetOneParameterError(SystemError): pass

	def __init__(self,
		timer:Timer=None,
		database:Database=None	):
		if (timer is None) or (database is None):
			raise self.DispatchNotGetOneParameterError(f'The dispatcher did not receive one of the items (something from the following list is "None", however it should not be "None"): \n\
{timer = }\n{database = }')
		self.timer = timer
		self.database = database
		self.api = API(vk_token, http_client=AiohttpClient(session=ClientSession(trust_env=True)))
		self.timer.new_async_task(self._check_all_datas)

	async def _check_all_datas(self) -> None:
		service_file = await self.get_service_file()
		async for rec in self.database.driver.get_all_inform():
			try:
				if (time() - int(rec['last_activity']) >= 30*24*60*60) and (rec['vk'] not in service_file):
					await self.api.messages.send(
						user_id=rec['vk'],
						peer_id=rec['vk'],
						random_id=0,
						message='Привет!\nТы целый месяц не пользовался нашим ботом :( (временный смайлик)\nНажми на кнопку что бы снова начать',
						keyboard=keyboards.month_no_activity_driver
					)
					await asyncio.sleep(1)
			except:
				pass
		async for rec in self.database.passanger.admin_get_all():
			try:
				last_message = await self.api.messages.get_history(
					user_id=rec['vk'],
					offset=0,
					count=5
				)
				if (time() - int(last_message.items[0].date) >= 30*24*60*60) and (rec['vk'] not in service_file):
					await self.api.messages.send(
						user_id=rec['vk'],
						peer_id=rec['vk'],
						random_id=0,
						message='Привет!\nТы целый месяц не пользовался нашим ботом :( (временный смайлик)\nНажми на кнопку что бы снова начать',
						keyboard=keyboards.month_no_activity_passanger
					)
					await asyncio.sleep(1)
			except:
				pass

	async def get_service_file(self) -> list:
		async with aiopen('cache/off.pylist', 'r', encoding='utf-8') as list_file:
			lines = await list_file.read()
		return eval(f'{lines}')

	async def off_account(self, new_id:int) -> None:
		old_list = await self.get_service_file()
		async with aiopen('cache/off.pylist', 'w', encoding='utf-8') as list_file:
			old_list.append(new_id)
			await list_file.write(f'{old_list}')

	async def on_account(self, off_id:int) -> None:
		old_list = await self.get_service_file()
		old_list.remove(off_id)
		async with aiopen('cache/off.pylist', 'w', encoding='utf-8') as list_file:
			await list_file.write(f'{old_list}')

	async def get_no_registred_drivers(self) -> list:
		async with aiopen('cache/no_registred.pylist', 'r', encoding='utf-8') as file:
			list_lines = await file.read()
		return eval(f'{list_lines}')

	async def remove_no_registred_drivers(self, registred_id:int) -> None:
		old_list = await self.get_no_registred_drivers()
		try:
			old_list.remove(registred_id)
		except:
			pass
		else:
			async with aiopen('cache/no_registred.pylist', 'w', encoding='utf-8') as file:
				await file.write(f'{old_list}')

	async def update_no_registred_driver(self, new_id:int) -> None:
		list_lines = await self.get_no_registred_drivers()
		async with aiopen('cache/no_registred.pylist', 'w', encoding='utf-8') as file:
			list_lines.append(new_id)
			await file.write(f'{list_lines}')

	async def check_registred(self, from_id:int) -> bool:
		list_lines = await self.get_no_registred_drivers()
		return from_id in list_lines