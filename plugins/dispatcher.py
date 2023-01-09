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
		try:
			all_chats = await self.api.messages.get_conversations(
			offset=0,
			count=200,
			filter='all'
			)
			for chat in all_chats.items:
				if (chat.conversation.peer.id not in service_file):
					await self.api.messages.send(
						user_id=chat.conversation.peer.id,
						peer_id=chat.conversation.peer.id,
						random_id=0,
						message='Привет!\nТы целый месяц не пользовался нашим ботом &#128532;\nНажми на кнопку что бы снова начать',
						keyboard=keyboards.month_no_activity
					)
		except:
			pass

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
		return eval(f'{list_lines}')

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