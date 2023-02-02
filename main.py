import asyncio # Импортируем асинхронность

from sys import platform
from threading import Thread
from vkbottle.bot import Message
from handlers import *
from plugins.keyboards import keyboards
from server import run_app, Response, routes, app

#try:
#	from loguru import logger
#except ImportError:
#	pass
#else:
#	logger.disable("vkbottle")

try:
	import logging
except ImportError:
	pass
else:
	logging.getLogger("vkbottle").setLevel(logging.INFO)

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

	if platform in ['linux', 'linux2']:
		# confirmation_code, secret_key = loop.run_until_complete(vk.setup_webhook())

		@routes.post('/callback')
		async def callback_api(request):
			try:
				reqdata = await request.json()
			except:
				return Response(status=503)

			if reqdata['type'] == 'confirmation':
				return Response(text=confirmation_code)

			elif reqdata['secret'] == secret_key:
				await vk.Thread_event(reqdata)
			return Response(text='ok')

		runner_list = asyncio.wait([
				loop.create_task(preset()),
				loop.create_task(dispatcher.checker()),
				loop.create_task(vk.run_polling()),
				loop.create_task(dispatcher.cache_cleaner()),
				loop.create_task(dispatcher.date_checker())
			])
	elif platform in ['win32', 'cygwin', 'msys']:
		runner_list = asyncio.wait([
				loop.create_task(preset()),
				loop.create_task(dispatcher.checker()),
				loop.create_task(vk.run_polling()),
				loop.create_task(dispatcher.cache_cleaner()),
				loop.create_task(dispatcher.date_checker())
			])

	app.add_routes(routes)

	pr = Thread(target=run_app, args=(app,), kwargs={'host': '127.0.0.1', 'port': '80', 'loop': loop})
	pr.start()

	loop.run_until_complete(runner_list)
