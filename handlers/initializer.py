from sys import platform
from pyqiwip2p import AioQiwiP2P
from dadata import DadataAsync
from vkbottle.bot import Bot
from plugins.binder import Binder
from plugins.database import Database
from plugins.plotter import Plotter
from plugins.dispatcher import Dispatch
from plugins.timer import Timer
from plugins.forms import Forms
from plugins.csveer import Csveer
from config import *

if platform in ['linux', 'linux2']:
	from multiprocessing import Process
	from vkbottle.callback import BotCallback
	from aiohttp.web import run_app 
	from .server import app, data

	pr = Process(target=run_app, args=(app,))
	pr.start()

	vk = Bot(
		token=vk_token,
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
		token=vk_token
	)

ddt = DadataAsync(ddt_token) # Инициализируем объект сервиса
binder = Binder() # Инициализируем объект связыввателя
db = Database() # Инициализируем базу данных
plot = Plotter() # Инициализируем статиста
forms = Forms(api=vk.api)
qiwi = AioQiwiP2P(auth_key=qiwi_token)
csv = Csveer()
timer = Timer()
dispatcher = Dispatch(
	timer=timer,
	database=db,
	api=vk.api
)