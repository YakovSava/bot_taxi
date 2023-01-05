import asyncio

from time import time
from aiofiles import open as aiopen
from vkbottle import API
from plugins.database import Database # For annotation
from plugins.timer import Timer # For annotation
from plugins.keyboards import keyboards

class Dispath:

	class DispatchNotGetOneParameterError(SystemError): pass

	def __init__(self,
		timer:Timer=None,
		database:Database=None,
		api:API=None
	):
		if (timer is None) or (database is None) or (api is None):
			raise self.DispatchNotGetOneParameterError(f'The dispatcher did not receive one of the items (something from the following list is "None", however it should not be "None"): \n\
{timer = }\n{database = }\n{api = }')
		self.timer = timer
		self.database = database
		self.api = api

	async def start(self):
		pass

	async def _check_all_datas(self) -> None:
		service_file = await self._get_service_file()
		async for rec in self.database.driver.get_all():
			if (time() - int(rec['last_activity']) >= 30*24*60*60) and (rec['vk'] not in service_file):
				await self.api.messages.send(
					user_id=rec['vk'],
					peer_id=rec['vk'],
					random_id=0,
					message='Привет!\nТы целый месяц не пользовался нашим ботом :( (временный смайлик)\nНажми на кнопку что бы снова начать',
					keyboard=keyboards.month_no_activity_driver
				)
				await asyncio.sleep(1)
		async for rec in self.database.passanger.admin_get_all():
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

	async def _get_service_file(self) -> list:
		async with aiopen('cache/off.pylist', 'r', encoding='utf-8') as list_file:
			lines = await list_file.read()
		return eval(lines)

	async def off_account(self, new_id:int) -> None:
		old_list = await self._get_service_file()
		async with aiopen('cache/off.pylist', 'w', encoding='utf-8') as list_file:
			old_list.append(new_id)
			await list_file.write(f'{old_list}')

	async def get_no_registred_driver(self) -> list:
		async with aiopen('cache/no_registred.pylist', 'r', encoding='utf-8') as file:
			list_lines = await file.read()
		return eval(list_lines)

	async def update_no_registred_driver(self, new_id:int) -> None:
		list_lines = await self.get_no_registred_driver()
		async with aiopen('cache/no_registred.pylist', 'w', encoding='utf-8') as file:
			list_lines.append(new_id)
			await file.write(f'{list_lines}')

	async def check_registred(self, from_id:int) -> bool:
		list_lines = await self.get_no_registred_driver()
		return from_id in list_lines