import shutil

print('Импорт и инициализация...')
import asyncio # Импортируем асинхронность
import shutil as shutils

from sys import platform
from os import remove
from os.path import isdir
from importlib import import_module
from rtoml import loads
from vkbottle.bot import Message
from plugins.keyboards import keyboards
from plugins.timer import Timer
from plugins.manager import Manager
from plugins.binder import Binder
from server import run_app, routes, app

print('Препроцессирование...')


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

null = None # Not debug!
timer = Timer()


with open('global_parameters.toml', 'r', encoding='utf-8') as gp:
	global_parameters = loads(gp.read())

all_datas = []
paths = []
for city, button, amount, link, token in global_parameters['citys']:
	if isdir(f'{city}_handlers'):
		shutil.rmtree(f'{city}_handlers')
	shutils.copytree('handlers', f'{city}_handlers')

	with open(f'local_parameters.toml', 'w', encoding='utf-8') as file:
		file.write(f'''qiwi = '{global_parameters['qiwi']}'
dadata = '{global_parameters['dadata']}'
city = '{city}'
token = '{token}'
count = {amount}
buttons = '{button}'
''')

	_temp = import_module(f'{city}_handlers', ('vk','db','binder','dispatcher'))

	datas = {
		'vk': _temp.vk,
		'db': _temp.db,
		'binder': _temp.binder,
		'dispatcher': _temp.dispatcher,
	}

	@datas['vk'].on.private_message()
	async def no_command(message:Message):
		some_state = await datas['vk'].state_dispenser.get(message.from_id)
		if some_state is not None:
			await datas['vk'].state_dispenser.delete(message.from_id)
		passanger_is_exists = await datas['db'].passanger.exists(message.from_id) # проверка на регистрацию... Да, сделать синхронно -  не судьба
		driver_is_exists = await datas['db'].driver.exists(message.from_id)
		if passanger_is_exists:
			await message.answer('Неизвестная команда', keyboard=keyboards.choose_service)
		elif driver_is_exists:
			await message.answer('Неизвестная команда', keyboard=keyboards.driver_registartion_success)
		else:
			await message.answer('Пользоваться ботом могут только зарегестрированные пользователи', keyboard=keyboards.start) # А это сообщение если человек не зарегестрирован
	async def preset():
		parameters = await datas['binder'].get_parameters()
		group_info = await datas['vk'].api.groups.get_by_id(
			group_id=parameters['group_id'],
			fields='city'
		)

		if group_info[0].city is not None:
			await datas['binder'].preset(group_info[0].city.title)

	datas['preset'] = preset()

	all_datas.append(datas)

	paths.append(f'{city}_handlers')

def destroyer():
	for path in paths:
		shutils.rmtree(path)
		remove(path.split('_')[0] + '_parameters.toml')
	remove('local_parameters.toml')

manager = Manager(binders=list(map(lambda cls: cls['binder'], all_datas)), destroy=destroyer)

if __name__ == '__main__':
	print('Запуск...')
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

	tmp_runner_list = [[
			loop.create_task(datas['preset']),
			loop.create_task(datas['dispatcher'].checker()),
			loop.create_task(datas['vk'].run_polling()),
			loop.create_task(datas['dispatcher'].cache_cleaner()),
			loop.create_task(datas['dispatcher'].date_checker())
		] for datas in all_datas]

	runner_list = []
	for raw in tmp_runner_list:
		for i in raw:
			runner_list.append(i)
	runner_list.append(
		loop.create_task(manager.sync_database())
	)

	app.add_routes(routes)
	timer.new_sync_task(run_app, app, host=('45.137.152.231' if platform in ['linux', 'linux2'] else '127.0.0.1'), port=8000, loop=loop)

	loop.run_until_complete(asyncio.wait(runner_list))
