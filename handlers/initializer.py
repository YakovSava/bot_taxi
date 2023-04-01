import asyncio

from sys import platform
from vkbottle.bot import Bot
from pyqiwip2p import AioQiwiP2P
from dadata import DadataAsync
from plugins.binder import Binder
from plugins.database import Database
# from plugins.plotter import Plotter
from plugins.dispatcher import Dispatch
from plugins.timer import Timer
from plugins.csveer import Csveer
from plugins.downoloader import DownoloadC
from config import *

# if platform in ['linux', 'linux2']:
# 	from vkbottle.callback import BotCallback

# 	data = {
# 		'secret': 'ThisISAVerySecretKey',
# 		'server': 'http://45.8.230.39/callback',
# 		'title': 'Test taxi call'
# 	}

# 	vk = Bot(
# 		token=vk_token,
# 		callback=BotCallback(
# 			url=data['server'],
# 			secret_key=data['secret'],
# 			title=data['title']
# 		)
# 	)
# el
if platform in ['win32', 'cygwin', 'msys']:
	try:
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	except:
		pass
		
vk = Bot(
	token=vk_token
)

vk.on.vbml_ignore_case = True

ddt = DadataAsync(ddt_token) # Инициализируем объект сервиса
binder = Binder(parameters_file='nyandoma_parameters.toml') # Инициализируем объект связыввателя
db = Database() # Инициализируем базу данных
# plot = Plotter() # Инициализируем статиста
qiwi = AioQiwiP2P(auth_key=qiwi_token)
csv = Csveer()
timer = Timer()
dispatcher = Dispatch(
	timer=timer,
	database=db,
	api=vk.api
	# CGetter=DownoloadC()
)