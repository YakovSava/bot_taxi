import asyncio # Импортируем асинхронность

from sys import platform
from vkbottle.bot import Bot, BotLabeler, Message
from handlers import *
from config import vk_token

try:
	from loguru import logger
except ImportError:
	pass
else:
	logger.disable("vkbottle")

try:
	import logging
except ImportError:
	pass
else:
	logging.getLogger("vkbottle").setLevel(logging.INFO)


label = BotLabeler()
for handlers_labeler in DOWNOLOADER:
	label.load(handlers_labeler)

if platform in ['linux', 'linux2']:
	from multiprocessing import Process
	from vkbottle.callback import BotCallback
	from aiohttp.web import run_app 
	from server import app, data

	pr = Process(target=run_app, args=(app,))
	pr.start()

	vk = Bot(
		token=vk_token,
		labeler=label,
		callback=BotCallback(
			url=data['url'],
			secret_key=data['key'],
			title=data['title']
		)
	)
elif platform in ['win32', 'cygwin', 'msys']:
	try:
		asyncio.set_event_loop(asyncio.WindowsSelectorEventLoopPolicy())
	except:
		pass
	vk = Bot(
		token=vk_token,
		labeler=label
	)

async def preset():
	parameters = await binder.get_parameters()
	group_info = await vk.api.groups.get_by_id(
		group_id=parameters['group_id'],
		fields='city'
	)
	if group_info[0].city is not None:
		await binder.preset(group_info[0].city.title)

null = None # Not debug!

@vk.on.private_message()
async def no_command(message:Message):
	some_state = await vk.state_dispenser.get(message.from_id)
	#print(some_state)
	if some_state is not None:
		await vk.state_dispenser.delete(message.from_id)
	passanger_is_exists = await db.passanger.exists(message.from_id) # проверка на регистрацию... Да, сделать синхронно -  не судьба
	driver_is_exists = await db.driver.exists(message.from_id)
	if passanger_is_exists:
		await message.answer('Неизвестная команда', keyboard = keyboards.choose_service)
	elif driver_is_exists:
		await message.answer('Неизвестная команда', keyboard = keyboards.driver_registartion_success)
	else:
		await message.answer('Пользоваться ботом могут только зарегестрированные пользователи', keyboard=keyboards.start) # А это сообщение если человек не зарегестрирован

if __name__ == '__main__':
	print('Начало работы!')
	loop = asyncio.new_event_loop()
	loop.run_until_complete(
		asyncio.wait([
			loop.create_task(preset()),
			loop.create_task(dispatcher.checker()),
			loop.create_task(vk.run_polling()),
			loop.create_task(forms.cache_cleaner()),
			loop.create_task(dispatcher.date_checker())
		])
	)