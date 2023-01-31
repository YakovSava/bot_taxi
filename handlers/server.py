import asyncio

from vkbottle.bot import Bot
from sys import platform
from config import vk_token

if platform in ['linux', 'linux2']:
	from vkbottle.callback import BotCallback

	data = {
		'secret': 'ThisISAVerySecretKey',
		'server': 'http://45.8.230.39/callback',
		'title': 'Test taxi call'
	}

	vk = Bot(
		token=vk_token,
		callback=BotCallback(
			url=data['server'],
			secret_key=data['secret'],
			title=data['title']
		)
	)
	
elif platform in ['win32', 'cygwin', 'msys']:
	try:
		asyncio.set_event_loop(asyncio.WindowsSelectorEventLoopPolicy())
	except:
		pass
	vk = Bot(
		token=vk_token
	)

vk.on.vbml_ignore_case = True